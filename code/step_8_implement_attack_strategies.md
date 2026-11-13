# Step 8: Cài đặt attack strategies

## Mục tiêu

Biến actor capabilities thành các strategy có thể chạy, kiểm tra và so sánh trên cùng context.

## Strategy 1: Searcher-only

Searcher được phép:

- Đọc public state theo visibility model.
- Chọn input hoặc thời điểm gửi transaction của mình.
- Gửi transaction/bundle của mình.

Searcher không được:

- Di chuyển hoặc xóa transaction của user khác.
- Đọc private order flow trong `PUBLIC_ONLY`.
- Chọn block header field ngoài khả năng đã khai báo.

## Strategy 2: Builder reorder

Builder dùng cùng transaction set với canonical run nhưng chọn thứ tự hợp lệ khác.

Generator phải giữ:

- Nonce order của từng sender.
- Dependency giữa transaction.
- Block gas limit.
- State validity.

Không cần vét cạn mọi permutation. Định nghĩa strategy search có giới hạn và ghi rõ đó là lower bound hay upper-bound approximation.

## Strategy 3: Builder selective inclusion

Builder được trì hoãn hoặc không include một candidate transaction trong block hiện tại theo scenario catalog.

Phải ghi:

- Transaction nào bị loại.
- Lý do transaction đó thuộc visibility set của builder.
- Outcome trong block hiện tại.
- Hệ quả liveness chưa được mô hình nếu transaction có thể vào block sau.

Kết quả này là counterfactual capability, không phải bằng chứng censorship lịch sử.

## Strategy trên safe reference

Chạy lại cùng strategy interface. Nếu strategy không còn ảnh hưởng outcome, vẫn ghi transaction cost và replay result. Không thay workload để làm safe reference đẹp hơn.

## Economic model

Tách các thành phần:

| Thành phần | Nguồn | Evidence label |
| --- | --- | --- |
| `attacker_tx_cost` | Replay receipt hoặc observed gas price rule | `REPLAYED` hoặc `DERIVED` |
| `explicit_bid_or_bribe` | Quan sát được nếu có, nếu không dùng scenario parameter | `OBSERVED` hoặc `MODELED` |
| `opportunity_cost` | Sensitivity parameter khi không quan sát được | `MODELED` |
| `incremental_expected_payout` | Paired outcomes và prize | `DERIVED` |

Không dùng block reward đơn giản làm toàn bộ opportunity cost.

## Strategy trace schema

```text
strategy_id
strategy_version
candidate_transactions
selected_order
excluded_transactions
search_budget
validity_checks
objective_value
stop_reason
```

## Đầu ra

- Strategy modules trong `scripts/replay/strategies/`
- Strategy unit tests.
- `research/strategy_spec.md`
- `research/cost_models.csv`
- `reports/strategy_validation.md`

## Tiêu chí hoàn thành

- Mỗi strategy ánh xạ đến một actor capability.
- Searcher test thất bại nếu code cố reorder honest transaction.
- Reorder output luôn thỏa nonce/dependency checks.
- Selective inclusion ghi rõ excluded transaction.
- Economic output không trộn modeled cost với measured cost.

## Lỗi cần tránh

- Cho builder chọn outcome trực tiếp thay vì tìm một transaction order hợp lệ.
- Chỉ giữ strategy thắng và bỏ strategy thất bại.
- Gọi best-found order là global optimum khi search chưa vét cạn.

