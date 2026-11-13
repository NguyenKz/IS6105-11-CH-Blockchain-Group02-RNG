#!/usr/bin/env python3
"""Pure checks for replay decoding, validity and paired evidence."""

from __future__ import annotations

from run_pilot import branch_validity, make_observation, weak_inputs_for, winner_is_attacker
from strategies import StrategyContext, build_reorder_strategy


ACTORS = {"honest": "0x" + "1" * 40, "attacker": "0x" + "2" * 40}
CHECKS = {
    "commitments_before_entropy": True,
    "entropy_unavailable_before_final_commit": True,
    "commitment_immutability": True,
    "same_participant_set": True,
    "same_payoff_rule": True,
}


def branch(order: list[str], winner: str) -> dict:
    transactions = []
    for nonce, participant in enumerate(order):
        transactions.append({
            "participant": participant,
            "tx_hash": f"0x{participant}{nonce}",
            "transaction": {
                "from": ACTORS[participant],
                "nonce": hex(nonce),
                "gas": hex(100_000),
            },
            "receipt": {
                "status": "0x1",
                "gasUsed": hex(21_000),
                "effectiveGasPrice": hex(1),
            },
            "trace": {"ok": True},
        })
    return {
        "order": order,
        "transactions": transactions,
        "post_state": {"winner": winner, "target_index": 0},
        "snapshot_restored": True,
        "attacker_address": ACTORS["attacker"],
    }


def main() -> None:
    context = StrategyContext(
        context_id="bsc-mainnet:0x" + "1" * 64,
        actor_model="BUILDER",
        visibility_model="BUILDER_RECEIVED",
        received_set=("honest", "attacker"),
        canonical_order=("honest", "attacker"),
        seed=1,
        gas_limit=30_000_000,
    )
    strategy = build_reorder_strategy(context)
    canonical = branch(["honest", "attacker"], ACTORS["honest"])
    manipulated = branch(["attacker", "honest"], ACTORS["attacker"])
    raw = {
        "block_hash": "0x" + "3" * 64,
        "source_rpc_id": "local-test",
        "block_number": 1,
        "parent_hash": "0x" + "4" * 64,
        "timestamp": "0x1",
        "gasLimit": "0x1c9c380",
        "gasUsed": "0x5208",
        "transactions": [],
        "actors": ACTORS,
        "safe_reference_checks": CHECKS,
    }

    assert weak_inputs_for("searcher_only", 1)["attacker"] == 1
    assert weak_inputs_for("builder_reorder", 1)["attacker"] == 0
    assert winner_is_attacker(
        {"winner": ACTORS["attacker"]}, ACTORS["attacker"]
    ) is True
    checks = branch_validity(canonical, ACTORS, 30_000_000, context.received_set)
    assert all(checks.values())

    row = make_observation(
        raw,
        "SC-002",
        "weak",
        "BUILDER",
        "BUILDER_RECEIVED",
        "BUILDER_REORDER",
        "builder_reorder",
        strategy,
        canonical,
        manipulated,
        "FEE_ONLY",
        "a" * 40,
    )
    assert row["canonical_outcome"] is not None
    assert row["manipulated_outcome"] is not None
    assert row["validity_checks"]["canonical_evidence_complete"]
    assert row["validity_checks"]["manipulated_evidence_complete"]
    assert row["canonical_win"] is False
    assert row["manipulated_win"] is True
    assert row["safe_reference_checks"] == CHECKS
    print("replay validation tests: PASS")


if __name__ == "__main__":
    main()
