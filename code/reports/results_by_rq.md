# Step 11 results by research question

All numbers below are derived from controlled local replay. They do not show that a historical BSC actor performed an attack.

## RQ-C1: Capability boundary

| family_id | capability | valid_pairs | validity_rate | canonical_win_rate | manipulated_win_rate | delta_p_win | ci_95_low | ci_95_high | winner_change_rate | liveness_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DICE2WIN_COMMIT_BLOCKHASH | BUILDER_REORDER | 100 | 1.000 | 0.510 | 0.510 | 0.000 | 0.000 | 0.000 | 0.000 | NOT_APPLICABLE |
| DICE2WIN_COMMIT_BLOCKHASH | BUILDER_SELECTIVE_INCLUSION | 100 | 1.000 | 0.510 | 0.510 | 0.000 | 0.000 | 0.000 | 0.000 | NOT_CHECKED |
| DICE2WIN_COMMIT_BLOCKHASH | SEARCHER_ONLY | 100 | 1.000 | 0.510 | 0.510 | 0.000 | 0.000 | 0.000 | 0.000 | NOT_APPLICABLE |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | 100 | 1.000 | 0.460 | 0.540 | 0.080 | -0.120 | 0.280 | 1.000 | NOT_APPLICABLE |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | 100 | 1.000 | 0.460 | 0.540 | 0.080 | -0.120 | 0.280 | 1.000 | NOT_CHECKED |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | SEARCHER_ONLY | 100 | 1.000 | 0.460 | 0.460 | 0.000 | 0.000 | 0.000 | 0.000 | NOT_APPLICABLE |

Searcher-only did not change the decoded winner in either public-informed rule. Builder reorder and declared selective inclusion changed the winner in every Fomo3D-inspired pair, but the changes were not always favorable to the attacker. Selective inclusion remains a capability test because liveness was not measured.

## RQ-C2: Paired effect

The Fomo3D-inspired point estimate is `delta_p_win = +0.080` for builder reorder and selective inclusion. Its paired bootstrap 95% interval includes zero, so this batch does not establish a stable positive advantage. The Dice2Win-inspired abstraction has `delta_p_win = 0.000` for all capabilities.

## RQ-C3: Economic sensitivity

| family_id | capability | cost_model_id | delta_p_win | mean_total_cost_wei | break_even_prize_bnb | cost_evidence |
| --- | --- | --- | --- | --- | --- | --- |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | FEE_ONLY | 0.080 | 58220900000000 | 0.000728 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | OPPORTUNITY_BASE | 0.080 | 174662700000000 | 0.002183 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | OPPORTUNITY_HIGH | 0.080 | 291104500000000 | 0.003639 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | OPPORTUNITY_LOW | 0.080 | 116441800000000 | 0.001456 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | FEE_ONLY | 0.080 | 58220900000000 | 0.000728 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | OPPORTUNITY_BASE | 0.080 | 174662700000000 | 0.002183 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | OPPORTUNITY_HIGH | 0.080 | 291104500000000 | 0.003639 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | OPPORTUNITY_LOW | 0.080 | 116441800000000 | 0.001456 | REPLAYED_FEE_PLUS_MODELED_BID_AND_OPPORTUNITY |

These break-even values use a point estimate and named cost assumptions. Transaction fees are replayed; bid and opportunity-cost fields are modeled. Because the probability interval includes zero, the table is sensitivity analysis rather than evidence of historical profitability. Capabilities with non-positive `delta_p_win` have no finite positive break-even prize under the declared formula.

## RQ-C4: Safe reference

| capability | paired_contexts | weak_delta_p_win | safe_delta_p_win | delta_reduction | ci_95_low | ci_95_high | safe_provenance_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BUILDER_REORDER | 100 | 0.080 | 0.000 | 0.080 | -0.120 | 0.280 | RULE_UNCONFIRMED |
| BUILDER_SELECTIVE_INCLUSION | 100 | 0.080 | 0.000 | 0.080 | -0.120 | 0.280 | RULE_UNCONFIRMED |
| SEARCHER_ONLY | 100 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | RULE_UNCONFIRMED |

The commit-before-entropy abstraction preserved the winner under reorder. Its deployed Dice2Win bytecode linkage remains `RULE_UNCONFIRMED`, and the weak-versus-safe effect interval for builder capabilities includes zero.

## Claim boundary

- C-002 is supported only as a controlled synthetic capability result.
- C-003, C-004 and C-005 are partially supported because uncertainty, modeled costs and provenance limits remain.
- The two-transaction workload does not estimate realistic competition, prevalence or all-block behavior.
