# Step 4 Replay Invariants

These invariants apply to every canonical and counterfactual run. A failed invariant produces a machine-readable failure row and does not get silently removed from the dataset.

## Context identity

| ID | Invariant | Automated check |
|---|---|---|
| INV-001 | Canonical and counterfactual runs use the same `context_id`. | Join run rows on `context_id`; reject an unpaired row. |
| INV-002 | Both runs use BSC chain ID `56`, the same source block hash and the same parent block. | Compare recorded context fields before execution. |
| INV-003 | Both runs start from the same `pre_state_block` and pinned state snapshot. | Compare fork block and snapshot state identifier. |
| INV-004 | Contract code, initial storage and workload are identical across the pair. | Compare code hash, storage setup hash and workload hash. |

## Transaction validity

| ID | Invariant | Automated check |
|---|---|---|
| INV-005 | Every transaction has a valid signature or is explicitly marked as an attacker-controlled local transaction. | Validate sender recovery or local test account ownership. |
| INV-006 | Each sender's nonce order remains valid. | Check nonce sequence within the selected transaction order. |
| INV-007 | Transaction dependencies remain valid after reordering. | Check declared dependency edges against selected order. |
| INV-008 | The block does not exceed its declared gas limit. | Sum execution gas and compare with the pinned limit. |
| INV-009 | A transaction that is not declared for selective inclusion is not silently removed. | Compare canonical and counterfactual transaction sets. |

## Capability boundary

| ID | Invariant | Automated check |
|---|---|---|
| INV-010 | `SEARCHER_ONLY` can change only attacker-controlled timing or input. | Compare honest transaction order, inclusion and input hashes. |
| INV-011 | `BUILDER_REORDER` keeps the declared transaction set unless the scenario explicitly permits an attacker insertion. | Compare transaction-hash sets and record insertions. |
| INV-012 | `BUILDER_SELECTIVE_INCLUSION` records every excluded transaction and its reason. | Require `excluded_transactions` and `stop_reason` fields. |
| INV-013 | No scenario changes timestamp or another block-header field unless that capability is explicitly added to the protocol. | Compare header fields and reject undeclared changes. |
| INV-014 | No scenario uses private flow under `PUBLIC_ONLY`. | Validate visibility-tagged inputs before execution. |

## Outcome and evidence

| ID | Invariant | Automated check |
|---|---|---|
| INV-015 | Canonical and counterfactual outcomes are decoded from the same event and storage schema. | Validate event signature, fields and decoder version. |
| INV-016 | Gas and fee values come from the receipt of the corresponding run. | Recalculate from run receipt and recorded price fields. |
| INV-017 | `replay_success` is false when execution or validation fails. | Require a failure reason for every false result. |
| INV-018 | Replay results are labeled `REPLAYED`; observed block fields retain `OBSERVED`. | Validate evidence labels before export. |
| INV-019 | Modeled opportunity cost and unobserved bid values are labeled `MODELED`. | Validate cost-model fields and formulas. |
| INV-020 | A replay outcome is not converted into historical builder attribution. | Reject fields that claim observed attack identity without approved evidence. |

## Required failure fields

Every failed scenario must preserve:

```text
context_id
scenario_id
failure_stage
failure_reason
invariant_id
evidence_label
created_at_utc
```
