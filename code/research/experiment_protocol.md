# Step 5 Experiment Protocol

## Status and purpose

This protocol locks the replay design before any full experiment is run. It
uses the existing 100-context crawl only as a feasibility pilot. It does not
add empirical attack results, prevalence estimates or economic claims.

- Chain: BNB Smart Chain mainnet, chain ID `56`.
- Source contexts: finalized blocks only.
- Primary safe reference: `COMMIT_BEFORE_ENTROPY`.
- Execution boundary: local or forked replay only; no mainnet writes.
- Evidence labels: `OBSERVED`, `REPLAYED`, `MODELED`, `DERIVED`.

## Unit of analysis

One observation is a scenario execution over one pinned block context and one
cost model:

```text
observation = context + rng pattern + actor capability + strategy + cost model
```

Canonical and counterfactual executions are paired by the same `context_id`.
They must use the same chain ID, source block, parent block, pre-state,
contract code, storage, honest inputs and workload. Only the declared
capability under test may change.

The stable logical key is:

```text
(context_id, scenario_id, seed, cost_model_id)
```

`run_id` is the SHA-256 hex digest of the UTF-8 string:

```text
schema_version|context_id|scenario_id|seed|cost_model_id|code_commit
```

## Locked RNG patterns

The replay harness must implement only these patterns in the initial run:

| ID | Construction under test | Allowed influence | Related scenario |
| --- | --- | --- | --- |
| `WEAK_PUBLIC_CONTEXT` | Outcome derives from public block or transaction context visible before the actor's decision | Searcher prediction or timing; builder ordering where declared | `SC-001` to `SC-003` |
| `WEAK_ORDER_DEPENDENT` | Outcome changes with transaction sender, position or order | Searcher-owned input or builder order, subject to the scenario capability | Supplementary only after the core fixture is available |
| `WEAK_BUILDER_CONTEXT` | Outcome depends on valid block construction choices such as inclusion or ordering | Builder selection and ordering only | Supplementary only after the core fixture is available |
| `COMMIT_BEFORE_ENTROPY` | Commitment is fixed before the later entropy used by the outcome is available | Same capability interface as the paired weak-RNG scenario | `SC-004` to `SC-006` |

`VRF` is not part of the primary run. It may replace the primary reference
only after request, fulfillment, verification and failure behavior are
implemented without a mock being treated as security evidence.

The initial dataset must not add a pattern merely to increase sample count.
Each added pattern requires a source mapping in the related-work matrix and an
update to this protocol before execution.

## Actor, visibility and capability

| Actor | Visibility | Capability | Permitted change |
| --- | --- | --- | --- |
| `SEARCHER` | `PUBLIC_ONLY` | `SEARCHER_ONLY` | Predict or time the attacker's own transaction or input |
| `BUILDER` | `BUILDER_RECEIVED` | `BUILDER_REORDER` | Reorder the declared valid transaction set and insert the declared attacker transaction |
| `BUILDER` | `BUILDER_RECEIVED` | `BUILDER_SELECTIVE_INCLUSION` | Reorder and omit only the pre-declared candidate transaction |

Searchers cannot reorder honest transactions, censor transactions or inspect
private flow. Builders cannot forge signatures, create invalid state, rewrite a
finalized block or arbitrarily edit header fields. Proposers remain an
architectural role, not a core attacker.

## Scenario lock

The runnable scenario set is the six rows in `research/scenario_catalog.csv`:

- `SC-001`: searcher against weak public-context RNG.
- `SC-002`: builder reorder against weak public-context RNG.
- `SC-003`: builder selective inclusion against weak public-context RNG.
- `SC-004`: searcher against the commit-before-entropy reference.
- `SC-005`: builder reorder against the commit-before-entropy reference.
- `SC-006`: builder selective inclusion against the commit-before-entropy reference.

Every counterfactual must pass nonce, dependency, signature, gas-limit and
state-validity checks. Selective inclusion must record the excluded transaction
and the declared reason. Failed executions remain in the dataset.

## Context and seed rules

For each source block:

