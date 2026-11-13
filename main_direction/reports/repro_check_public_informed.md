# Public-informed synthetic replay report

This report compares controlled synthetic adapters with the `VERY_SIMPLE_RULES` baseline. It is not evidence that a historical attack occurred.

| Rule family | Capability | Paired contexts | Canonical win rate | Manipulated win rate | delta_p_win | Validity rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DICE2WIN_COMMIT_BLOCKHASH | BUILDER_REORDER | 100 | 0.510 | 0.510 | +0.000 | 1.000 |
| DICE2WIN_COMMIT_BLOCKHASH | BUILDER_SELECTIVE_INCLUSION | 100 | 0.510 | 0.510 | +0.000 | 1.000 |
| DICE2WIN_COMMIT_BLOCKHASH | SEARCHER_ONLY | 100 | 0.510 | 0.510 | +0.000 | 1.000 |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_REORDER | 100 | 0.460 | 0.540 | +0.080 | 1.000 |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | BUILDER_SELECTIVE_INCLUSION | 100 | 0.460 | 0.540 | +0.080 | 1.000 |
| FOMO3D_PUBLIC_CONTEXT_HASH_MODULO | SEARCHER_ONLY | 100 | 0.460 | 0.460 | +0.000 | 1.000 |

## Evidence status

- Fomo3D mapping: `CONFIRMED` public-context mechanism.
- Dice2Win mapping: `RULE_UNCONFIRMED` for deployed-bytecode linkage; official source mechanism is recorded.
- PancakeSwap VRF: confirmed catalog reference, not implemented or replayed.

Failed contexts: 0.

Economic profit is not claimed because bid and opportunity cost remain modeled.
