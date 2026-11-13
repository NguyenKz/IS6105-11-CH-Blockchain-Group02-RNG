# Code replay đã được kiểm chứng

Thư mục này chứa code có thể tái lập, research plan, fixture, schema, analysis,
report và logs đã được kiểm chứng cho artifact giữa kỳ.

## Research plan

Research plan theo thứ tự nằm trong `step_1_research_map.md` đến
`step_12_write_report_and_release.md`. Plan mô tả quy trình và ranh giới bằng
chứng; plan không biến experiment chưa chạy thành kết quả.

## Kết quả đã kiểm chứng

Batch đã hoàn thành là `data/derived/public_informed_synthetic/`, gồm 100
contexts và 2.400 observations. Manifest và schema validation output nằm trong
`data/manifests/` và thư mục dataset. Kết quả là controlled local replay trên
synthetic adapter, không phải bằng chứng historical attack.

## Chạy validation

```bash
python scripts/replay/test_public_informed.py
python scripts/replay/validate_result.py \
  --self-test \
  --schema research/bsc_rng_mev_replay.schema.json
python scripts/replay/validate_result.py \
  --input data/derived/public_informed_synthetic/observations.jsonl \
  --schema research/bsc_rng_mev_replay.schema.json
```

PDF report được build từ repository root bằng file riêng
`Blockchain-Group02-RNG-Midterm2-verified-report.metadata.yaml`. Tách Pandoc
metadata giúp GitHub không render metadata thành bảng.

Crawl/replay mới có thể cần `PINAX_API_KEY` local. Không commit `.env`, key,
credential, private RPC URL hoặc private order flow.
