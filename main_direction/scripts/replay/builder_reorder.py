"""Builder strategy: bounded valid order enumeration."""

from __future__ import annotations

from .common import StrategyContext, StrategyResult, bounded_permutations, validity_for_order


def build_reorder_strategy(context: StrategyContext, limit: int = 32) -> StrategyResult:
    candidates, truncated = bounded_permutations(context, limit)
    if not candidates:
        raise ValueError("no valid builder order")
    alternatives = [candidate for candidate in candidates if candidate != context.canonical_order]
    selected = alternatives[0] if alternatives else context.canonical_order
    alternative_found = bool(alternatives)
    checks = validity_for_order(context, selected)
    checks.update({
        "same_workload": True,
        "alternative_order_found": alternative_found,
        "global_optimum_claimed": False,
    })
    return StrategyResult(
        strategy_id="builder_reorder",
        strategy_version="1.0",
        candidate_transactions=tuple(context.received_set),
        selected_order=selected,
        excluded_transactions=(),
        search_budget={
            "max_candidates": limit,
            "evaluated_candidates": len(candidates),
            "deterministic": True,
        },
        validity_checks=checks,
        objective_value=None,
        stop_reason=(
            "SEARCH_BOUNDED_32"
            if truncated
            else "ALTERNATIVE_VALID_ORDER_FOUND"
            if alternative_found
            else "NO_ALTERNATIVE_VALID_ORDER"
        ),
        metadata={
            "alternative_order_found": alternative_found,
            "global_optimum_claimed": False,
        },
    )
