# IS6105.11.CH — Replay RNG của Nhóm Blockchain 02

Artifact nghiên cứu giữa kỳ đã được kiểm chứng cho đề tài:

> Capability-Aware Analysis of Weak On-Chain RNG Exploitability on BNB Smart Chain

Repository này chỉ chứa các artifact nộp bài đã được kiểm chứng. Repository
không chứa workspace gốc, template proposal, bản nháp, ghi chú bài giảng, file
làm việc cá nhân hoặc bản DOCX nộp trước đây.

## Nội dung repository

- `Blockchain-Group02-RNG-Midterm2-verified-report.pdf` — báo cáo cuối.
- `Blockchain-Group02-RNG-Midterm2-verified-report.md` — source của báo cáo.
- `Blockchain-Group02-RNG-Midterm2-verified-report.metadata.yaml` — PDF-only
  metadata của Pandoc; file được tách riêng để GitHub không render metadata
  thành bảng.
- `code/` — code tối thiểu, fixture, schema, analysis, report, bảng, biểu đồ,
  manifest và replay logs đã được kiểm chứng.

Batch đã kiểm chứng gồm 100 BSC contexts, 2.400 observations, sáu scenario,
bốn cost model và không có context thất bại. Schema validation đã pass. Kết
quả là controlled local replay trên synthetic adapter. Đây không phải bằng
chứng một actor lịch sử trên BSC đã tấn công, không ước lượng prevalence trên
toàn BSC và không chứng minh profitability thực tế.

Confirmatory holdout 1.000 contexts, các run participant robustness 2/5/10,
slide deck và speaker script không được đưa vào vì các artifact đó không có
trong workspace đã kiểm chứng.

## Kế hoạch nghiên cứu theo từng bước

| Step | Nội dung | Tài liệu |
|---:|---|---|
| 1 | Bản đồ nghiên cứu | [Step 1](code/step_1_research_map.md) |
| 2 | Phạm vi và claims | [Step 2](code/step_2_lock_scope_and_claims.md) |
| 3 | Khảo sát related work | [Step 3](code/step_3_review_related_work.md) |
| 4 | Threat model | [Step 4](code/step_4_define_threat_model.md) |
| 5 | Đặc tả experiment và dataset | [Step 5](code/step_5_specify_experiment.md) |
| 6 | Thu thập block context BSC | [Step 6](code/step_6_crawl_bsc_contexts.md) |
| 7 | Replay harness | [Step 7](code/step_7_build_replay_harness.md) |
| 8 | Attack strategies | [Step 8](code/step_8_implement_attack_strategies.md) |
| 9 | Pilot và quyết định go/no-go | [Step 9](code/step_9_run_pilot.md) |
| 10 | Public-informed synthetic evaluation | [Step 10](code/step_10_collect_full_dataset.md) |
| 11 | Phân tích kết quả | [Step 11](code/step_11_analyze_results.md) |
| 12 | Báo cáo và phát hành artifact | [Step 12](code/step_12_write_report_and_release.md) |

Các file step mô tả research plan và provenance của workflow.

## Reproduce và validate

Các lệnh dưới đây được chạy từ `code/`. Hãy cài dependency của project và
Foundry/Anvil local trước, hoặc điều chỉnh theo Docker setup của workspace gốc.

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

Để rebuild PDF từ report source:

```bash
pandoc Blockchain-Group02-RNG-Midterm2-verified-report.md \
  --metadata-file Blockchain-Group02-RNG-Midterm2-verified-report.metadata.yaml \
  -o Blockchain-Group02-RNG-Midterm2-verified-report.pdf \
  --pdf-engine=xelatex \
  --resource-path=".:code"
```

Chạy crawl hoặc replay mới có thể cần `PINAX_API_KEY` local. Không commit
`.env`, API key, private RPC URL, credential hoặc private order flow.

## Ranh giới bằng chứng

- `OBSERVED`: chain context hoặc source evidence được data pipeline đọc.
- `REPLAYED`: thực thi local trên Foundry/Anvil.
- `MODELED`: giả định về prize, bid/bribe và opportunity cost.
- `DERIVED`: metric tính từ replay output.
- `HYPOTHESIS`: proposition nghiên cứu chưa được xác nhận.

`BUILDER_RECEIVED` là capability assumption trong experiment, không phải
private order flow quan sát được. Các contract Fomo3D-inspired và
Dice2Win-inspired là synthetic adapter; không claim deployed application replay.

## License và attribution

Repository này là course research artifact của Nhóm Blockchain 02. Các source
reference được giữ attribution gốc. Việc phân phối lại public-chain data vẫn
phụ thuộc điều khoản của provider.
