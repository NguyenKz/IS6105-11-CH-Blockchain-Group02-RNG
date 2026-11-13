# Verified replay code

This directory contains the reproducible code, research plan, fixtures, schema,
analysis, reports, and verified logs for the midterm artifact.

## Research plan

The ordered research plan is in `step_1_research_map.md` through
`step_12_write_report_and_release.md`. The plan documents process and evidence
boundaries; it does not turn unexecuted experiments into results.

## Verified result

The completed batch is `data/derived/public_informed_synthetic/` with 100
contexts and 2,400 observations. The manifest and schema validation output are
under `data/manifests/` and the dataset directory. Results are controlled local
replay on synthetic adapters, not historical attack evidence.

## Run validation

```bash
python scripts/replay/test_public_informed.py
python scripts/replay/validate_result.py \
  --self-test \
  --schema research/bsc_rng_mev_replay.schema.json
python scripts/replay/validate_result.py \
  --input data/derived/public_informed_synthetic/observations.jsonl \
  --schema research/bsc_rng_mev_replay.schema.json
```

The PDF report is built from the repository root with the separate
`Blockchain-Group02-RNG-Midterm2-verified-report.metadata.yaml` file. Keeping
Pandoc metadata separate prevents GitHub from rendering it as a table.

Fresh crawl/replay commands may require a local `PINAX_API_KEY`. Never commit
`.env`, keys, credentials, private RPC URLs, or private order flow.
