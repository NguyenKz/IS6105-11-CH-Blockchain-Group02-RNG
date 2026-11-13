#!/usr/bin/env python3
"""Run one deterministic replay fixture against a local Anvil endpoint.

This file refuses non-local RPC URLs before sending any transaction. The
remote Pinax endpoint is used only by run_fixture.sh to create the local fork.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CHAIN_ID = 56
SOURCE_BLOCK = 125_053_984
PRE_STATE_BLOCK = SOURCE_BLOCK - 1
PLAY_SELECTOR = "0x6898f82b"
COMMIT_SELECTOR = "0xf14fcbc8"
SAFE_PLAY_SELECTOR = "0xc7a1865b"
WINNER_SELECTOR = "0xdfbf53ae"
TURN_SELECTOR = "0x8b299903"
TARGET_INDEX_SELECTOR = "0x8819a510"
COMMITTED_COUNT_SELECTOR = "0x903ac41d"
PLAY_COUNT_SELECTOR = "0x97614302"
TARGET_FINALIZED_SELECTOR = "0x0e12cb85"
PRIZE_WEI_SELECTOR = "0x009fa800"
PARTICIPANT_COUNT_SELECTOR = "0x2bb79548"

HONEST_SECRET = "0x" + "11" * 32
ATTACKER_SECRET = "0x" + "22" * 32
HONEST_COMMITMENT = "0xb569321de72d0af89c2fb48a484de3fc9343f31600ae1f3e13d633cb48cbf816"
ATTACKER_COMMITMENT = "0xc4bd59e1394781d1c7bf20a2c0b30c2acc9fbdd52dc5e0d76917de4034ebdf59"


class RpcFailure(RuntimeError):
    pass


class LocalRpc:
    def __init__(self, url: str) -> None:
        if not (url.startswith("http://127.0.0.1:") or url.startswith("http://localhost:")):
            raise RpcFailure("replay RPC must be a local Anvil endpoint")
        self.url = url
        self.request_id = 0

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        self.request_id += 1
        payload = json.dumps(
            {"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params or []}
        ).encode("utf-8")
        try:
            request = Request(
                self.url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
            raise RpcFailure(f"{method}: {type(error).__name__}") from error
        if "error" in data:
            raise RpcFailure(f"{method}: {data['error']}")
        return data.get("result")

    def send(self, sender: str, data: str, to: str | None = None) -> dict[str, Any]:
        transaction: dict[str, Any] = {
            "from": sender,
            "data": data,
            "gas": hex(5_000_000),
            "value": "0x0",
        }
        if to is not None:
            transaction["to"] = to
        tx_hash = self.call("eth_sendTransaction", [transaction])
        return self.wait_receipt(tx_hash)

    def wait_receipt(self, tx_hash: str) -> dict[str, Any]:
        for _ in range(150):
            receipt = self.call("eth_getTransactionReceipt", [tx_hash])
            if receipt is not None:
                if receipt.get("status") != "0x1":
                    raise RpcFailure(f"transaction reverted: {tx_hash}")
                return receipt
            time.sleep(0.1)
        raise RpcFailure(f"receipt timeout: {tx_hash}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def quantity(value: str) -> int:
    return int(value, 16)


def pad_bytes32(value: str) -> str:
    clean = value[2:] if value.startswith("0x") else value
    if len(clean) != 64:
        raise ValueError("expected bytes32")
    return clean


def pad_address(value: str) -> str:
    clean = value[2:] if value.startswith("0x") else value
    if len(clean) != 40:
        raise ValueError("expected address")
    return clean.rjust(64, "0")


def artifact_bytecode(root: Path, contract: str) -> str:
    path = root / "replay" / "out" / f"{contract}.sol" / f"{contract}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    bytecode = data["bytecode"]["object"]
    if not bytecode or bytecode == "0x":
        raise RpcFailure(f"empty bytecode: {contract}")
    return bytecode[2:] if bytecode.startswith("0x") else bytecode


def deploy(rpc: LocalRpc, root: Path, contract: str, constructor_args: str) -> tuple[str, dict[str, Any]]:
    accounts = rpc.call("eth_accounts")
    receipt = rpc.send(accounts[0], "0x" + artifact_bytecode(root, contract) + constructor_args)
    address = receipt.get("contractAddress")
    if not address:
        raise RpcFailure(f"deployment did not return an address: {contract}")
    return address, receipt


def trace(rpc: LocalRpc, tx_hash: str) -> Any:
    return rpc.call("debug_traceTransaction", [tx_hash, {"disableStorage": True, "disableMemory": True}])


def call_word(rpc: LocalRpc, address: str, selector: str) -> int:
    result = rpc.call("eth_call", [{"to": address, "data": selector}, "latest"])
    return int(result, 16)


def call_address(rpc: LocalRpc, address: str, selector: str) -> str:
    result = rpc.call("eth_call", [{"to": address, "data": selector}, "latest"])
    return "0x" + result[-40:]


def call_reverts(rpc: LocalRpc, address: str, data: str, sender: str) -> bool:
    try:
        rpc.call("eth_call", [{"from": sender, "to": address, "data": data}, "latest"])
    except RpcFailure:
        return True
    return False


def branch_state(rpc: LocalRpc, address: str, safe: bool) -> dict[str, Any]:
    state = {
        "block_number": quantity(rpc.call("eth_blockNumber")),
        "winner": call_address(rpc, address, WINNER_SELECTOR),
        "target_index": call_word(rpc, address, TARGET_INDEX_SELECTOR),
    }
    if safe:
        state["committed_count"] = call_word(rpc, address, COMMITTED_COUNT_SELECTOR)
        state["play_count"] = call_word(rpc, address, PLAY_COUNT_SELECTOR)
        state["target_finalized"] = bool(call_word(rpc, address, TARGET_FINALIZED_SELECTOR))
    else:
        state["turn"] = call_word(rpc, address, TURN_SELECTOR)
    return state


def run_order(
    rpc: LocalRpc,
    address: str,
    accounts: dict[str, str],
    order: list[str],
    selector: str,
    secrets: dict[str, str] | None = None,
    inputs: dict[str, int] | None = None,
) -> dict[str, Any]:
    transactions = []
    for name in order:
        data = selector
        if secrets is not None:
            data += pad_bytes32(secrets[name])
        if inputs is not None:
            data += f"{inputs[name]:064x}"
        receipt = rpc.send(accounts[name], data, address)
        tx_hash = receipt["transactionHash"]
        transaction = rpc.call("eth_getTransactionByHash", [tx_hash])
        if transaction is None:
            raise RpcFailure(f"transaction not found: {tx_hash}")
        transactions.append(
            {
                "participant": name,
                "tx_hash": tx_hash,
                "transaction": transaction,
                "receipt": receipt,
                "trace": trace(rpc, tx_hash),
            }
        )
    return {"order": order, "transactions": transactions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    context = json.loads(args.context.read_text(encoding="utf-8").splitlines()[0])
    if context["block_number"] != SOURCE_BLOCK:
        raise RpcFailure(f"fixture requires source block {SOURCE_BLOCK}")
    if context["block_number"] - 1 != PRE_STATE_BLOCK:
        raise RpcFailure("unexpected pre-state block")
    raw_block_path = root / "data" / "pilot_100" / "raw" / "blocks" / f"block_{SOURCE_BLOCK}.json"
    raw_block = json.loads(raw_block_path.read_text(encoding="utf-8"))["response"]
    if raw_block["hash"] != context["block_hash"] or raw_block["parentHash"] != context["parent_hash"]:
        raise RpcFailure("raw and normalized source block metadata differ")

    rpc = LocalRpc(args.rpc_url)
    chain_id = quantity(rpc.call("eth_chainId"))
    fork_block = quantity(rpc.call("eth_blockNumber"))
    if chain_id != CHAIN_ID:
        raise RpcFailure(f"unexpected local chain id: {chain_id}")
    if fork_block != PRE_STATE_BLOCK:
        raise RpcFailure(f"unexpected fork block: {fork_block}")

    accounts = rpc.call("eth_accounts")
    if len(accounts) < 2:
        raise RpcFailure("Anvil did not expose two unlocked accounts")
    actors = {"honest": accounts[0], "attacker": accounts[1]}
    block_hash = context["block_hash"]
    constructor_weak = pad_bytes32(block_hash) + pad_address(actors["attacker"])
    constructor_safe = pad_bytes32(block_hash)

    weak_address, weak_deploy = deploy(rpc, root, "WeakContextRngGame", constructor_weak)
    weak_snapshot = rpc.call("evm_snapshot")
    weak_pre_state = branch_state(rpc, weak_address, safe=False)
    target_index = weak_pre_state["target_index"]
    weak_inputs = {"honest": 0, "attacker": target_index}
    weak_canonical = run_order(
        rpc, weak_address, actors, ["honest", "attacker"], PLAY_SELECTOR, inputs=weak_inputs
    )
    weak_canonical["post_state"] = branch_state(rpc, weak_address, safe=False)
    if not rpc.call("evm_revert", [weak_snapshot]):
        raise RpcFailure("weak snapshot restore failed")
    weak_after_revert = branch_state(rpc, weak_address, safe=False)
    weak_counterfactual = run_order(
        rpc, weak_address, actors, ["attacker", "honest"], PLAY_SELECTOR, inputs=weak_inputs
    )
    weak_counterfactual["post_state"] = branch_state(rpc, weak_address, safe=False)

    safe_address, safe_deploy = deploy(rpc, root, "CommitBeforeEntropyGame", constructor_safe)
    safe_before_commit = branch_state(rpc, safe_address, safe=True)
    rpc.send(actors["honest"], COMMIT_SELECTOR + pad_bytes32(HONEST_COMMITMENT), safe_address)
    safe_after_first_commit = branch_state(rpc, safe_address, safe=True)
    rpc.send(actors["attacker"], COMMIT_SELECTOR + pad_bytes32(ATTACKER_COMMITMENT), safe_address)
    safe_after_all_commits = branch_state(rpc, safe_address, safe=True)
    safe_reference_checks = {
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
            call_word(rpc, weak_address, PARTICIPANT_COUNT_SELECTOR)
            == call_word(rpc, safe_address, PARTICIPANT_COUNT_SELECTOR)
        ),
        "same_payoff_rule": (
            call_word(rpc, weak_address, PRIZE_WEI_SELECTOR)
            == call_word(rpc, safe_address, PRIZE_WEI_SELECTOR)
        ),
    }
    if not all(safe_reference_checks.values()):
        raise RpcFailure(f"safe reference checks failed: {safe_reference_checks}")
    safe_snapshot = rpc.call("evm_snapshot")
    safe_pre_state = branch_state(rpc, safe_address, safe=True)
    safe_canonical = run_order(
        rpc,
        safe_address,
        actors,
        ["honest", "attacker"],
        SAFE_PLAY_SELECTOR,
        {"honest": HONEST_SECRET, "attacker": ATTACKER_SECRET},
    )
    safe_canonical["post_state"] = branch_state(rpc, safe_address, safe=True)
    if not rpc.call("evm_revert", [safe_snapshot]):
        raise RpcFailure("safe snapshot restore failed")
    safe_after_revert = branch_state(rpc, safe_address, safe=True)
    safe_counterfactual = run_order(
        rpc,
        safe_address,
        actors,
        ["attacker", "honest"],
        SAFE_PLAY_SELECTOR,
        {"honest": HONEST_SECRET, "attacker": ATTACKER_SECRET},
    )
    safe_counterfactual["post_state"] = branch_state(rpc, safe_address, safe=True)

    output = {
        "schema_version": "1.0",
        "source_rpc_id": context["source_rpc_id"],
        "chain_id": chain_id,
        "source_block_number": context["block_number"],
        "source_block_hash": context["block_hash"],
        "parent_hash": context["parent_hash"],
        "pre_state_block": PRE_STATE_BLOCK,
        "block_timestamp": quantity(raw_block["timestamp"]),
        "gas_limit": quantity(raw_block["gasLimit"]),
        "gas_used_block": quantity(raw_block["gasUsed"]),
        "tx_count": len(raw_block["transactions"]),
        "retrieved_at_utc": utc_now(),
        "fixture": {
            "actors": actors,
            "weak_contract": weak_address,
            "safe_contract": safe_address,
            "weak_deploy_receipt": weak_deploy,
            "safe_deploy_receipt": safe_deploy,
            "weak": {
                "pre_state": weak_pre_state,
                "canonical": weak_canonical,
                "after_revert": weak_after_revert,
                "counterfactual": weak_counterfactual,
            },
            "safe": {
                "before_commit": safe_before_commit,
                "after_first_commit": safe_after_first_commit,
                "after_all_commits": safe_after_all_commits,
                "reference_checks": safe_reference_checks,
                "pre_state": safe_pre_state,
                "canonical": safe_canonical,
                "after_revert": safe_after_revert,
                "counterfactual": safe_counterfactual,
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("fixture replay: PASS")
    print(f"source block: {SOURCE_BLOCK}")
    print("weak and safe branches: PASS")
    print(f"raw output: {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RpcFailure, KeyError) as error:
        print(f"fixture replay: FAIL ({error})")
        raise SystemExit(1)
