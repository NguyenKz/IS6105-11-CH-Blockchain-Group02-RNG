# Step 2 Protocol: Scope and Claim Boundaries

## Status

- Scope status: locked for Step 2.
- Primary safe reference for the initial protocol: `commit-before-entropy`.
- Final replay feasibility gate: Step 5.
- Evidence labels: `OBSERVED`, `REPLAYED`, `MODELED`, `DERIVED`.

This document converts `research_detail.md` into a bounded protocol. It does not report experimental results.

## Research object

The study examines weak randomness derived from public block or transaction context in payoff-bearing smart-contract interactions on BNB Smart Chain mainnet.

The experimental unit is a paired replay:

```text
one observation = block context + RNG pattern + actor capability + strategy + cost model
```

Canonical and manipulated executions must share the same `context_id`, chain ID, parent block, pinned pre-state, contract code, honest inputs and workload. Only the capability under test may change.

## Locked scope

### Included

- BNB Smart Chain mainnet finalized block contexts.
- Weak RNG derived from public block or transaction attributes.
- Payoff-bearing outcomes such as a prize, mint allocation or game result.
- User, searcher and builder actor models.
- Searcher prediction or timing, builder reorder, and builder selective inclusion.
- Paired replay against the canonical transaction order.
- Economic analysis using observed fees and explicitly labeled modeled costs.
- One primary safe reference that can run on the same replay harness.

### Excluded from the research core

- Multi-block reorg, majority collusion and consensus attacks.
- Validator or proposer as the primary attacker.
- Generic DeFi arbitrage or sandwich attacks.
- Prevalence scanning across all BSC contracts.
- A gas or latency benchmark across three RNG protocols.
- Selective-abort deposit optimization.
- A new RNG protocol design.
- Treating historical builder attribution as proof that an attack occurred.

## Actor capability matrix

| Actor | Observes | Allowed actions | Explicitly not assumed |
| --- | --- | --- | --- |
| User | Confirmed chain and state | Sends their own transaction | Cannot control block construction |
| Searcher | Public state and public order flow that is visible to the observer | Predicts, chooses timing, submits their own transaction or bundle | Cannot reorder honest transactions, censor transactions or see private flow |
| Builder | Pre-state plus transactions or bundles received by the builder | Selects a valid transaction set, orders it, inserts its own transaction and builds a bid | Cannot forge signatures, create invalid state or rewrite a finalized chain |
| Proposer | Candidate builder bids and local mempool | Selects and seals a valid block | Not an attacker in the core scenarios; no collusion or reorg model |

The builder model follows the role separation described in the BSC builder protocol reference. The study does not assume that a builder can set an arbitrary block timestamp or rewrite other header fields.

## Capability levels

| ID | Capability | Counterfactual change |
| --- | --- | --- |
| `SEARCHER_ONLY` | Predict or time the attack and submit only attacker-controlled transactions | Honest transaction order and inclusion remain unchanged |
| `BUILDER_REORDER` | Reorder a valid transaction set and insert attacker-controlled transactions | Honest transactions remain included; only valid order changes |
| `BUILDER_SELECTIVE_INCLUSION` | Reorder and omit a candidate transaction from the current block | Omission is allowed only as a labeled counterfactual capability |

`BUILDER_SELECTIVE_INCLUSION` is not evidence that a historical builder performed the action. It measures what the capability could achieve under the stated pre-state and workload.

## Research questions and measurable outputs

| RQ | Locked interpretation | Primary metrics | Required evidence |
| --- | --- | --- | --- |
| RQ-C1 | Which weak RNG patterns are predictable or influenceable for each actor capability? | `replay_success`, valid replay rate, outcome change by capability | Threat model plus replay traces |
| RQ-C2 | How much do reorder and selective inclusion change the outcome relative to canonical order? | `p_win`, `delta_p_win`, `EV`, paired outcome difference | Same `context_id` for canonical and manipulated runs |
| RQ-C3 | When does manipulation become economically worthwhile? | `net_profit`, break-even prize, positive-profit scenario rate | Observed fee fields plus labeled modeled costs |
| RQ-C4 | How much does the primary safe reference reduce exploitability? | Difference in `delta_p_win`, `EV`, `net_profit` and replay success | Same contexts, workload and capability levels |

## Evidence rules

Every value in the dataset and report must carry one evidence label.

| Label | Use |
| --- | --- |
| `OBSERVED` | Directly read from BSC blocks, receipts, traces, RPC responses or approved source metadata |
| `REPLAYED` | Produced by executing a pinned context under the replay harness |
| `MODELED` | Assumed parameter or sensitivity value, such as unobserved opportunity cost |
| `DERIVED` | Calculated from labeled fields using a recorded formula |

Replay results describe a possible outcome under a capability model. They do not establish that a named builder, searcher or proposer executed the attack on mainnet.

## Economic definition

The core economic quantity is:

```text
net_profit = incremental_expected_payout
             - attacker_tx_cost
             - explicit_bid_or_bribe
             - opportunity_cost
```

`opportunity_cost` is `MODELED` unless the study has a direct approved observation. The protocol must not substitute block reward for the complete cost of the attack.

## Safe reference decision

The Step 2 primary reference is `commit-before-entropy` because it can be represented as a deterministic contract interaction in the same local replay harness without treating an oracle mock as evidence about VRF security.

Step 5 must verify that the reference preserves the comparison invariants and can be replayed successfully. If it fails that gate, Step 5 may promote VRF to primary and must update `decision_log.md` and `safe_reference_todo.md`.

VRF remains documented as the deferred alternative in `safe_reference_todo.md`. It is not part of a gas or latency benchmark.

## Ethical boundary

- Read-only mainnet data collection is allowed.
- Replay runs use local or forked state only.
- No attack transaction is sent to BSC mainnet.
- Credentials, private endpoints and unauthorized data are not collected or published.
- A concrete live-contract risk is separated into responsible disclosure and is not silently presented as a classroom exploit result.

## Step 2 completion gate

- The four RQs have measurable outputs.
- Actor roles are separate and each scenario has one capability level.
- Included and excluded scope is explicit.
- Evidence labels are used consistently.
- The primary safe reference and fallback decision gate are recorded.
- No empirical result is stated before the replay dataset exists.
