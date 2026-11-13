#!/usr/bin/env python3
"""Run the Step 8 strategy matrix on the 100 pinned contexts, sequentially."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from run_fixture import (  # noqa: E402
    ATTACKER_COMMITMENT,
    ATTACKER_SECRET,
    CHAIN_ID,
    COMMIT_SELECTOR,
    HONEST_COMMITMENT,
    HONEST_SECRET,
    PLAY_SELECTOR,
    SAFE_PLAY_SELECTOR,
    LocalRpc,
    branch_state,
    call_reverts,
    call_word,
    deploy,
    pad_address,
    pad_bytes32,
    PARTICIPANT_COUNT_SELECTOR,
    PRIZE_WEI_SELECTOR,
    quantity,
    run_order,
    trace,
    utc_now,
)
from strategies import (  # noqa: E402
    StrategyContext,
    build_reorder_strategy,
    build_searcher_strategy,
    build_selective_inclusion_strategy,
)

SCHEMA_VERSION = "1.0"
SEED = "1"
COST_MODELS = {
    "FEE_ONLY": 0,
    "OPPORTUNITY_LOW": 1,
    "OPPORTUNITY_BASE": 2,
    "OPPORTUNITY_HIGH": 4,
}
SCENARIOS = (
    ("SC-001", "weak", "searcher_only"),
    ("SC-002", "weak", "builder_reorder"),
    ("SC-003", "weak", "builder_selective_inclusion"),
    ("SC-004", "safe", "searcher_only"),
    ("SC-005", "safe", "builder_reorder"),
    ("SC-006", "safe", "builder_selective_inclusion"),
)


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.setdefault(key.strip(), value.strip().strip("'\""))
    return values


def configuration() -> tuple[str, str]:
    file_values = read_env_file(ROOT / ".env")
    api_key = os.environ.get("PINAX_API_KEY") or file_values.get("PINAX_API_KEY")
    if not api_key:
        raise RuntimeError("PINAX_API_KEY is required in the environment or final_project/main_direction/.env")
    base_url = os.environ.get("PINAX_RPC_BASE_URL") or file_values.get(
        "PINAX_RPC_BASE_URL", "https://bsc.rpc.pinax.network"
    )
    return api_key, base_url.rstrip("/")


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def run_id(context_id: str, scenario_id: str, cost_model_id: str, code_commit: str) -> str:
    value = "|".join((SCHEMA_VERSION, context_id, scenario_id, SEED, cost_model_id, code_commit))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def wait_for_anvil(rpc_url: str, process: subprocess.Popen[bytes]) -> LocalRpc:
    rpc = LocalRpc(rpc_url)
    for _ in range(80):
        if process.poll() is not None:
            break
        try:
            if quantity(rpc.call("eth_chainId")) == CHAIN_ID:
                return rpc
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("Anvil did not become ready")


def start_anvil(api_key: str, base_url: str, pre_state_block: int, port: int) -> tuple[subprocess.Popen[bytes], LocalRpc]:
    fork_url = f"{base_url}/v1/{api_key}/"
    command = [
        "anvil",
        "--fork-url",
        fork_url,
        "--fork-block-number",
        str(pre_state_block),
        "--chain-id",
        str(CHAIN_ID),
        "--port",
        str(port),
        "--silent",
    ]
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        return process, wait_for_anvil(f"http://127.0.0.1:{port}", process)
    except Exception:
        process.terminate()
        process.wait(timeout=5)
        raise


def stop_anvil(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def raw_block(context: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / "data" / "pilot_100" / "raw" / "blocks" / f"block_{context['block_number']}.json"
    return json.loads(path.read_text(encoding="utf-8"))["response"]


def transaction_cost(branch: dict[str, Any]) -> int:
    return sum(
        quantity(item["receipt"].get("gasUsed", "0x0"))
        * quantity(item["receipt"].get("effectiveGasPrice", "0x0"))
        for item in branch.get("transactions", [])
        if item["participant"] == "attacker"
    )


def outcome(branch: dict[str, Any] | None) -> dict[str, Any] | None:
    if branch is None:
        return None
    return {
        "winner": branch["post_state"]["winner"],
        "target_index": branch["post_state"]["target_index"],
        "order": branch["order"],
        "transaction_hashes": [item["tx_hash"] for item in branch["transactions"]],
    }


def branch_success(branch: dict[str, Any] | None) -> bool:
    return branch is not None and all(
        item["receipt"].get("status") == "0x1" and item.get("trace") is not None
        for item in branch["transactions"]
    )


def winner_is_attacker(outcome_value: dict[str, Any] | None, attacker_address: str | None) -> bool | None:
    if outcome_value is None or not attacker_address:
        return None
    return outcome_value["winner"].lower() == attacker_address.lower()


def branch_validity(
    branch: dict[str, Any] | None,
    actors: dict[str, str],
    gas_limit: int,
    received_set: tuple[str, ...],
    dependencies: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, bool]:
    dependencies = dependencies or {}
    if branch is None:
        return {key: False for key in (
            "nonce", "dependency", "signature", "gas_limit", "state",
            "same_transaction_set", "snapshot_restore", "evidence_complete",
        )}

    transactions = branch.get("transactions", [])
    order = tuple(branch.get("order", ()))
    nonce_ok = True
    gas_ok = True
    signature_ok = True
    last_nonce: dict[str, int] = {}
    gas_used = 0
    for item in transactions:
        transaction = item.get("transaction") or {}
        participant = item.get("participant")
        sender = str(transaction.get("from", "")).lower()
        expected_sender = actors.get(participant, "").lower()
        signature_ok = signature_ok and bool(expected_sender) and sender == expected_sender
        try:
            nonce = quantity(transaction["nonce"])
            gas = quantity(transaction["gas"])
            used = quantity(item["receipt"].get("gasUsed", "0x0"))
        except (KeyError, TypeError, ValueError):
            nonce_ok = False
            gas_ok = False
            continue
        previous = last_nonce.get(sender)
        nonce_ok = nonce_ok and (previous is None or nonce == previous + 1)
        last_nonce[sender] = nonce
        gas_ok = gas_ok and gas <= gas_limit
        gas_used += used

    dependency_ok = all(
        all(dependency in order[:index] for dependency in dependencies.get(name, ()))
        for index, name in enumerate(order)
    )
    state_ok = branch_success(branch)
    evidence_ok = bool(transactions) and all(
        item.get("receipt") is not None and item.get("trace") is not None
        for item in transactions
    )
    return {
        "nonce": nonce_ok,
        "dependency": dependency_ok,
        "signature": signature_ok,
        "gas_limit": gas_ok and gas_used <= gas_limit,
        "state": state_ok,
        "same_transaction_set": set(order) == set(received_set),
        "snapshot_restore": bool(branch.get("snapshot_restored")),
        "evidence_complete": evidence_ok,
    }


def execution_valid(checks: dict[str, bool]) -> bool:
    return all(checks.get(key, False) for key in (
        "nonce", "dependency", "signature", "gas_limit", "state",
        "snapshot_restore", "evidence_complete",
    ))


def execute_branch(
    rpc: LocalRpc,
    address: str,
    actors: dict[str, str],
    order: list[str],
    selector: str,
    *,
    inputs: dict[str, int] | None = None,
    secrets: dict[str, str] | None = None,
    safe: bool,
) -> dict[str, Any]:
    snapshot = rpc.call("evm_snapshot")
    pre_state = branch_state(rpc, address, safe=safe)
    result: dict[str, Any] | None = None
    try:
        result = run_order(rpc, address, actors, order, selector, secrets=secrets, inputs=inputs)
        result["post_state"] = branch_state(rpc, address, safe=safe)
    finally:
        if not rpc.call("evm_revert", [snapshot]):
            raise RuntimeError("branch snapshot restore failed")
        if result is not None:
            result["snapshot_restored"] = branch_state(rpc, address, safe=safe) == pre_state
    if result is None:
        raise RuntimeError("branch execution returned no result")
    return result


def strategy_context(raw: dict[str, Any], actor_model: str, visibility: str) -> StrategyContext:
    return StrategyContext(
        context_id=f"bsc-mainnet:{raw['block_hash']}",
        actor_model=actor_model,
        visibility_model=visibility,
        received_set=("honest", "attacker"),
        canonical_order=("honest", "attacker"),
        seed=1,
        gas_limit=quantity(raw["gasLimit"]),
    )


def strategy_for(name: str, context: StrategyContext, target_index: int):
    if name == "searcher_only":
        return build_searcher_strategy(
            StrategyContext(
                context.context_id,
                "SEARCHER",
                "PUBLIC_ONLY",
                context.received_set,
                context.canonical_order,
                context.seed,
                context.gas_limit,
            ),
            public_target_index=target_index,
        )
    if name == "builder_reorder":
        return build_reorder_strategy(context)
    if name == "builder_selective_inclusion":
        return build_selective_inclusion_strategy(context, "honest")
    raise ValueError(f"unknown strategy: {name}")


def weak_inputs_for(strategy_id: str, target_index: int) -> dict[str, int]:
    if strategy_id == "searcher_only":
        return {"honest": 0, "attacker": target_index}
    return {"honest": 0, "attacker": 0}


def failure_row(
    raw: dict[str, Any], scenario_id: str, family: str, strategy_id: str, cost_model_id: str,
    code_commit: str, failure_reason: str, strategy_result: Any,
) -> dict[str, Any]:
    actor_model = "SEARCHER" if strategy_id == "searcher_only" else "BUILDER"
    visibility = "PUBLIC_ONLY" if actor_model == "SEARCHER" else "BUILDER_RECEIVED"
    selective = strategy_id == "builder_selective_inclusion"
    capability = {
        "searcher_only": "SEARCHER_ONLY",
        "builder_reorder": "BUILDER_REORDER",
        "builder_selective_inclusion": "BUILDER_SELECTIVE_INCLUSION",
    }[strategy_id]
    return make_observation(
        raw, scenario_id, family, actor_model, visibility, capability,
        strategy_id, strategy_result, None, None, cost_model_id, code_commit, failure_reason,
    )


def make_observation(
    raw: dict[str, Any], scenario_id: str, family: str, actor_model: str, visibility: str,
    capability: str, strategy_id: str, strategy_result: Any, canonical: dict[str, Any] | None,
    manipulated: dict[str, Any] | None, cost_model_id: str, code_commit: str,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    canonical_outcome = outcome(canonical)
    manipulated_outcome = outcome(manipulated)
    actors = raw.get("actors", {})
    canonical_checks = branch_validity(
        canonical, actors, quantity(raw["gasLimit"]), ("honest", "attacker")
    )
    manipulated_checks = branch_validity(
        manipulated, actors, quantity(raw["gasLimit"]), ("honest", "attacker")
    )
    success = failure_reason is None and execution_valid(canonical_checks) and execution_valid(manipulated_checks)
    if not success and not failure_reason:
        failure_reason = "receipt_or_trace_validation_failed"
    attacker_address = actors.get("attacker")
    attacker_tx = None
    if manipulated:
        for item in manipulated["transactions"]:
            if item["participant"] == "attacker":
                attacker_tx = item["tx_hash"]
                attacker_address = attacker_address or manipulated.get("attacker_address")
                break
    fee = transaction_cost(manipulated) if manipulated else None
    multiplier = COST_MODELS[cost_model_id]
    opportunity = None if fee is None else fee * multiplier
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id(f"bsc-mainnet:{raw['block_hash']}", scenario_id, cost_model_id, code_commit),
        "context_id": f"bsc-mainnet:{raw['block_hash']}",
        "scenario_id": scenario_id,
        "seed": SEED,
        "source_rpc_id": raw["source_rpc_id"],
        "chain_id": CHAIN_ID,
        "source_block_number": raw["block_number"],
        "source_block_hash": raw["block_hash"],
        "parent_hash": raw["parent_hash"],
        "pre_state_block": raw["block_number"] - 1,
        "code_commit": code_commit,
        "cost_model_id": cost_model_id,
        "created_at_utc": utc_now(),
        "block_timestamp": quantity(raw["timestamp"]),
        "gas_limit": quantity(raw["gasLimit"]),
        "gas_used_block": quantity(raw["gasUsed"]),
        "tx_count": len(raw["transactions"]),
        "rng_pattern": "WEAK_PUBLIC_CONTEXT" if family == "weak" else "COMMIT_BEFORE_ENTROPY",
        "actor_model": actor_model,
        "visibility_model": visibility,
        "capability": capability,
        "ordering_strategy": {
            "searcher_only": "SEARCHER_TIMING",
            "builder_reorder": "BUILDER_REORDER",
            "builder_selective_inclusion": "BUILDER_SELECTIVE_INCLUSION",
        }[strategy_id],
        "selective_inclusion": strategy_id == "builder_selective_inclusion",
        "strategy_id": strategy_id,
        "attacker_tx": attacker_tx,
        "received_set": ["honest", "attacker"],
        "canonical_order": list(canonical["order"]) if canonical else ["honest", "attacker"],
        "selected_order": list(manipulated["order"]) if manipulated else list(strategy_result.selected_order),
        "excluded_transactions": list(strategy_result.excluded_transactions),
        "validity_checks": {
            **strategy_result.validity_checks,
            **{f"canonical_{key}": value for key, value in canonical_checks.items()},
            **{f"manipulated_{key}": value for key, value in manipulated_checks.items()},
        },
        "canonical_outcome": canonical_outcome,
        "manipulated_outcome": manipulated_outcome,
        "canonical_win": winner_is_attacker(canonical_outcome, attacker_address),
        "manipulated_win": winner_is_attacker(manipulated_outcome, attacker_address),
        "prize_wei": "1000000000000000000",
        "attacker_tx_cost_wei": None if fee is None else str(fee),
        "explicit_bid_or_bribe_wei": "0",
        "opportunity_cost_wei": None if opportunity is None else str(opportunity),
        "net_profit_wei": None,
        "safe_reference": "COMMIT_BEFORE_ENTROPY",
        "safe_reference_outcome": canonical_outcome if family == "safe" else None,
        "safe_reference_checks": raw.get("safe_reference_checks", {
            "commitments_before_entropy": False,
            "entropy_unavailable_before_final_commit": False,
            "commitment_immutability": False,
            "same_participant_set": False,
            "same_payoff_rule": False,
        }),
        "replay_success": success,
        "failure_reason": failure_reason,
        "evidence_label_source_context": "OBSERVED",
        "evidence_label_replay": "REPLAYED",
        "evidence_label_tx_cost": "REPLAYED" if fee is not None else "DERIVED",
        "evidence_label_bid": "MODELED",
        "evidence_label_opportunity_cost": "MODELED",
        "evidence_label_derived": "DERIVED",
    }


def run_context(
    context: dict[str, Any], api_key: str, base_url: str, port: int, code_commit: str,
    observations: list[dict[str, Any]], strategy_traces: list[dict[str, Any]],
    receipts: list[dict[str, Any]], traces: list[dict[str, Any]], failures: list[dict[str, Any]],
) -> bool:
    raw = raw_block(context)
    raw.update(
        {
            "block_number": context["block_number"],
            "block_hash": context["block_hash"],
            "parent_hash": context["parent_hash"],
            "source_rpc_id": context["source_rpc_id"],
        }
    )
    process: subprocess.Popen[bytes] | None = None
    rpc: LocalRpc | None = None
    try:
        process, rpc = start_anvil(api_key, base_url, context["block_number"] - 1, port)
        accounts = rpc.call("eth_accounts")
        if len(accounts) < 2:
            raise RuntimeError("Anvil did not expose two unlocked accounts")
        actors = {"honest": accounts[0], "attacker": accounts[1]}
        raw["actors"] = actors
        weak_args = pad_bytes32(context["block_hash"]) + pad_address(actors["attacker"])
        safe_args = pad_bytes32(context["block_hash"])
        weak_address, _ = deploy(rpc, ROOT, "WeakContextRngGame", weak_args)
        safe_address, _ = deploy(rpc, ROOT, "CommitBeforeEntropyGame", safe_args)
        safe_before_commit = branch_state(rpc, safe_address, safe=True)
        rpc.send(actors["honest"], COMMIT_SELECTOR + pad_bytes32(HONEST_COMMITMENT), safe_address)
        safe_after_first_commit = branch_state(rpc, safe_address, safe=True)
        rpc.send(actors["attacker"], COMMIT_SELECTOR + pad_bytes32(ATTACKER_COMMITMENT), safe_address)
        safe_after_all_commits = branch_state(rpc, safe_address, safe=True)
        raw["safe_reference_checks"] = {
            "commitments_before_entropy": (
                not safe_before_commit["target_finalized"]
                and not safe_after_first_commit["target_finalized"]
                and safe_after_all_commits["target_finalized"]
            ),
            "entropy_unavailable_before_final_commit": not safe_after_first_commit["target_finalized"],
            "commitment_immutability": call_reverts(
                rpc,
                safe_address,
                COMMIT_SELECTOR + pad_bytes32(ATTACKER_COMMITMENT),
                actors["honest"],
            ),
            "same_participant_set": (
                quantity(rpc.call("eth_call", [{"to": weak_address, "data": PARTICIPANT_COUNT_SELECTOR}, "latest"]))
                == quantity(rpc.call("eth_call", [{"to": safe_address, "data": PARTICIPANT_COUNT_SELECTOR}, "latest"]))
            ),
            "same_payoff_rule": (
                quantity(rpc.call("eth_call", [{"to": weak_address, "data": PRIZE_WEI_SELECTOR}, "latest"]))
                == quantity(rpc.call("eth_call", [{"to": safe_address, "data": PRIZE_WEI_SELECTOR}, "latest"]))
            ),
        }
        if not all(raw["safe_reference_checks"].values()):
            raise RuntimeError(f"safe reference checks failed: {raw['safe_reference_checks']}")
        weak_base = branch_state(rpc, weak_address, safe=False)
        target_index = weak_base["target_index"]
        common = strategy_context(raw, "BUILDER", "BUILDER_RECEIVED")
        for scenario_id, family, strategy_id in SCENARIOS:
            address = safe_address if family == "safe" else weak_address
            safe = family == "safe"
            strategy = strategy_for(strategy_id, common, target_index)
            weak_canonical_inputs = {"honest": 0, "attacker": 0}
            weak_manipulated_inputs = weak_inputs_for(strategy_id, target_index)
            secrets = {"honest": HONEST_SECRET, "attacker": ATTACKER_SECRET} if safe else None
            selector = SAFE_PLAY_SELECTOR if safe else PLAY_SELECTOR
            canonical_order = ["honest", "attacker"]
            canonical = execute_branch(
                rpc, address, actors, canonical_order, selector, safe=safe,
                inputs=None if safe else weak_canonical_inputs, secrets=secrets,
            )
            if strategy_id == "builder_reorder":
                selected_order = list(strategy.selected_order)
            elif strategy_id == "builder_selective_inclusion":
                selected_order = list(strategy.selected_order)
            else:
                selected_order = canonical_order
            manipulated = execute_branch(
                rpc, address, actors, selected_order, selector, safe=safe,
                inputs=None if safe else weak_manipulated_inputs, secrets=secrets,
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
                "context_id": common.context_id,
                "scenario_id": scenario_id,
                **strategy.as_dict(),
                "canonical_runtime_validity": canonical_checks,
                "manipulated_runtime_validity": manipulated_checks,
            })
            for branch_name, branch in (("canonical", canonical), ("manipulated", manipulated)):
                for item in branch["transactions"]:
                    receipts.append({"context_id": common.context_id, "scenario_id": scenario_id, "branch": branch_name, "participant": item["participant"], "receipt": item["receipt"]})
                    traces.append({"context_id": common.context_id, "scenario_id": scenario_id, "branch": branch_name, "participant": item["participant"], "trace": item["trace"]})
            for cost_model_id in COST_MODELS:
                observations.append(make_observation(
                    raw, scenario_id, family,
                    "SEARCHER" if strategy_id == "searcher_only" else "BUILDER",
                    "PUBLIC_ONLY" if strategy_id == "searcher_only" else "BUILDER_RECEIVED",
                    {"searcher_only": "SEARCHER_ONLY", "builder_reorder": "BUILDER_REORDER", "builder_selective_inclusion": "BUILDER_SELECTIVE_INCLUSION"}[strategy_id],
                    strategy_id, strategy, canonical, manipulated, cost_model_id, code_commit,
                ))
        return True
    except Exception as error:
        reason = f"{type(error).__name__}:{error}"
        context_id = f"bsc-mainnet:{raw['block_hash']}"
        observations[:] = [row for row in observations if row["context_id"] != context_id]
        strategy_traces[:] = [row for row in strategy_traces if row["context_id"] != context_id]
        receipts[:] = [row for row in receipts if row["context_id"] != context_id]
        traces[:] = [row for row in traces if row["context_id"] != context_id]
        failures.append({"block_number": context["block_number"], "failure_reason": reason})
        for scenario_id, family, strategy_id in SCENARIOS:
            fallback_context = strategy_context(raw, "BUILDER", "BUILDER_RECEIVED")
            strategy = strategy_for(strategy_id, fallback_context, 0)
            for cost_model_id in COST_MODELS:
                observations.append(failure_row(raw, scenario_id, family, strategy_id, cost_model_id, code_commit, reason, strategy))
        return False
    finally:
        if process is not None:
            stop_anvil(process)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "derived" / "pilot")
    parser.add_argument("--port", type=int, default=18546)
    args = parser.parse_args()
    api_key, base_url = configuration()
    code_commit = git_commit()
    contexts = [json.loads(line) for line in (ROOT / "data" / "pilot_100" / "normalized" / "block_contexts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(contexts) != 100:
        raise RuntimeError(f"expected 100 contexts, found {len(contexts)}")
    observations: list[dict[str, Any]] = []
    strategy_traces: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started = time.monotonic()
    successful_contexts = 0
    for index, context in enumerate(contexts, start=1):
        ok = run_context(context, api_key, base_url, args.port, code_commit, observations, strategy_traces, receipts, traces, failures)
        successful_contexts += int(ok)
        print(f"pilot context {index}/100 block={context['block_number']} status={'PASS' if ok else 'FAIL'}", flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("observations.jsonl", observations), ("strategy_traces.jsonl", strategy_traces), ("receipts.jsonl", receipts), ("traces.jsonl", traces)):
        (args.output / name).write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "code_commit": code_commit,
        "sampling_seed": SEED,
        "context_count": len(contexts),
        "block_hashes": [context["block_hash"] for context in contexts],
        "scenario_matrix": [{"scenario_id": s, "family": f, "strategy": strategy} for s, f, strategy in SCENARIOS],
        "cost_models": list(COST_MODELS),
        "successful_contexts": successful_contexts,
        "failed_contexts": len(failures),
        "observation_rows": len(observations),
        "strategy_trace_rows": len(strategy_traces),
        "receipt_rows": len(receipts),
        "trace_rows": len(traces),
        "failure_reasons": failures,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "execution": "sequential local Anvil fork; no mainnet transaction submission",
        "source_rpc_id": "pinax-bsc-rpc",
        "authenticated_url_recorded": False,
    }
    manifest_path = ROOT / "data" / "manifests" / "pilot_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"pilot complete: {successful_contexts}/100 contexts")
    print(f"observations: {args.output / 'observations.jsonl'}")
    return 0 if successful_contexts else 1


if __name__ == "__main__":
    raise SystemExit(main())