- `context_id` is `bsc-mainnet:<source_block_hash>`.
- `pre_state_block` is the state immediately before the source transaction or
  workload, recorded as a block number.
- `source_block_hash`, `parent_hash`, block timestamp, gas fields and observed
  transaction metadata are copied from the `OBSERVED` source artifact.
- `seed` is a decimal unsigned string derived from SHA-256 of
  `context_id|scenario_id`; it is not generated from replay outcomes.

The same seed and context are used for canonical and manipulated branches.
Any branch-specific randomness is derived only from the locked seed and the
declared strategy, never from a post-outcome value.

## Outcome and economic metrics

For valid rows, the analysis uses:

```text
p_win = wins / valid_replays
delta_p_win = p_win_manipulated - p_win_canonical
expected_payout = p_win * prize_wei
incremental_expected_payout = expected_payout_manipulated
                              - expected_payout_canonical
net_profit = incremental_expected_payout
             - attacker_tx_cost_wei
             - explicit_bid_or_bribe_wei
             - opportunity_cost_wei
capability_uplift = metric_builder - metric_searcher
```

All native-token values are integer wei. Any opportunity cost not directly
observed is `MODELED` and must be evaluated under the named sensitivity model.
Metrics are `DERIVED` and are null when required inputs are unavailable.

## Evidence and failure rules

- Block, receipt, trace and source metadata are `OBSERVED`.
- Pinned local/fork execution results are `REPLAYED`.
- Assumed bids, opportunity costs and sensitivity parameters are `MODELED`.
- Formulas and aggregate metrics are `DERIVED`.
- `replay_success=true` requires valid execution, decoded outcome and all
  applicable invariants.
- `replay_success=false` requires a non-empty `failure_reason`; the row is not
  deleted or silently converted into a zero outcome.
- Replay output does not prove that a historical builder, searcher or proposer
  performed an attack.

## RQ-to-output mapping

| RQ | Variables | Primary metrics | Locked output |
| --- | --- | --- | --- |
| RQ-C1 | `rng_pattern`, `actor_model`, `visibility_model`, `replay_success` | Valid replay rate, outcome change, failure reasons | Capability and replay-validity table |
| RQ-C2 | `ordering_strategy`, `selective_inclusion`, paired context | `p_win`, `delta_p_win`, paired outcome difference | Canonical versus counterfactual table and uncertainty plot |
| RQ-C3 | `prize_wei`, cost fields, `cost_model_id` | `net_profit`, break-even prize | Cost-model sensitivity table |
| RQ-C4 | `safe_reference`, matched scenario and context | Change in `delta_p_win`, expected payout and net profit | Weak RNG versus safe-reference comparison |

## Controlled extensions after pre-experiment validation

The existing fixture is the `VERY_SIMPLE_RULES` method-validation baseline. It
remains a valid result for checking paired replay, capability isolation,
validity checks, evidence capture and safe-reference behavior; it is not a
claim about historical attacks.

The only planned main extension is a small public-informed synthetic study:

- Screen approximately three public projects and retain pass, fail and excluded
  candidates in the catalog.
- Use evidence from one or two rule families to create minimal synthetic
  adapters. Each adapter records its public exemplar IDs, mechanism mapping and
  preserved invariant.
- Reuse the baseline workload, context sample, participant counts, target
  indices, capabilities, seeds, cost models and analysis. The rule family is
  the declared change; no scenario may be redesigned after seeing outcomes.
- Store the result in a separate batch from `pilot/` and
  `pre_experiment_validation/`.

Replay against one real application/rule is optional and may be attempted only
if source or bytecode, ABI/calldata, randomness/payoff evidence and a
pre-state replay match are all available. Otherwise record `unsupported` or
`rule_unconfirmed`. Rule inference from one context is not allowed; a future
implementation would separate discovery contexts from independent validation
contexts.

## Run boundary

Step 5 creates only protocol and validation artifacts. It does not crawl more
blocks, run a replay, submit a transaction or claim a positive result. The next
step may build the replay harness against this locked specification.
