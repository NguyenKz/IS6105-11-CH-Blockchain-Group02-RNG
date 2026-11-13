"""Searcher strategy: only choose the attacker's own input/timing."""

from __future__ import annotations

from .common import StrategyContext, StrategyResult, validity_for_order


def build_searcher_strategy(
    context: StrategyContext, attacker: str = "attacker", public_target_index: int = 0
) -> StrategyResult:
    if tuple(context.canonical_order) != tuple(context.received_set):
        raise ValueError("searcher strategy requires canonical order for the received set")
    checks = validity_for_order(context, context.canonical_order)
    checks.update({"honest_order_unchanged": True, "private_flow_used": False})
    return StrategyResult(
        strategy_id="searcher_only",
        strategy_version="1.0",
        candidate_transactions=(attacker,),
        selected_order=context.canonical_order,
        excluded_transactions=(),
        search_budget={"max_candidates": 1, "evaluated_candidates": 1, "deterministic": True},
        validity_checks=checks,
        objective_value=None,
        stop_reason="PUBLIC_INPUT_SELECTED",
        attacker_input=public_target_index,
        metadata={"attacker": attacker, "changed_capability": "attacker_input_or_timing"},
    )
