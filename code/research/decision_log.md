# Step 2 Decision Log

## Decision D-001: Study boundary

- Date: 2026-10-01
- Decision: Study current BSC mainnet finalized block contexts and payoff-bearing weak RNG.
- Included capability levels: searcher-only, builder reorder, and builder selective inclusion.
- Excluded from the core: multi-block reorg, majority collusion, consensus attacks, generic arbitrage, selective-abort deposit optimization, all-chain prevalence scanning and new RNG protocol design.
- Reason: These exclusions keep the study focused on actor-specific exploitability and economic viability.
- Source: `research_detail.md`, `step_1_research_map.md`, `step_2_lock_scope_and_claims.md`.

## Decision D-002: Actor boundary

- Decision: Treat user, searcher, builder and proposer as separate roles.
- Builder is the primary block-construction actor in the counterfactual model.
- Proposer is described for architectural completeness and is not a primary attacker.
- No proposer collusion, majority power or arbitrary header rewriting is assumed.
- Source: `research_detail.md`, `step_4_define_threat_model.md`, `research/protocol.md`.

## Decision D-003: Evidence boundary

- Decision: Label every value as `OBSERVED`, `REPLAYED`, `MODELED` or `DERIVED`.
- A replay outcome is evidence of possibility under a declared model, not evidence that a historical actor performed the attack.
- Unmeasured quantitative claims remain `HYPOTHESIS` in `claims_register.csv`.
- Source: `step_1_research_map.md`, `research/protocol.md`.

## Decision D-004: Primary safe reference

- Decision: Use `commit-before-entropy` as the Step 2 primary safe reference.
- Reason: It can be represented as a deterministic flow in the same local replay harness without treating an oracle mock as evidence about VRF security.
- Gate: Step 5 must verify deterministic replay, invariant preservation and valid outcome comparison. If the gate fails, Step 5 may promote VRF and must record the change here.
- Deferred mechanism: VRF is preserved in `safe_reference_todo.md`.

## Decision D-005: Ethical boundary

- Decision: Collect read-only mainnet data and use local or forked replay only.
- Prohibited: sending attack transactions to BSC mainnet, publishing credentials or private endpoints, and presenting source-pattern detection as proof of a live exploit.
- A concrete live-contract risk must follow responsible disclosure separately from the course report.

## Open gates for later steps

1. Step 3 must support the research gap with a related-work matrix and dated search log.
2. Step 4 must verify actor permissions against current BSC specifications.
3. Step 5 must lock schema, sampling and analysis before the full run.
4. Step 5 must decide whether VRF remains deferred or becomes the primary safe reference.

## Decision D-006: Related-work boundary

- Date: 2026-10-01
- Decision: Use only project context and direct primary or official sources listed in `step_3_review_related_work.md`.
- Excluded input: `/Users/nguyenkz/Downloads/deep-research-report (2).md` because it is outside the project and is not a project artifact.
- Related-work gap wording is conditional on the recorded search scope. No claim of being the first study is made.
- Source: `research/search_log.csv`, `research/related_work_matrix.csv`, `research/related_work_notes.md`.

## Decision D-007: Threat-model boundary

- Date: 2026-10-01
- Decision: Keep user, searcher, builder and proposer as separate actors. Use `PUBLIC_ONLY` and `BUILDER_RECEIVED` as the visibility models.
- Builder reorder and selective inclusion remain counterfactual capabilities. They are not observations about historical builder behavior.
- Reorg, majority collusion, proposer attack, private-flow access for searchers, arbitrary header edits and generic arbitrage remain outside the core.
- Source: `research/threat_model.md`, `research/scenario_catalog.csv`, `research/invariants.md`, BEP-322 and BNB Chain MEV documentation.

## Decision D-008: Step 5 experiment lock

- Date: 2026-10-01
- Decision: Lock paired canonical/counterfactual replay on BSC mainnet finalized contexts, using the six scenarios in `research/scenario_catalog.csv`.
- Primary safe reference: `COMMIT_BEFORE_ENTROPY`. VRF remains deferred until its request, fulfillment, verification and failure behavior can be replayed without a mock oracle.
- Sampling: the existing 100 contexts from blocks 125053984–125054083 are feasibility-only. Full-run selection must use a pre-registered finalized window, fixed seed and outcome-independent hash ordering, with no intentional overlap.
- Analysis: use paired differences, failure-preserving reporting, named cost models and uncertainty intervals. No prevalence, historical attack or positive-profit claim is asserted before replay evidence exists.
- Source: `research/experiment_protocol.md`, `research/data_dictionary.md`, `research/sampling_plan.md`, `research/analysis_plan.md`, `research/schema/bsc_rng_mev_replay.schema.json`.

## Decision D-009: Step 7 replay toolchain

- Date: 2026-10-01
- Decision: Use Foundry `1.8.3` and Anvil for the local replay harness. The fixture forks BSC at pre-state block `125053983`, runs on local chain ID `56`, and never broadcasts a transaction to BSC mainnet.
- Fixture boundary: the synthetic weak-RNG and commit-before-entropy contracts receive the observed source block hash as a pinned public-context input. Their outcomes are `REPLAYED` fixture evidence, not historical contract or builder observations.
- Validation: weak builder reorder changes the fixture winner, the safe reference preserves it, snapshot restoration passes, and two observation rows validate against the Step 5 schema.
- Source: `replay/`, `scripts/replay/`, `data/replay/fixture/`, `reports/replay_harness_validation.md`.

## D-010 — Step 8 strategy boundary

The strategy engine uses three explicit capabilities: searcher-only input or
timing, builder reorder over the received set, and predeclared builder
selective inclusion. Each strategy is deterministic and records its candidate
set, selected order, exclusions, validity checks, search budget and stop
reason. The safe reference uses the same interface and workload. No strategy
is treated as historical censorship or a global optimum.

## D-011 — Step 9 pilot decision

The 100-context strategy pilot ran on local Anvil forks for source blocks
125053984–125054083. All 100 contexts loaded and produced schema-valid paired
results; no mainnet write was made and no failure rows were needed. The gate is
`GO` for continued replay-pipeline engineering only. This does not upgrade
claims C-002–C-005, and it does not establish prevalence, historical attack or
economic viability. The four cost models remain modeled sensitivity labels;
`net_profit_wei` is intentionally not used as a conclusion.

## D-012: Relevant transaction-count boundary

- Date: 2026-10-10.
- Decision: Retain the two-transaction Step 10 workload as the minimal
  capability test. It supports the claim that order can change a decoded
  outcome, but not a claim about realistic effect magnitude, all-block
  behavior or prevalence.
- Scale definition: Use the number of transactions that compete in the same
  workload. Do not recreate unrelated transactions solely to match the total
  transaction count of a real block.
- Optional robustness check: If time permits, replay participant counts 2, 5
  and 10 on the same 100 contexts and rule families, with all other protocol
  choices fixed. Save the result in a separate exploratory batch.
- Reporting rule: If the robustness check is not run, state the
  two-transaction limitation and do not generalize the observed `+0.080`
  `delta_p_win` as a realistic effect magnitude.
- Source: `step_11_analyze_results.md`,
  `reports/public_informed_synthetic_report.md`.
