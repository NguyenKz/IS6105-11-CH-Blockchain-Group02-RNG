# IS6105.11.CH — Blockchain Group 02 RNG Replay

Verified midterm research artifact for:

> Capability-Aware Analysis of Weak On-Chain RNG Exploitability on BNB Smart Chain

This repository contains only the verified submission artifacts. It does not
contain the original workspace, proposal templates, drafts, lecture notes,
personal working files, or the previous DOCX submission.

## What is included

- `Blockchain-Group02-RNG-Midterm2-verified-report.pdf` — final report.
- `Blockchain-Group02-RNG-Midterm2-verified-report.md` — report source.
- `main_direction/` — minimal code, fixtures, schema, analysis, reports,
  tables, figures, manifests, and verified replay logs.

The verified batch contains 100 BSC contexts, 2,400 observations, six
scenarios, four cost models, and zero failed contexts. Schema validation passed.
The results are controlled local replay results on synthetic adapters. They are
not evidence that a historical BSC actor performed an attack, and they do not
estimate BSC-wide prevalence or real-world profitability.

The 1,000-context confirmatory holdout, participant robustness 2/5/10 runs,
slide deck, and speaker script are not included because those artifacts were
not present in the verified workspace.

## Reproduce and validate

The commands below run from `main_direction/`. Install the project dependencies
and Foundry/Anvil locally first, or adapt them to the Docker setup used by the
original workspace.

```bash
cd main_direction
python scripts/replay/test_public_informed.py
python scripts/replay/validate_result.py \
  --self-test \
  --schema research/bsc_rng_mev_replay.schema.json
python scripts/replay/validate_result.py \
  --input data/derived/public_informed_synthetic/observations.jsonl \
  --schema research/bsc_rng_mev_replay.schema.json
```

Running a fresh crawl or replay may require a local `PINAX_API_KEY`. Never
commit `.env`, API keys, private RPC URLs, credentials, or private order flow.

## Evidence boundary

- `OBSERVED`: chain context or source evidence read by the data pipeline.
- `REPLAYED`: local Foundry/Anvil execution.
- `MODELED`: prize, bid/bribe, and opportunity-cost assumptions.
- `DERIVED`: metrics calculated from replay output.
- `HYPOTHESIS`: an unconfirmed research proposition.

`BUILDER_RECEIVED` is an experimental capability assumption, not observed
private order flow. The Fomo3D-inspired and Dice2Win-inspired contracts are
synthetic adapters; deployed application replay is not claimed.

## License and attribution

This repository is a course research artifact by Blockchain Group 02. The
included source references retain their original attribution. Public-chain
data redistribution remains subject to the terms of its provider.
