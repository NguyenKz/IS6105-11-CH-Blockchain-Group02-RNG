# Step 5 Dataset Data Dictionary

The canonical observation is one JSON object validated by
`schema/bsc_rng_mev_replay.schema.json`. A CSV export uses JSON strings for
array and object fields so that the same values remain recoverable.

## Conventions

- `OBSERVED`: copied from an approved chain or source artifact.
- `REPLAYED`: produced by a local or forked execution.
- `MODELED`: declared assumption or sensitivity input.
- `DERIVED`: deterministic calculation from labeled fields.
- Native-token amounts use integer `wei` strings. No floating-point money is
  stored.
- Nullable fields are present with JSON `null`; they are not omitted.
- `failure_reason` is required and non-empty when `replay_success=false`.

## Identity and provenance fields

| Field | Type | Unit | Nullable | Evidence | Definition |
| --- | --- | --- | --- | --- | --- |
| `schema_version` | string | version | no | DERIVED | Dataset schema version, currently `1.0`. |
| `run_id` | string | SHA-256 hex | no | DERIVED | Hash of the locked run identity tuple. |
| `context_id` | string | identifier | no | OBSERVED | `bsc-mainnet:<source_block_hash>`. |
| `scenario_id` | enum string | identifier | no | DERIVED | One of `SC-001` through `SC-006`. |
| `seed` | decimal string | unsigned integer | no | DERIVED | SHA-256-derived deterministic seed. |
| `source_rpc_id` | string | identifier | no | OBSERVED | RPC or approved source label, never a credential. |
| `chain_id` | integer | chain ID | no | OBSERVED | Must equal `56`. |
| `source_block_number` | integer | block | no | OBSERVED | Historical source block. |
| `source_block_hash` | string | 32-byte hash | no | OBSERVED | Hash of the pinned source block. |
| `parent_hash` | string | 32-byte hash | no | OBSERVED | Parent hash of the pinned source block. |
| `pre_state_block` | integer | block | no | OBSERVED | State block used before the replay workload. |
| `code_commit` | string | Git commit | no | OBSERVED | Replay harness revision used for the row. |
| `cost_model_id` | string | identifier | no | MODELED | Named cost model used by the economic calculation. |
| `created_at_utc` | string | RFC 3339 UTC | no | DERIVED | Artifact creation timestamp. |

## Context and scenario fields

| Field | Type | Unit | Nullable | Evidence | Definition |
| --- | --- | --- | --- | --- | --- |
| `block_timestamp` | integer | Unix seconds | no | OBSERVED | Source block timestamp. |
| `gas_limit` | integer | gas | no | OBSERVED | Source block gas limit. |
| `gas_used_block` | integer | gas | no | OBSERVED | Source block gas used. |
| `tx_count` | integer | transactions | no | OBSERVED | Number of source transactions. |
| `rng_pattern` | enum string | identifier | no | DERIVED | Weak pattern or safe-reference construction under test. |
| `actor_model` | enum string | identifier | no | DERIVED | `SEARCHER` or `BUILDER`. |
| `visibility_model` | enum string | identifier | no | DERIVED | `PUBLIC_ONLY` or `BUILDER_RECEIVED`. |
| `capability` | enum string | identifier | no | DERIVED | Capability level used by the scenario. |
| `ordering_strategy` | enum string | identifier | no | DERIVED | Canonical, timing, reorder or selective-inclusion strategy. |
| `selective_inclusion` | boolean | flag | no | DERIVED | Whether the counterfactual may omit the declared candidate. |
| `strategy_id` | string | identifier | no | DERIVED | Stable name for the strategy implementation. |
| `attacker_tx` | string | transaction hash or local ID | yes | OBSERVED/REPLAYED | Attacker-controlled transaction under the scenario. |
| `received_set` | array[string] | transaction IDs | yes | OBSERVED/REPLAYED | Transactions available to the builder. |
| `canonical_order` | array[string] | transaction IDs | yes | OBSERVED | Historical or canonical transaction order. |
| `selected_order` | array[string] | transaction IDs | yes | REPLAYED | Valid order selected by the counterfactual strategy. |
| `excluded_transactions` | array[string] | transaction IDs | yes | REPLAYED | Pre-declared transactions omitted by selective inclusion. |
| `validity_checks` | object | named checks | yes | REPLAYED | Nonce, dependency, signature, gas and state checks. |

## Outcomes and economics

| Field | Type | Unit | Nullable | Evidence | Definition |
| --- | --- | --- | --- | --- | --- |
| `canonical_outcome` | string or object | contract-defined | yes | REPLAYED | Decoded outcome under canonical order. |
| `manipulated_outcome` | string or object | contract-defined | yes | REPLAYED | Decoded counterfactual outcome. |
| `canonical_win` | boolean | flag | yes | DERIVED | Attacker win in canonical execution. |
| `manipulated_win` | boolean | flag | yes | DERIVED | Attacker win in counterfactual execution. |
| `prize_wei` | decimal string | wei | yes | OBSERVED/MODELED | Prize or value-at-risk used in the run. |
| `attacker_tx_cost_wei` | decimal string | wei | yes | OBSERVED/MODELED | Attacker transaction fee. |
| `explicit_bid_or_bribe_wei` | decimal string | wei | yes | OBSERVED/MODELED | Explicit bid or bribe cost, if present. |
| `opportunity_cost_wei` | decimal string | wei | yes | MODELED | Builder block-space or alternative-use cost. |
| `net_profit_wei` | signed decimal string | wei | yes | DERIVED | Incremental expected payout less all declared costs; negative values are valid. |
| `safe_reference` | enum string | identifier | no | DERIVED | `COMMIT_BEFORE_ENTROPY` or deferred `VRF`. |
| `safe_reference_outcome` | string or object | contract-defined | yes | REPLAYED | Paired safe-reference outcome when applicable. |
| `safe_reference_checks` | object | named checks | no | REPLAYED | Evidence that commitment ordering, immutability, participant set and payoff rule satisfy the safe-reference gate. |

## Quality and evidence fields

| Field | Type | Unit | Nullable | Evidence | Definition |
| --- | --- | --- | --- | --- | --- |
| `replay_success` | boolean | flag | no | REPLAYED | True only when execution, decoding and invariants pass. |
| `failure_reason` | string | reason code/text | yes | REPLAYED | Required for failed replay; null for success. |
| `evidence_label_source_context` | enum string | label | no | DERIVED | Evidence label for source context fields. |
| `evidence_label_replay` | enum string | label | no | DERIVED | Evidence label for replay fields. |
| `evidence_label_tx_cost` | enum string | label | no | DERIVED | Label for transaction cost. |
| `evidence_label_bid` | enum string | label | no | DERIVED | Label for bid or bribe. |
| `evidence_label_opportunity_cost` | enum string | label | no | DERIVED | Label for opportunity cost. |
| `evidence_label_derived` | enum string | label | no | DERIVED | Label for calculated metrics. |

## Derived formulas

```text
p_win = wins / valid_replays
delta_p_win = p_win_manipulated - p_win_canonical
expected_payout = p_win * prize_wei
incremental_expected_payout = expected_payout_manipulated
                              - expected_payout_canonical
net_profit_wei = incremental_expected_payout
                 - attacker_tx_cost_wei
                 - explicit_bid_or_bribe_wei
                 - opportunity_cost_wei
```

Aggregate metrics are calculated from valid paired rows only and retain counts
of failed rows and their reasons.
