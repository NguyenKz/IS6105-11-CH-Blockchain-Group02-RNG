# Step 5 Sampling Plan

## Purpose and sampling frame

The study samples BNB Smart Chain mainnet finalized block contexts. Sampling is
defined before replay results are inspected. No block is selected because its
transactions or outcome appear favorable.

The existing feasibility pilot contains 100 consecutive contexts:

```text
chain_id: 56
block range: 125053984–125054083
artifact: data/pilot_100/normalized/block_contexts.jsonl
```

This pilot validates data access and context normalization only. It is not a
prevalence sample and cannot support an exploitability-rate claim.

## Reproducible selection rule

For any full run:

1. Record one finalized source window and its inclusive block bounds before
   looking at replay outcomes.
2. Exclude only technical impossibilities defined in advance, such as a
   missing block response or a broken parent link. Keep the exclusion and
   failure reason in the sampling log.
3. Hash each eligible block hash together with the fixed sampling seed.
4. Sort by that hash and select without replacement.
5. Write the selected block hashes, seed, window, exclusions and code commit to
   the run manifest before replay starts.

The seed is fixed in the manifest and is never derived from an outcome. The
full-run frame must not intentionally overlap the 100-context feasibility
pilot.

## Sample-size rule

The initial full-run minimum is 100 contexts. After the first 100 replayed
contexts, increase the sample only according to this pre-registered rule:

- primary binary metric: paired manipulated-versus-canonical outcome change;
- target: Wilson 95% interval half-width at most `0.05`;
- maximum: 1,000 contexts;
- if the target is not reached at 1,000, report the achieved interval and stop;
- never add contexts because the result is non-significant, inconvenient or
  economically unattractive.

This rule may stop early only at a scheduled checkpoint after a complete batch.
The checkpoint and resulting sample size must be recorded before inspecting
the next batch.

## Pairing and scenario allocation

Every selected context receives the same locked scenario allocation. Weak-RNG
and safe-reference scenarios use matched `context_id` values and the same
workload. Searcher and builder comparisons use the same context set; they do
not receive separately filtered blocks.

Each row is keyed by:

```text
context_id + scenario_id + seed + cost_model_id
```

Multiple cost models reuse the same replay result and must not create a new
sample of contexts.

## Sampling exclusions and failure handling

Allowed pre-replay exclusions are limited to missing or structurally invalid
source contexts. A replay failure is not a sampling exclusion. It remains a
row with `replay_success=false`, `failure_reason`, scenario ID and context ID.

The final sampling manifest must report:

- source window and chain ID;
- sampling seed and selection algorithm;
- selected, excluded and failed context counts;
- exact exclusion/failure reasons;
- pilot overlap check;
- source RPC ID and code commit.

## Interpretation boundary

The pilot and full run estimate behavior of the declared workload and scenario
model. They do not establish all-BSC prevalence, historical builder behavior or
the frequency of real-world attacks.

## Small public-rule extension

The baseline workload is not replaced. To test whether its conclusions depend
on an unrealistically simple rule, screen approximately three public projects
with inspectable reward/winner logic. Record every candidate and its status in
`research/public_rule_catalog.csv`; do not keep only projects that produce a
desired replay effect.

From the evidence, map at most one or two rule families to minimal synthetic
adapters. The adapters reuse the same context selection, workload,
participant-count scenarios, target indices, capability matrix, seed policy,
cost models and paired analysis as the baseline. Only the rule mechanism is
changed. The mapping must identify the public contract/project, code or
bytecode evidence, randomness source, payoff rule and the invariant preserved
by the synthetic abstraction.

An optional real-rule extension may use at most one application. It is eligible
only when the rule can be matched at the exact pre-state and the required
source/bytecode, ABI, event/trace, randomness and payoff evidence are present.
Otherwise it is reported as `unsupported` or `rule_unconfirmed`, not replaced
with a convenient target. Rule prediction from observed contexts is future
work; if ever attempted, discovery and validation contexts must be disjoint.
