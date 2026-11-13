# Step 4 Threat Model

## Status and boundary

This threat model is locked for the current Direction 1 study. It describes capabilities used by local or forked replay. It does not claim that any named historical builder, searcher or proposer performed an attack on BSC Mainnet.

Mainnet collection remains read-only. Counterfactual actions are executed only in local or forked environments from pinned mainnet state and receive the evidence label `REPLAYED`.

## Actors

| Actor | Observes | Allowed actions | Explicitly not assumed |
|---|---|---|---|
| `USER` | Confirmed chain state and the user's own application inputs | Submit the user's own transaction | Cannot control block construction or see private builder flow |
| `SEARCHER` | Public state and public order flow available under the scenario | Predict or time an opportunity; change the attacker's own input; submit the attacker's own transaction or bundle | Cannot reorder, remove or rewrite an honest user's transaction; cannot see private flow unless the scenario explicitly grants it |
| `BUILDER` | Pre-state plus transactions or bundles received by the builder | Select a valid transaction set; choose a valid order; insert an attacker-controlled transaction; construct a candidate block bid | Cannot forge signatures; cannot make invalid state valid; cannot rewrite a finalized block; cannot choose arbitrary header fields outside the declared model |
| `PROPOSER` | Candidate builder bids and proposer-local inputs | Select and seal a valid block according to the declared proposer boundary | Not a primary attacker; no majority collusion, censorship coalition or reorg power is modeled |

The builder boundary follows BEP-322 and BNB Chain MEV documentation. The model treats builder access to a transaction or bundle as a scenario precondition. It does not treat the public mempool as the complete BSC order flow.

## Visibility models

### `PUBLIC_ONLY`

The actor can use only public chain state and public order flow that is explicitly available in the scenario. Private builder or validator flow is not visible.

### `BUILDER_RECEIVED`

The builder can use the transactions or bundles received before candidate-block construction. This visibility is conditional. The replay input must record which transactions belong to the builder's received set.

## Capability matrix

| Capability ID | Actor | Visibility | Counterfactual change | Honest transaction rule |
|---|---|---|---|---|
| `SEARCHER_ONLY` | `SEARCHER` | `PUBLIC_ONLY` | Predict or time an attacker-controlled transaction and choose its input | Honest order and inclusion remain unchanged |
| `BUILDER_REORDER` | `BUILDER` | `BUILDER_RECEIVED` | Choose a different valid order for the received transaction set and insert an attacker transaction if declared | All required honest transactions remain included |
| `BUILDER_SELECTIVE_INCLUSION` | `BUILDER` | `BUILDER_RECEIVED` | Reorder and omit a declared candidate transaction from the current block | Omission is recorded and treated as a counterfactual capability, not observed censorship |
| `PROPOSER_DESCRIPTIVE` | `PROPOSER` | `BUILDER_RECEIVED` or declared proposer input | Select a valid candidate block for architecture description only | No proposer attack result is included in the core metrics |

## Core scenario families

The scenario rows are defined in `scenario_catalog.csv`.

1. Searcher prediction or timing.
2. Builder reorder with the same valid transaction set.
3. Builder reorder plus selective inclusion of a declared candidate.
4. Safe-reference comparison under the same workload and each relevant capability.

The safe-reference family is expanded into separate rows so every executable scenario has one actor model and one visibility model.

## Attacker goal and success boundary

The attacker goal is an outcome change defined by the workload, such as a favorable payoff outcome or an increase in `p_win`. A scenario is successful only if the execution is valid, the declared capability was respected, and the outcome decoder records the intended change.

An outcome that is possible in replay is not evidence that the outcome occurred on mainnet. Economic success additionally requires the named cost model and the recorded `net_profit` formula.

## Out of scope

- Multi-block reorg and finality attacks.
- Majority collusion or consensus attacks.
- Proposer or validator as the primary attacker.
- Generic arbitrage, sandwiching or unrelated DeFi MEV.
- Searcher access to private transaction flow.
- Arbitrary timestamp, gas-limit or other header manipulation.
- Forged user signatures or invalid transaction execution.
- Historical builder attribution from block contents alone.

## Evidence labels

- `OBSERVED`: source block, transaction, receipt, trace or official source response.
- `REPLAYED`: local or forked execution under this threat model.
- `MODELED`: declared cost, visibility or sensitivity assumption.
- `DERIVED`: calculated value whose formula and inputs are recorded.
