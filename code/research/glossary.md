# Step 2 Glossary

These definitions are normative for the protocol, code, dataset and report.

## Core terms

| Term | Operational definition | Data or code rule |
| --- | --- | --- |
| `weak RNG` | A randomness construction whose relevant output depends on block or transaction context that an in-scope actor can observe, predict or influence under the stated capability model. | Store `rng_pattern` and the source context. Do not label a contract weak only because it contains a block-related opcode. |
| `block context` | The pinned block-level and parent-level inputs used by the replay, including block number, timestamp, parent hash, gas limit and transaction context. | Identify the context with a stable `context_id` and preserve the source block hash. |
| `canonical order` | The historical transaction order in the pinned block context. | `ordering_strategy = CANONICAL`; preserve original transaction indices. |
| `manipulated order` | A valid counterfactual order produced by an allowed searcher or builder strategy. | Store the strategy, permutation or order hash, and validation result. |
| `selective inclusion` | A builder capability that omits a candidate transaction from the current block while retaining a valid block and the stated workload constraints. | Store `selective_inclusion = true`; mark the run as counterfactual. |
| `searcher` | An actor that can observe the public information assigned to the scenario and submit only transactions or bundles controlled by that actor. | A searcher run must not reorder honest transactions or use private-flow information. |
| `builder` | An actor that receives eligible transactions or bundles and constructs a valid candidate block by selecting and ordering them. | A builder run may reorder or selectively include only within the declared capability. |
| `proposer` | The actor that selects or seals a valid block from candidate builder output. | Descriptive architecture role only; not a core attacker model. |
| `exploitability` | The measurable change in outcome or economic value that a capability achieves over the paired canonical baseline. | Report `delta_p_win`, `delta_EV`, `net_profit` and `replay_success`, not a binary source-code label alone. |
| `economic viability` | The condition that the incremental expected payout minus all declared costs is positive under a named cost model. | `economic_viability = net_profit > 0`; record the cost model and evidence labels. |
| `safe reference` | A randomness mechanism evaluated on the same replay context and capability levels as the weak RNG baseline, intended to reduce attacker control of the outcome. | Store the reference ID and compare paired metrics. |
| `commit-before-entropy` | A reference flow in which the commitment is fixed before the later entropy used by the outcome is available. | Replay the commit and reveal phases with pinned inputs; do not treat an arbitrary mock as external randomness. |
| `VRF` | A verifiable random function flow in which a request receives a cryptographically verifiable output from an oracle or provider. | Use only if request, fulfillment, verification and failure behavior are modeled correctly. |

## Replay and result fields

| Field | Definition | Boolean or value rule |
| --- | --- | --- |
| `context_id` | Stable identifier for one pinned historical block context. | Same value must join canonical and all counterfactual runs. |
| `actor_model` | One of `SEARCHER_ONLY`, `BUILDER_REORDER`, `BUILDER_SELECTIVE_INCLUSION`. | Exactly one value per replay row. |
| `visibility_model` | Information available to the actor, such as `PUBLIC_ONLY` or `BUILDER_RECEIVED`. | Must be compatible with `actor_model`. |
| `ordering_strategy` | The order generation method used by the run. | `CANONICAL` is the baseline; every other strategy must be named. |
| `canonical_outcome` | Outcome returned by the historical transaction order under the pinned pre-state. | Store the outcome representation and its evidence label. |
| `manipulated_outcome` | Outcome returned by the counterfactual strategy under the same pinned pre-state. | Store only after transaction and state validity checks pass. |
| `canonical_win` | Whether the attacker-controlled participant wins in the canonical run. | Boolean. `null` if the canonical run is invalid or its outcome cannot be evaluated. |
| `manipulated_win` | Whether the attacker-controlled participant wins in the counterfactual run. | Boolean. `null` if the manipulated run is invalid or its outcome cannot be evaluated. |
| `replay_success` | True only when the run executes against the pinned code and pre-state, all required transactions are valid, the final outcome is decoded, and the stated invariants pass. | Boolean. False requires `failure_reason`; it must not be inferred from `manipulated_win`. |
| `attacker_tx_cost` | Gas cost and any explicitly declared transaction fee paid by the attacker in the modeled run. | Store unit and evidence label. |
| `opportunity_cost` | Modeled value of the builder block-space or alternative-use cost. | `MODELED` unless directly observed and approved. |
| `net_profit` | Incremental expected payout minus declared costs. | `DERIVED`; null when required inputs are unavailable. |
| `safe_reference` | Identifier of the reference mechanism used for the paired comparison. | Use `COMMIT_BEFORE_ENTROPY` or `VRF`; do not leave an unlabeled generic value. |

## Naming rules

- Use `builder` and `proposer` as separate roles.
- Use `replay` for a counterfactual execution, not for a historical attack claim.
- Use `hypothesis` for an unmeasured claim.
- Preserve units for native token, wei, gas and time fields.
- Record nullability and failure reason instead of deleting failed runs.
