"""Builder strategy: omit a transaction declared before replay."""

from __future__ import annotations

from .common import StrategyContext, StrategyResult, validity_for_order


def build_selective_inclusion_strategy(
    context: StrategyContext, excluded_transaction: str
) -> StrategyResult:
    if excluded_transaction not in context.received_set:
        raise ValueError("excluded transaction must be in the received set")
    selected = tuple(name for name in context.canonical_order if name != excluded_transaction)
    checks = validity_for_order(
        StrategyContext(
            context.context_id,
            context.actor_model,
            context.visibility_model,
            tuple(name for name in context.received_set if name != excluded_transaction),
            selected,
            context.seed,
            context.gas_limit,
            context.dependencies,
        ),
        selected,
    )
    checks.update({"declared_omission": True, "liveness_checked": False})
    return StrategyResult(
        strategy_id="builder_selective_inclusion",
        strategy_version="1.0",
        candidate_transactions=tuple(context.received_set),
        selected_order=selected,
        excluded_transactions=(excluded_transaction,),
        search_budget={"max_candidates": 1, "evaluated_candidates": 1, "deterministic": True},
        validity_checks=checks,
        objective_value=None,
        stop_reason="DECLARED_CANDIDATE_OMITTED",
        metadata={
            "omission_reason": "declared_before_replay",
            "liveness_limitation": "not_historical_censorship",
        },
    )
