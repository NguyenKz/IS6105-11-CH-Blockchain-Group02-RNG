#!/usr/bin/env python3
"""Validate replay observations against the locked Step 5 schema."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


def rows_from(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else [value]


def validate(path: Path, schema_path: Path) -> int:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    rows = rows_from(path)
    keys: set[tuple[str, str, str, str]] = set()
    for row in rows:
        validator.validate(row)
        key = (row["context_id"], row["scenario_id"], row["seed"], row["cost_model_id"])
        if key in keys:
            raise ValidationError(f"duplicate logical key: {key}")
        keys.add(key)
        if row["replay_success"] is False and not row["failure_reason"]:
            raise ValidationError("failed replay has no failure_reason")
    if not rows:
        raise ValidationError("no observation rows")
    return len(rows)


def self_test(schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    fixture = {
        "schema_version": "1.0",
        "run_id": "a" * 64,
        "context_id": "bsc-mainnet:0x" + "1" * 64,
        "scenario_id": "SC-002",
        "seed": "1",
        "source_rpc_id": "local-fixture",
        "chain_id": 56,
        "source_block_number": 125053984,
        "source_block_hash": "0x" + "2" * 64,
        "parent_hash": "0x" + "3" * 64,
        "pre_state_block": 125053983,
        "code_commit": "a" * 40,
        "cost_model_id": "fixture",
        "created_at_utc": "2026-10-01T00:00:00Z",
        "block_timestamp": 1,
        "gas_limit": 1,
        "gas_used_block": 1,
        "tx_count": 1,
        "rng_pattern": "WEAK_PUBLIC_CONTEXT",
        "actor_model": "BUILDER",
        "visibility_model": "BUILDER_RECEIVED",
        "capability": "BUILDER_REORDER",
        "ordering_strategy": "BUILDER_REORDER",
        "selective_inclusion": False,
        "strategy_id": "fixture",
        "attacker_tx": None,
        "received_set": [],
        "canonical_order": [],
        "selected_order": [],
        "excluded_transactions": [],
        "validity_checks": {},
        "canonical_outcome": None,
        "manipulated_outcome": None,
        "canonical_win": None,
        "manipulated_win": None,
        "prize_wei": None,
        "attacker_tx_cost_wei": None,
        "explicit_bid_or_bribe_wei": None,
        "opportunity_cost_wei": None,
        "net_profit_wei": None,
        "safe_reference": "COMMIT_BEFORE_ENTROPY",
        "safe_reference_outcome": None,
        "safe_reference_checks": {
            "commitments_before_entropy": True,
            "entropy_unavailable_before_final_commit": True,
            "commitment_immutability": True,
            "same_participant_set": True,
            "same_payoff_rule": True,
        },
        "replay_success": True,
        "failure_reason": None,
        "evidence_label_source_context": "OBSERVED",
        "evidence_label_replay": "REPLAYED",
        "evidence_label_tx_cost": "REPLAYED",
        "evidence_label_bid": "MODELED",
        "evidence_label_opportunity_cost": "MODELED",
        "evidence_label_derived": "DERIVED",
    }
    validator.validate(fixture)
    negative = copy.deepcopy(fixture)
    negative["net_profit_wei"] = "-1"
    validator.validate(negative)
    invalid = copy.deepcopy(fixture)
    invalid["replay_success"] = False
    try:
        validator.validate(invalid)
    except ValidationError:
        return
    raise AssertionError("schema accepted failed replay without failure_reason")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report: dict[str, Any] = {
        "status": "PASS",
        "schema": str(args.schema),
        "self_test": args.self_test,
    }
    if args.self_test:
        self_test(args.schema)
        print("schema self-test: PASS")
        report["self_test_status"] = "PASS"
    if args.input:
        report["observation_count"] = validate(args.input, args.schema)
        print(f"schema validation: PASS ({args.input})")
        report["input"] = str(args.input)
        report["input_status"] = "PASS"
    if not args.self_test and not args.input:
        parser.error("provide --input or --self-test")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"validation report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
