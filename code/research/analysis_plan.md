# Step 5 Analysis Plan

## Analysis status

This plan is locked before the full replay run. It distinguishes confirmatory
metrics specified here from exploratory observations added after the pilot.
No quantitative result is asserted by this document.

## Analysis unit

The primary unit is a paired observation identified by `context_id` and
`scenario_id`. Canonical and counterfactual branches must share the same
context, pre-state, workload and honest inputs. Failed replays are reported
separately and are never recoded as losses or wins.

## Confirmatory questions and outputs

| RQ | Confirmatory comparison | Metrics | Output |
| --- | --- | --- | --- |
| RQ-C1 | Weak RNG pattern by declared actor capability | valid replay rate, failure rate, outcome change | Capability validity table |
| RQ-C2 | Counterfactual strategy versus canonical order | `p_win`, `delta_p_win`, paired outcome difference | Paired comparison table and interval plot |
| RQ-C3 | Incremental payout versus named costs | `expected_payout`, `net_profit_wei`, break-even prize | Cost-model sensitivity table |
| RQ-C4 | Weak RNG versus `COMMIT_BEFORE_ENTROPY` on matched contexts | change in `delta_p_win`, payout and net profit | Safe-reference comparison table |

## Metrics

For each scenario and actor capability:

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

Use integer wei for arithmetic. Convert to display units only in reporting and
record the conversion. A metric is null when its required inputs are missing.

## Uncertainty and paired inference

Report numerator, denominator, valid count and failed count for every binary
metric. Use paired bootstrap resampling of `context_id` within each comparison
group for 95% uncertainty intervals. Resampling keeps all scenario rows for a
context together, preserving the paired design.

For binary outcomes, also report the number of contexts where the manipulated
branch wins, loses or ties relative to canonical. Do not report only a p-value;
include effect size and interval.

If a subgroup has too few valid pairs for a stable interval, report the count,
the instability and the failure breakdown instead of suppressing the subgroup.

## Economic sensitivity

The report must include named cost models:

- observed transaction fee where available;
- explicit bid or bribe when observed or directly declared;
- low, base and high modeled opportunity-cost assumptions.

Modeled values carry `MODELED` labels. Break-even prize is solved from the
declared net-profit formula for each cost model. A prize sweep may illustrate
sensitivity, but it cannot replace missing cost evidence or be presented as an
observed market threshold.

## Missingness and failure analysis

Publish a failure table grouped by `scenario_id`, `context_id`, failure stage
and `failure_reason`. Distinguish source failure, transaction validation
failure, execution failure, outcome decoding failure and invariant failure.

Do not impute a failed replay as `canonical_win=false` or
`manipulated_win=false`. Sensitivity analysis may compare complete cases with
the full failure report, but it must not silently drop failures.

## Exploratory analysis boundary

Post-pilot exploratory plots may inspect gas, transaction count, timestamp or
other observable context features. They must be labeled exploratory, cannot
change the primary sample or hypotheses, and cannot introduce a new claim into
the claims register without evidence.

The analysis does not estimate all-BSC prevalence, identify a historical
attacking builder, or generalize replay outcomes to real attacks.
