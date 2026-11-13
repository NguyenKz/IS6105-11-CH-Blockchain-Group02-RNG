# Step 11 robustness checks

## Completed checks

- Paired bootstrap: 10,000 context-level resamples with seed `6105`.
- Input integrity: 2,400 public-informed observations, 600 invariant rows and no replay failure.
- Cost-model duplication: outcome rates use only `FEE_ONLY`; economic sensitivity uses all four named models.
- Execution validity: canonical and manipulated runtime invariants pass for all 600 scenario executions.
- Safe lifecycle: commit-before-entropy checks and reorder winner preservation pass.

## Uncertainty

Fomo3D-inspired builder reorder has point estimate `+0.080` with 95% interval `[-0.120, +0.280]`. The interval includes zero. The report therefore does not claim a stable positive probability advantage.

## Known limitations

- The workload has one honest and one attacker transaction. It demonstrates a minimal capability, not realistic competition magnitude.
- The optional participant-count batch for 2, 5 and 10 participants was not run.
- Selective inclusion records a declared omission but does not measure liveness or historical censorship.
- Dice2Win-inspired replay abstracts the public mechanism; deployed-bytecode linkage remains `RULE_UNCONFIRMED`.
- Bid and opportunity cost are modeled. Break-even values are conditional sensitivity results.
