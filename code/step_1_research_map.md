# Step 1: Bản đồ nghiên cứu

## Mục tiêu

Biến `research_detail.md` thành một chuỗi công việc có thứ tự, đầu ra và điều kiện dừng rõ ràng. File này là mục lục điều hành cho toàn bộ hướng nghiên cứu.

## Câu hỏi nghiên cứu được giữ nguyên

| RQ | Nội dung cần chứng minh | Bằng chứng chính |
| --- | --- | --- |
| RQ-C1 | Mỗi actor có thể dự đoán hoặc tác động loại weak RNG nào | Threat model, scenario tests và replay traces |
| RQ-C2 | Reorder hoặc selective inclusion thay đổi xác suất thắng và EV bao nhiêu | Paired replay trên cùng block context |
| RQ-C3 | Khi nào chiến lược thao túng có `net_profit > 0` | Phí quan sát được kết hợp các thành phần chi phí được gắn nhãn rõ |
| RQ-C4 | Safe reference giảm exploitability bao nhiêu | Cùng context, cùng workload và cùng capability level |

## Thứ tự thực hiện

| Step | File | Kết quả cần đạt | Phụ thuộc |
| --- | --- | --- | --- |
| 1 | `step_1_research_map.md` | Bản đồ công việc và quy tắc bằng chứng | `research_detail.md` |
| 2 | `step_2_lock_scope_and_claims.md` | Khóa scope, RQ, thuật ngữ và claim register | Step 1 |
| 3 | `step_3_review_related_work.md` | Ma trận related work và research gap có căn cứ | Step 2 |
| 4 | `step_4_define_threat_model.md` | Actor-capability matrix và scenario catalog | Step 2, Step 3 |
| 5 | `step_5_specify_experiment.md` | Protocol, biến, metric, schema và kế hoạch phân tích | Step 4 |
| 6 | `step_6_crawl_bsc_contexts.md` | Raw block contexts có provenance và kiểm tra chất lượng | Step 5 |
| 7 | `step_7_build_replay_harness.md` | Harness replay deterministic cho weak RNG và safe reference | Step 5, Step 6 |
| 8 | `step_8_implement_attack_strategies.md` | Searcher, reorder và selective inclusion strategies | Step 4, Step 7 |
| 9 | `step_9_run_pilot.md` | Pilot report và quyết định go/no-go | Step 6, Step 7, Step 8 |
| 10 | `step_10_collect_full_dataset.md` | Dataset chính theo protocol đã khóa | Step 9 pass |
| 11 | `step_11_analyze_results.md` | Bảng, biểu đồ và câu trả lời cho bốn RQ | Step 10 |
| 12 | `step_12_write_report_and_release.md` | Báo cáo và artifact có thể tái lập | Step 11 |

## Quy tắc phân loại bằng chứng

Mọi con số trong dữ liệu và báo cáo phải có một trong bốn nhãn:

| Nhãn | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `OBSERVED` | Lấy trực tiếp từ BSC/RPC | block header, gas used, canonical transaction order |
| `REPLAYED` | Sinh ra khi chạy lại context có kiểm soát | outcome sau reorder, gas của attacker transaction |
| `MODELED` | Giá trị giả định hoặc sensitivity parameter | opportunity cost, private builder bid không quan sát được |
| `DERIVED` | Tính từ các trường trên bằng công thức đã khóa | `delta_p_win`, `net_profit`, break-even prize |

Không dùng `REPLAYED` để khẳng định builder thật đã tấn công. Không gọi `MODELED` là dữ liệu đo được.

## Cấu trúc artifact dự kiến

Các step sau sẽ tạo artifact theo cấu trúc này. Chưa cần tạo toàn bộ thư mục ở Step 1.

```text
final_project/code/
├── research/
│   ├── protocol.md
│   ├── threat_model.md
│   ├── related_work_matrix.csv
│   └── scenario_catalog.csv
├── data/
│   ├── raw/
│   ├── interim/
│   ├── derived/
│   └── manifests/
├── contracts/
├── scripts/
├── analysis/
└── reports/
```

## Quy tắc chuyển step

Chỉ chuyển sang step tiếp theo khi:

- Đầu ra bắt buộc của step hiện tại đã tồn tại.
- Tiêu chí hoàn thành trong file step đã được đánh dấu.
- Các quyết định thay đổi scope đã được ghi vào decision log.
- Dữ liệu hoặc claim mới có provenance.

Nếu một gate thất bại, quay lại step tạo ra giả định sai. Không thêm dataset hoặc attack scenario ngoài scope để che lấp lỗi pipeline.

## Đầu ra

- Chuỗi 12 step được liên kết từ `README.md`.
- Bảng ánh xạ RQ sang loại bằng chứng.
- Quy tắc evidence label dùng xuyên suốt nghiên cứu.
- Definition of done chung cho hướng 1.

## Tiêu chí hoàn thành của Step 1

- Tất cả step file được tạo và liên kết hợp lệ.
- Mỗi step sau có mục tiêu, đầu ra và tiêu chí hoàn thành.
- Thứ tự phụ thuộc không yêu cầu artifact chưa được tạo.
- Cả bốn RQ xuất hiện trong bản đồ nghiên cứu.

## Definition of done của toàn hướng

Hướng nghiên cứu hoàn thành khi:

- Bốn RQ có câu trả lời từ cùng một derived replay dataset.
- Mọi scenario tuân thủ threat model đã khóa.
- Canonical và manipulated run có cùng pre-state và workload, chỉ khác capability đang kiểm tra.
- Báo cáo phân biệt `OBSERVED`, `REPLAYED`, `MODELED` và `DERIVED`.
- Một người khác có thể lấy manifest, chạy lại một context và thu được cùng outcome.
