# IS6105.11.CH — Blockchain Group 02 RNG Replay

Verified midterm research artifact for:

> Capability-Aware Analysis of Weak On-Chain RNG Exploitability on BNB Smart Chain

This repository contains only the verified submission artifacts. It does not
contain the original workspace, proposal templates, drafts, lecture notes,
personal working files, or the previous DOCX submission.

## What is included

- `Blockchain-Group02-RNG-Midterm2-verified-report.pdf` — final report.
- `Blockchain-Group02-RNG-Midterm2-verified-report.md` — report source.
- `code/` — minimal code, fixtures, schema, analysis, reports,
  tables, figures, manifests, and verified replay logs.

The verified batch contains 100 BSC contexts, 2,400 observations, six
scenarios, four cost models, and zero failed contexts. Schema validation passed.
The results are controlled local replay results on synthetic adapters. They are
not evidence that a historical BSC actor performed an attack, and they do not
estimate BSC-wide prevalence or real-world profitability.

The 1,000-context confirmatory holdout, participant robustness 2/5/10 runs,
slide deck, and speaker script are not included because those artifacts were
not present in the verified workspace.

## Kế hoạch nghiên cứu từng bước

| Step | Nội dung | Tài liệu |
|---:|---|---|
| 1 | Bản đồ nghiên cứu | [Step 1](code/step_1_research_map.md) |
| 2 | Khóa phạm vi và claims | [Step 2](code/step_2_lock_scope_and_claims.md) |
| 3 | Khảo sát nghiên cứu liên quan | [Step 3](code/step_3_review_related_work.md) |
| 4 | Xác định threat model | [Step 4](code/step_4_define_threat_model.md) |
| 5 | Đặc tả thí nghiệm và dataset | [Step 5](code/step_5_specify_experiment.md) |
| 6 | Thu thập block context từ BSC | [Step 6](code/step_6_crawl_bsc_contexts.md) |
| 7 | Xây replay harness | [Step 7](code/step_7_build_replay_harness.md) |
| 8 | Cài đặt attack strategies | [Step 8](code/step_8_implement_attack_strategies.md) |
| 9 | Chạy pilot và quyết định go/no-go | [Step 9](code/step_9_run_pilot.md) |
| 10 | Chạy public-informed synthetic evaluation | [Step 10](code/step_10_collect_full_dataset.md) |
| 11 | Phân tích kết quả | [Step 11](code/step_11_analyze_results.md) |
| 12 | Viết báo cáo và đóng gói artifact | [Step 12](code/step_12_write_report_and_release.md) |

Các file step là research plan và provenance của quy trình, không biến các run
chưa thực hiện thành kết quả. Confirmatory holdout 1.000 contexts và
participant robustness 2/5/10 vẫn là kế hoạch/future work.

## Reproduce and validate

The commands below run from `code/`. Install the project dependencies
and Foundry/Anvil locally first, or adapt them to the Docker setup used by the
original workspace.

```bash
cd code
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
