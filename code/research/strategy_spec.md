# Step 8 — Strategy specification

## Boundary

The pilot uses a synthetic two-participant contract on a local Anvil fork. The
fork is created from each observed BSC pre-state block, but the deployed game is
not a historical BSC contract. Every result is labelled `REPLAYED`; it cannot
show that a builder historically attacked a real transaction.

The shared interface is implemented by `scripts/replay/strategies/`:

| Strategy | Actor / visibility | Allowed capability | Fixed boundary |
| --- | --- | --- | --- |
| `searcher_only` | `SEARCHER` / `PUBLIC_ONLY` | Attacker's own input or timing | Honest order and inclusion remain unchanged |
| `builder_reorder` | `BUILDER` / `BUILDER_RECEIVED` | Reorder received transactions | Same set, valid order, nonce/dependency and gas checks |
| `builder_selective_inclusion` | `BUILDER` / `BUILDER_RECEIVED` | Omit one declared candidate | Candidate and omission reason are fixed before replay |

`StrategyContext` contains `context_id`, actor and visibility models, received
set, canonical order, seed, gas limit and optional dependencies. A
`StrategyResult` records candidates, selected order, exclusions, budget,
validity checks, objective value and stop reason.

## Determinism

- Searcher input is derived from the public fixture target index, not from a
  post-replay outcome.
- Reorder enumerates sorted valid permutations. It evaluates all permutations
  for the two-transaction fixture and at most 32 candidates for larger input;
  `SEARCH_BOUNDED_32` means no global optimum is claimed.
- Selective inclusion always omits the predeclared `honest` candidate in this
  pilot. It records the liveness limitation and does not call the result
  censorship.
- The safe reference uses the same participants, workload and strategy
  interface. It is not tuned after seeing outcomes.

## Economic fields

Receipt gas cost is observed on the local replay and labelled `REPLAYED`.
Explicit bid/bribe is zero only as a fixture model and labelled `MODELED`.
Opportunity cost has low/base/high modeled sensitivity. A missing cost
evidence field prevents an economic conclusion.

No strategy result is a prevalence, historical-attack, builder-advantage or
economic-viability claim about BSC.
