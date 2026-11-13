# Step 9: Chạy pilot và quyết định go/no-go

## Mục tiêu

Kiểm tra toàn bộ pipeline trên khoảng 100 finalized BSC contexts trước khi khóa full-run sample và tốn thêm RPC/compute.

## Điều kiện bắt đầu

- Protocol, threat model và schema đã tồn tại.
- RPC preflight đã xác minh historical state access.
- Weak RNG baseline và một safe reference chạy end-to-end.
- Ba capability strategies có test.

## Pilot matrix tối thiểu

Trên mỗi context hợp lệ:

- Canonical weak RNG.
- Searcher-only weak RNG.
- Builder reorder weak RNG.
- Builder selective inclusion weak RNG.
- Canonical và các strategy tương ứng trên safe reference.

Nếu chi phí quá cao, chạy một subset đã định trước và ghi rõ selection rule.

## Kiểm tra kỹ thuật

- Tỷ lệ context có thể fork/load.
- Determinism khi rerun cùng seed.
- Schema validation.
- Canonical/counterfactual pre-state equality.
- Transaction validity sau reorder.
- Coverage của receipt và trace.
- Runtime, RPC usage và storage growth.

## Kiểm tra phương pháp

- Metric có thực sự thay đổi khi capability tăng không?
- Failure reason có phân biệt lỗi dữ liệu, lỗi harness và scenario không khả thi không?
- Opportunity cost có đang bị trình bày sai như measured data không?
- Safe reference có dùng cùng workload không?
- Mỗi RQ có ít nhất một output khả dụng từ pilot không?

## Go/no-go table

| Kết quả | Quyết định |
| --- | --- |
| Pipeline deterministic, context đủ dữ liệu, schema ổn | Go: khóa protocol v1 và thiết kế full run |
| RPC thiếu archive state | Đổi provider hoặc thu hẹp window, không thay bằng unrelated dataset |
| Reorder thường invalid | Sửa dependency model hoặc giảm search space |
| Weak RNG pattern không thể hiện capability đang nghiên cứu | Thay pattern có căn cứ từ Related Work và ghi protocol amendment |
| Safe reference không cùng workload | Sửa harness trước khi full run |
| Cost component không quan sát được | Giữ dưới dạng modeled sensitivity và hạ mức claim |

## Sau pilot

1. Viết `reports/pilot_report.md`.
2. Ghi mọi protocol amendment.
3. Khóa schema version 1.
4. Chọn full-run sample size và sampling window dựa trên bằng chứng pilot.
5. Đóng băng code commit dùng cho full run.

## Đầu ra

- `reports/pilot_report.md`
- `data/derived/pilot/`
- `data/manifests/pilot_manifest.json`
- Protocol amendment nếu cần.
- Quyết định `GO`, `NARROW` hoặc `STOP` có lý do.

## Tiêu chí hoàn thành

- Ít nhất một context có canonical và manipulated replay thành công như proposal yêu cầu.
- Mọi context pilot có result hoặc machine-readable failure reason.
- Determinism được kiểm tra trên fixture chọn trước.
- Full-run sampling plan không được chọn theo outcome mong muốn.
- Quyết định go/no-go được ghi trước khi chạy full dataset.

## Lỗi cần tránh

- Xóa row fail để tăng replay success.
- Báo pilot effect size như kết quả cuối.
- Thêm RQ mới vì thấy một pattern thú vị mà không tách exploratory analysis.

## Sau khi pilot đã Revalidated

Pilot hiện tại được giữ là `VERY_SIMPLE_RULES` method-validation baseline.
Bước tiếp theo, nếu được duyệt, chỉ là screen khoảng 3 public projects và xây
1–2 public-informed synthetic rule families chạy cùng workload. Một real-rule
replay là tùy chọn, không phải gate bắt buộc. Không chọn hướng theo kết quả
pilot và không chạy predictor rule inference trong đồ án này.

