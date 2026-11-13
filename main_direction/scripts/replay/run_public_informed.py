#!/usr/bin/env python3
"""Run the two public-informed synthetic rule families on pinned BSC contexts."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from run_fixture import (
    ATTACKER_COMMITMENT,
    ATTACKER_SECRET,
    COMMIT_SELECTOR,
    HONEST_COMMITMENT,
    HONEST_SECRET,
    PARTICIPANT_COUNT_SELECTOR,
    PLAY_SELECTOR,
    PRIZE_WEI_SELECTOR,
    SAFE_PLAY_SELECTOR,
    branch_state,
    call_reverts,
    call_word,
    deploy,
    pad_address,
    pad_bytes32,
    quantity,
    run_order,
    trace,
)
from run_pilot import (
    CHAIN_ID,
    COST_MODELS,
    SCENARIOS,
    SEED,
    branch_validity,
    configuration,
    execute_branch,
    execution_valid,
    make_observation,
    raw_block,
    start_anvil,
    stop_anvil,
    strategy_context,
    strategy_for,
    utc_now,
    weak_inputs_for,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DEFAULT = ROOT / "data" / "derived" / "public_informed_synthetic"
MANIFEST_DEFAULT = ROOT / "data" / "manifests" / "public_informed_synthetic_manifest.json"
REPORT_DEFAULT = ROOT / "reports" / "public_informed_synthetic_report.md"
FINALIZE_ENTROPY_SELECTOR = "0x361fb18d"

RULES = {
    "weak": {
        "contract": "Fomo3dInspiredGame",
        "rule_family_id": "FOMO3D_PUBLIC_CONTEXT_HASH_MODULO",
        "rule_mapping_id": "MAP-FOMO3D-PUBLIC-CONTEXT",
        "rule_provenance_status": "CONFIRMED",
    },
    "safe": {
        "contract": "Dice2WinInspiredGame",
        "rule_family_id": "DICE2WIN_COMMIT_BLOCKHASH",
        "rule_mapping_id": "MAP-DICE2WIN-COMMIT-BLOCKHASH",
        "rule_provenance_status": "RULE_UNCONFIRMED",
    },
}


def code_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in (
        Path(__file__),
        ROOT / "replay" / "src" / "Fomo3dInspiredGame.sol",
        ROOT / "replay" / "src" / "Dice2WinInspiredGame.sol",
        ROOT / "scripts" / "replay" / "run_pilot.py",
        ROOT / "research" / "schema" / "bsc_rng_mev_replay.schema.json",
    ):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def protected_output(path: Path) -> bool:
    resolved = path.resolve()
    protected = (
        (ROOT / "data" / "derived" / "pilot").resolve(),
        (ROOT / "data" / "derived" / "pre_experiment_validation").resolve(),
    )
    return any(resolved == item or item in resolved.parents for item in protected)


def public_run_id(
    context_id: str,
    scenario_id: str,
    cost_model_id: str,
    code_version: str,
    rule_family_id: str,
) -> str:
    value = "|".join(("1.0", context_id, scenario_id, SEED, cost_model_id, code_version, rule_family_id))
    return hashlib.sha256(value.encode()).hexdigest()


def annotate_observation(row: dict[str, Any], family: str, code_version: str) -> dict[str, Any]:
    rule = RULES[family]
    row.update({key: rule[key] for key in (
        "rule_family_id", "rule_mapping_id", "rule_provenance_status"
    )})
    row["code_commit"] = code_version
    row["run_id"] = public_run_id(
        row["context_id"],
        row["scenario_id"],
        row["cost_model_id"],
        code_version,
        rule["rule_family_id"],
    )
    return row


def constructor_arguments(raw: dict[str, Any], attacker: str) -> str:
    return "".join((
        pad_bytes32(raw["block_hash"]),
        f"{quantity(raw['timestamp']):064x}",
        f"{quantity(raw['difficulty']):064x}",
        pad_address(raw["miner"]),
        f"{quantity(raw['gasLimit']):064x}",
        f"{raw['block_number']:064x}",
        pad_address(attacker),
    ))


def setup_safe_game(
    rpc: Any,
    address: str,
    actors: dict[str, str],
    block_hash: str,
    weak_address: str,
) -> tuple[dict[str, bool], list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    before = branch_state(rpc, address, safe=True)

    honest_receipt = rpc.send(
        actors["honest"], COMMIT_SELECTOR + pad_bytes32(HONEST_COMMITMENT), address
    )
    evidence.append(setup_evidence(rpc, "honest_commit", "honest", honest_receipt))
    after_first = branch_state(rpc, address, safe=True)
    immutable = call_reverts(
        rpc,
        address,
        COMMIT_SELECTOR + pad_bytes32(ATTACKER_COMMITMENT),
        actors["honest"],
    )

    attacker_receipt = rpc.send(
        actors["attacker"], COMMIT_SELECTOR + pad_bytes32(ATTACKER_COMMITMENT), address
    )
    evidence.append(setup_evidence(rpc, "attacker_commit", "attacker", attacker_receipt))
    after_commits = branch_state(rpc, address, safe=True)

    finalize_receipt = rpc.send(
        actors["honest"], FINALIZE_ENTROPY_SELECTOR + pad_bytes32(block_hash), address
    )
    evidence.append(setup_evidence(rpc, "finalize_entropy", "honest", finalize_receipt))
    after_finalize = branch_state(rpc, address, safe=True)

    checks = {
        "commitments_before_entropy": (
            not before["target_finalized"]
            and not after_first["target_finalized"]
            and not after_commits["target_finalized"]
            and after_finalize["target_finalized"]
        ),
        "entropy_unavailable_before_final_commit": not after_first["target_finalized"],
        "commitment_immutability": immutable,
        "same_participant_set": (
            call_word(rpc, weak_address, PARTICIPANT_COUNT_SELECTOR)
            == call_word(rpc, address, PARTICIPANT_COUNT_SELECTOR)
        ),
        "same_payoff_rule": (
            call_word(rpc, weak_address, PRIZE_WEI_SELECTOR)
            == call_word(rpc, address, PRIZE_WEI_SELECTOR)
        ),
    }
    return checks, evidence


def setup_evidence(
    rpc: Any, action: str, participant: str, receipt: dict[str, Any]
) -> dict[str, Any]:
    tx_hash = receipt["transactionHash"]
    return {
        "action": action,
        "participant": participant,
        "transaction_hash": tx_hash,
        "receipt": receipt,
        "trace": trace(rpc, tx_hash),
        "logs": receipt.get("logs", []),
    }


def record_branch_evidence(
    context_id: str,
    scenario_id: str,
    family: str,
    branch_name: str,
    branch: dict[str, Any],
    receipts: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> None:
    for item in branch["transactions"]:
        identity = {
            "context_id": context_id,
            "scenario_id": scenario_id,
            "rule_family_id": RULES[family]["rule_family_id"],
            "branch": branch_name,
            "participant": item["participant"],
            "transaction_hash": item["tx_hash"],
        }
        receipts.append({**identity, "receipt": item["receipt"]})
        traces.append({**identity, "trace": item["trace"]})
        events.append({**identity, "logs": item["receipt"].get("logs", [])})


def run_context(
    context: dict[str, Any],
    api_key: str,
    base_url: str,
    port: int,
    code_version: str,
    observations: list[dict[str, Any]],
    strategy_traces: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    events: list[dict[str, Any]],
    invariants: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> bool:
    raw = raw_block(context)
    raw.update({
        "block_number": context["block_number"],
        "block_hash": context["block_hash"],
        "parent_hash": context["parent_hash"],
        "source_rpc_id": context["source_rpc_id"],
    })
    process = None
    context_id = f"bsc-mainnet:{context['block_hash']}"
    try:
        process, rpc = start_anvil(api_key, base_url, context["block_number"] - 1, port)
        accounts = rpc.call("eth_accounts")
        if len(accounts) < 2:
            raise RuntimeError("Anvil did not expose two unlocked accounts")
        actors = {"honest": accounts[0], "attacker": accounts[1]}
        raw["actors"] = actors

        weak_address, _ = deploy(
            rpc,
            ROOT,
            RULES["weak"]["contract"],
            constructor_arguments(raw, actors["attacker"]),
        )
        safe_address, _ = deploy(rpc, ROOT, RULES["safe"]["contract"], "")
        safe_checks, setup_items = setup_safe_game(
            rpc, safe_address, actors, context["block_hash"], weak_address
        )
        if not all(safe_checks.values()):
            raise RuntimeError(f"safe reference checks failed: {safe_checks}")
        raw["safe_reference_checks"] = safe_checks
        for item in setup_items:
            identity = {
                "context_id": context_id,
                "scenario_id": "SETUP",
                "rule_family_id": RULES["safe"]["rule_family_id"],
                "branch": "setup",
                "participant": item["participant"],
                "transaction_hash": item["transaction_hash"],
                "action": item["action"],
            }
            receipts.append({**identity, "receipt": item["receipt"]})
            traces.append({**identity, "trace": item["trace"]})
            events.append({**identity, "logs": item["logs"]})

        target_index = branch_state(rpc, weak_address, safe=False)["target_index"]
        common = strategy_context(raw, "BUILDER", "BUILDER_RECEIVED")
        for scenario_id, family, strategy_id in SCENARIOS:
            address = safe_address if family == "safe" else weak_address
            safe = family == "safe"
            strategy = strategy_for(strategy_id, common, target_index)
            canonical_inputs = {"honest": 0, "attacker": 0}
            manipulated_inputs = weak_inputs_for(strategy_id, target_index)
            secrets = {"honest": HONEST_SECRET, "attacker": ATTACKER_SECRET} if safe else None
            selector = SAFE_PLAY_SELECTOR if safe else PLAY_SELECTOR

            canonical = execute_branch(
                rpc,
                address,
                actors,
                ["honest", "attacker"],
                selector,
                safe=safe,
                inputs=None if safe else canonical_inputs,
                secrets=secrets,
            )
            selected_order = (
                list(strategy.selected_order)
                if strategy_id != "searcher_only"
                else ["honest", "attacker"]
            )
            manipulated = execute_branch(
                rpc,
                address,
                actors,
                selected_order,
                selector,
                safe=safe,
                inputs=None if safe else manipulated_inputs,
                secrets=secrets,
            )
            canonical["attacker_address"] = actors["attacker"]
            manipulated["attacker_address"] = actors["attacker"]
            canonical_checks = branch_validity(
                canonical, actors, quantity(raw["gasLimit"]), common.received_set
            )
            manipulated_checks = branch_validity(
                manipulated, actors, quantity(raw["gasLimit"]), common.received_set
            )
            strategy_traces.append({
                "context_id": context_id,
                "scenario_id": scenario_id,
                "rule_family_id": RULES[family]["rule_family_id"],
                "rule_mapping_id": RULES[family]["rule_mapping_id"],
                **strategy.as_dict(),
                "canonical_runtime_validity": canonical_checks,
                "manipulated_runtime_validity": manipulated_checks,
            })
            record_branch_evidence(
                context_id, scenario_id, family, "canonical", canonical, receipts, traces, events
            )
            record_branch_evidence(
                context_id, scenario_id, family, "manipulated", manipulated, receipts, traces, events
            )

            canonical_winner = canonical["post_state"]["winner"]
            manipulated_winner = manipulated["post_state"]["winner"]
            invariants.append({
                "context_id": context_id,
                "scenario_id": scenario_id,
                "rule_family_id": RULES[family]["rule_family_id"],
                "canonical_snapshot_restored": canonical["snapshot_restored"],
                "manipulated_snapshot_restored": manipulated["snapshot_restored"],
                "canonical_valid": execution_valid(canonical_checks),
                "manipulated_valid": execution_valid(manipulated_checks),
                "builder_input_unchanged": strategy_id == "searcher_only" or manipulated_inputs == canonical_inputs,
                "safe_reorder_preserves_winner": (
                    family != "safe"
                    or strategy_id != "builder_reorder"
                    or canonical_winner == manipulated_winner
                ),
            })
            for cost_model_id in COST_MODELS:
                row = make_observation(
                    raw,
                    scenario_id,
                    family,
                    "SEARCHER" if strategy_id == "searcher_only" else "BUILDER",
                    "PUBLIC_ONLY" if strategy_id == "searcher_only" else "BUILDER_RECEIVED",
                    {
                        "searcher_only": "SEARCHER_ONLY",
                        "builder_reorder": "BUILDER_REORDER",
                        "builder_selective_inclusion": "BUILDER_SELECTIVE_INCLUSION",
                    }[strategy_id],
                    strategy_id,
                    strategy,
                    canonical,
                    manipulated,
                    cost_model_id,
                    code_version,
                )
                observations.append(annotate_observation(row, family, code_version))
        return True
    except Exception as error:
        reason = f"{type(error).__name__}:{error}"
        observations[:] = [row for row in observations if row["context_id"] != context_id]
        strategy_traces[:] = [row for row in strategy_traces if row["context_id"] != context_id]
        receipts[:] = [row for row in receipts if row["context_id"] != context_id]
        traces[:] = [row for row in traces if row["context_id"] != context_id]
        events[:] = [row for row in events if row["context_id"] != context_id]
        invariants[:] = [row for row in invariants if row["context_id"] != context_id]
        failures.append({"block_number": context["block_number"], "failure_reason": reason})
        raw.setdefault("actors", {})
        for scenario_id, family, strategy_id in SCENARIOS:
            strategy = strategy_for(
                strategy_id,
                strategy_context(raw, "BUILDER", "BUILDER_RECEIVED"),
                0,
            )
            for cost_model_id in COST_MODELS:
                row = make_observation(
                    raw,
                    scenario_id,
                    family,
                    "SEARCHER" if strategy_id == "searcher_only" else "BUILDER",
                    "PUBLIC_ONLY" if strategy_id == "searcher_only" else "BUILDER_RECEIVED",
                    {
                        "searcher_only": "SEARCHER_ONLY",
                        "builder_reorder": "BUILDER_REORDER",
                        "builder_selective_inclusion": "BUILDER_SELECTIVE_INCLUSION",
                    }[strategy_id],
                    strategy_id,
                    strategy,
                    None,
                    None,
                    cost_model_id,
                    code_version,
                    reason,
                )
                observations.append(annotate_observation(row, family, code_version))
        return False
    finally:
        if process is not None:
            stop_anvil(process)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def run_context_isolated(
    index: int,
    context: dict[str, Any],
    api_key: str,
    base_url: str,
    port: int,
    code_version: str,
) -> tuple[int, bool, dict[str, list[dict[str, Any]]]]:
    result: dict[str, list[dict[str, Any]]] = {
        "observations": [],
        "strategy_traces": [],
        "receipts": [],
        "traces": [],
        "events": [],
        "invariants": [],
        "failures": [],
    }
    ok = run_context(
        context,
        api_key,
        base_url,
        port,
        code_version,
        result["observations"],
        result["strategy_traces"],
        result["receipts"],
        result["traces"],
        result["events"],
        result["invariants"],
        result["failures"],
    )
    return index, ok, result


def write_report(path: Path, rows: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    sampled = [row for row in rows if row["cost_model_id"] == "FEE_ONLY"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in sampled:
        groups.setdefault((row["rule_family_id"], row["capability"]), []).append(row)

    lines = [
        "# Public-informed synthetic replay report",
        "",
        "This report compares controlled synthetic adapters with the `VERY_SIMPLE_RULES` baseline. It is not evidence that a historical attack occurred.",
        "",
        "| Rule family | Capability | Paired contexts | Canonical win rate | Manipulated win rate | delta_p_win | Validity rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in sorted(groups):
        group = groups[key]
        valid = [row for row in group if row["replay_success"]]
        decided = [row for row in valid if row["canonical_win"] is not None and row["manipulated_win"] is not None]
        canonical_rate = sum(bool(row["canonical_win"]) for row in decided) / len(decided) if decided else 0.0
        manipulated_rate = sum(bool(row["manipulated_win"]) for row in decided) / len(decided) if decided else 0.0
        validity_rate = len(valid) / len(group) if group else 0.0
        lines.append(
            f"| {key[0]} | {key[1]} | {len(group)} | {canonical_rate:.3f} | "
            f"{manipulated_rate:.3f} | {manipulated_rate - canonical_rate:+.3f} | {validity_rate:.3f} |"
        )

    lines.extend([
        "",
        "## Evidence status",
        "",
        "- Fomo3D mapping: `CONFIRMED` public-context mechanism.",
        "- Dice2Win mapping: `RULE_UNCONFIRMED` for deployed-bytecode linkage; official source mechanism is recorded.",
        "- PancakeSwap VRF: confirmed catalog reference, not implemented or replayed.",
        "",
        f"Failed contexts: {len(failures)}.",
        "",
        "Economic profit is not claimed because bid and opportunity cost remain modeled.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_DEFAULT)
    parser.add_argument("--report", type=Path, default=REPORT_DEFAULT)
    parser.add_argument("--port", type=int, default=18547)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 100:
        raise ValueError("limit must be between 1 and 100")
    if args.workers < 1 or args.workers > 8:
        raise ValueError("workers must be between 1 and 8")
    if protected_output(args.output):
        raise ValueError("refusing to write into pilot or pre_experiment_validation")

    api_key, base_url = configuration()
    code_version = code_fingerprint()
    context_path = ROOT / "data" / "pilot_100" / "normalized" / "block_contexts.jsonl"
    contexts = [
        json.loads(line)
        for line in context_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.limit]

    observations: list[dict[str, Any]] = []
    strategy_traces: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    invariants: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started = time.monotonic()
    successful_contexts = 0
    completed: dict[int, tuple[bool, dict[str, list[dict[str, Any]]]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                run_context_isolated,
                index,
                context,
                api_key,
                base_url,
                args.port + index,
                code_version,
            ): (index, context)
            for index, context in enumerate(contexts)
        }
        for future in concurrent.futures.as_completed(futures):
            index, context = futures[future]
            result_index, ok, result = future.result()
            completed[result_index] = (ok, result)
            print(
                f"public-informed context {index + 1}/{len(contexts)} "
                f"block={context['block_number']} status={'PASS' if ok else 'FAIL'}",
                flush=True,
            )

    for index in range(len(contexts)):
        ok, result = completed[index]
        successful_contexts += int(ok)
        observations.extend(result["observations"])
        strategy_traces.extend(result["strategy_traces"])
        receipts.extend(result["receipts"])
        traces.extend(result["traces"])
        events.extend(result["events"])
        invariants.extend(result["invariants"])
        failures.extend(result["failures"])

    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (
        ("observations.jsonl", observations),
        ("strategy_traces.jsonl", strategy_traces),
        ("receipts.jsonl", receipts),
        ("traces.jsonl", traces),
        ("events.jsonl", events),
        ("invariants.jsonl", invariants),
    ):
        write_jsonl(args.output / name, rows)

    manifest = {
        "schema_version": "1.0",
        "code_fingerprint": code_version,
        "sampling_seed": SEED,
        "context_count": len(contexts),
        "scenario_execution_count": len(contexts) * len(SCENARIOS),
        "rule_families": [RULES["weak"], RULES["safe"]],
        "cost_models": list(COST_MODELS),
        "successful_contexts": successful_contexts,
        "failed_contexts": len(failures),
        "observation_rows": len(observations),
        "strategy_trace_rows": len(strategy_traces),
        "receipt_rows": len(receipts),
        "trace_rows": len(traces),
        "event_rows": len(events),
        "invariant_rows": len(invariants),
        "failure_reasons": failures,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "execution": f"{args.workers} isolated local Anvil workers; no mainnet transaction submission",
        "source_rpc_id": "pinax-bsc-rpc",
        "authenticated_url_recorded": False,
        "provenance_manifest": "data/public_rule_evidence/manifest.json",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(args.report, observations, failures)
    print(f"public-informed replay: {successful_contexts}/{len(contexts)} contexts")
    print(f"observations: {len(observations)}")
    return 0 if successful_contexts == len(contexts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
