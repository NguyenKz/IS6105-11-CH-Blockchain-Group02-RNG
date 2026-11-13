# Direction 1 progress

Last updated: 2026-10-11

## Current status

Direction 1 remains the only active topic. Step 8–9 remain revalidated, and
Step 10 is complete for the narrow public-informed synthetic supplement. The
Step 11 paired analysis is also complete. The historical pilot,
pre-experiment validation and Step 10 replay artifacts were preserved byte
for byte. [Step 11B](./step_11b_confirmatory_robustness_plan.md) is planned to
add an independent 1,000-context holdout, a small 2/5/10-participant
robustness batch and one real-rule feasibility gate. No Step 11B experiment
has started. Step 12 reporting follows Step 11B or a documented blocker.

## Step status

| Step | Status | Note |
| --- | --- | --- |
| 1–7 | Complete as design/artifacts | Research map, protocol, data, contexts and replay harness exist. |
| 8 | Revalidated | Foundry 4/4 PASS and repaired fixture replay PASS in `data/derived/pre_experiment_validation/`. |
| 9 | Revalidated | New fixture batch is valid; historical 100-context pilot remains unchanged. |
| 10 | Complete | Three public projects cataloged; two synthetic mappings replayed across 100 pinned contexts with 2,400 valid observations. |
| 11 | Complete | Executed notebook, seven analysis tables, five figures and RQ-C1 to RQ-C4 report exist. |
| 11B | Planned, not started | Independent holdout, participant robustness and a bounded real-rule feasibility gate are documented; no crawl or replay has run. |
| 12 | Not started | Write the final report, audit claims and package reproduction instructions after Step 11B or a documented blocker. |

## Pre-experiment gates

| Gate | Code/schema status | Replay status |
| --- | --- | --- |
| 1. Builder alternative order | Python unit test PASS | Foundry/anvil PASS; non-canonical order observed |
| 2. Outcome decoder and capability isolation | Python validation PASS | Fixture PASS; final-winner decoder and input isolation checked |
| 3. Safe-reference lifecycle | Contract and schema checks PASS | Fixture PASS; entropy finalizes after final commitment |
| 4. Runtime validity and paired evidence | Validation code and synthetic test PASS | Fixture PASS; receipts/traces/events and snapshot checks present |
| 5. Signed `net_profit_wei` | Schema self-test accepts negative wei | Schema validation PASS; no pilot profit was filled in |

## Completed in this pass

- `builder_reorder` selects the first valid order different from canonical and
  records `NO_ALTERNATIVE_VALID_ORDER` when no alternative exists.
- Builder reorder and selective inclusion keep canonical weak-RNG inputs;
  searcher-only is the only strategy that changes attacker input.
- Final `winner == attacker` is the payoff decoder for paired outcomes.
- Runtime checks cover nonce, dependency, signature/from, gas, state,
  transaction-set and snapshot restoration.
- Pilot output code records canonical and manipulated receipts, traces and
  events.
- The safe fixture exposes `targetFinalized` and records commitment lifecycle
  checks.
- The schema accepts signed `net_profit_wei` values without changing old
  pilot artifacts.
- Corrected the ABI selectors for the public constant getters used by the
  safe-reference checks; the revalidation batch was then rerun from scratch.
- Stored the new validation artifacts separately under
  `data/derived/pre_experiment_validation/`, including raw runs, observations,
  branch evidence, invariants and validation outputs.

## Checks run

Using `venv/bin/activate`:

- Strategy unit tests: PASS.
- Replay validation tests: PASS.
- Schema self-test: PASS.
- Foundry replay fixture tests: PASS (4/4).
- Anvil fork fixture replay: PASS.
- `collect_result.py`: PASS (2 observations).
- New batch acceptance checks: PASS (order/input isolation, safe-reference,
  snapshot, validity and paired evidence).
- New batch observations, existing fixture observations and the 100-context
  pilot observations: JSON Schema PASS.
- Historical pilot artifacts and manifest: unchanged.
- Public-rule provenance validation: PASS (3 records and 3 mappings).
- Public-informed Foundry tests: PASS (7/7 total fixture tests).
- Public-informed replay: PASS (100/100 contexts; 2,400 observations).
- Public-informed schema and evidence acceptance checks: PASS.
- Step 11 analysis unit tests: PASS (5/5).
- Step 11 notebook execution: PASS (8/8 code cells; no error output).
- Deterministic rerun: PASS; generated tables, figures and reports retained
  identical hashes across two notebook executions.
