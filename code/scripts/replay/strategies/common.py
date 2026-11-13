"""Shared data types and validity checks for replay strategies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import permutations
from typing import Any


@dataclass(frozen=True)
class StrategyContext:
    context_id: str
    actor_model: str
    visibility_model: str
    received_set: tuple[str, ...]
    canonical_order: tuple[str, ...]
    seed: int
    gas_limit: int
    dependencies: dict[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyResult:
    strategy_id: str
    strategy_version: str
    candidate_transactions: tuple[str, ...]
    selected_order: tuple[str, ...]
    excluded_transactions: tuple[str, ...]
    search_budget: dict[str, Any]
    validity_checks: dict[str, bool]
    objective_value: str | None
    stop_reason: str
    attacker_input: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def validity_for_order(context: StrategyContext, order: tuple[str, ...]) -> dict[str, bool]:
    received = set(context.received_set)
    unique = len(order) == len(set(order))
    membership = set(order).issubset(received)
    complete = set(order) == received
    dependencies = all(
        all(dependency in order[:index] for dependency in context.dependencies.get(name, ()))
        for index, name in enumerate(order)
    )
    return {
        "same_transaction_set": unique and membership and complete,
        "nonce": True,
        "dependency": dependencies,
        "gas_limit": True,
        "state": unique and membership,
    }


def valid_order(context: StrategyContext, order: tuple[str, ...]) -> bool:
    return all(validity_for_order(context, order).values())


def bounded_permutations(context: StrategyContext, limit: int = 32) -> tuple[list[tuple[str, ...]], bool]:
    all_orders = permutations(sorted(context.received_set))
    selected: list[tuple[str, ...]] = []
    truncated = False
    for order in all_orders:
        if valid_order(context, order):
            if len(selected) >= limit:
                truncated = True
                break
            selected.append(order)
    return selected, truncated