- `git diff --check`: PASS.

## Revalidation run

Foundry was run from `/Users/nguyenkz/.foundry/bin` and the local fork replay
completed successfully. The new batch is:

```bash
final_project/code/data/derived/pre_experiment_validation/
```

The recorded code baseline for the generated observations is commit
`655564c` (`fix(replay): revalidate fixture gates`). The pilot directory and
pilot manifest were not written.

## Step 10 entry criteria

- Foundry fixture tests pass.
- The repaired fixture rerun passes with both canonical and counterfactual
  evidence.
- Strategy traces show a non-canonical valid order for the two-transaction
  independent fixture.
- Safe-reference checks are all true.
- The revalidation code is committed as `655564c` and recorded in the next
  manifest.
- Sampling window, seed and full-run output paths remain outcome-independent.

The validation-specific criteria above remain met. Step 10 used a separate
batch and did not modify the historical pilot.

## Step 10 result

The current pre-experiment result is retained as the `VERY_SIMPLE_RULES`
method-validation baseline. It is not a failed study and it is not evidence of
a historical attack.

The narrow supplement is complete:

- cataloged Fomo3D Long, Dice2Win v5 and PancakeSwap Lottery v2;
- implemented `FOMO3D_PUBLIC_CONTEXT_HASH_MODULO` and
  `DICE2WIN_COMMIT_BLOCKHASH` as separate synthetic adapters;
- kept PancakeSwap VRF as a confirmed catalog-only reference;
- ran 600 scenario executions across the same 100 pinned BSC contexts;
- produced 2,400 schema-valid observations and 600 invariant rows;
- stored 2,500 receipt, trace and event rows, including safe-rule setup;
- completed with 100/100 successful contexts and no replay failures;
- compared `delta_p_win` with the `VERY_SIMPLE_RULES` baseline.

The output batch and report are:

```text
data/derived/public_informed_synthetic/
data/manifests/public_informed_synthetic_manifest.json
reports/public_informed_synthetic_report.md
```

Fomo3D and PancakeSwap have confirmed runtime/source evidence. Dice2Win's
official source establishes the mechanism, but its historical runtime
bytecode was not independently recovered from the checked RPC, so its strict
provenance status remains `RULE_UNCONFIRMED`.

The strongest public-informed result is limited to the synthetic workload:
builder reorder and declared selective inclusion changed Fomo-inspired
attacker win rate from 0.460 to 0.540 (`delta_p_win = +0.080`), while
searcher-only had no change. All three Dice-inspired capabilities had
`delta_p_win = 0.000`. These are controlled replay results, not evidence of a
historical attack.

Replay on at most one real application/rule is optional and requires complete
evidence plus an exact pre-state replay match. Rule inference from contexts is
future work only; no predictor or discovery/validation split is implemented
in the current project.

## Step 11 result

The executed notebook is `analysis/step_11_results.ipynb`. It uses only the
completed Step 10 batch and the preserved `VERY_SIMPLE_RULES` baseline.
Outcome statistics use one `FEE_ONLY` row per paired scenario so the four cost
models do not duplicate probability observations. Economic sensitivity uses
all four named cost models.

The main paired results are:

- Fomo3D-inspired searcher-only: `delta_p_win = 0.000`;
- Fomo3D-inspired builder reorder and selective inclusion:
  `delta_p_win = +0.080`, paired bootstrap 95% interval `[-0.120, +0.280]`;
- Dice2Win-inspired capabilities: `delta_p_win = 0.000`;
- all 600 public-informed scenario executions passed runtime invariants;
- selective inclusion remains `liveness_status = NOT_CHECKED`;
- break-even values are conditional sensitivity results because bid and
  opportunity cost remain `MODELED`.

The interval around `+0.080` contains zero. Step 11 therefore does not claim a
stable positive advantage or historical profitability. The two-transaction
workload remains a minimal capability test; the optional 2/5/10 participant
batch was not run.

The next required work is Step 12: write the final report, audit claim wording
and package the reproduction instructions. Real-application replay remains an
optional extension, not a completion requirement.
