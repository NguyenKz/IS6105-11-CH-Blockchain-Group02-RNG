# Step 11B: Confirmatory holdout và participant robustness

## Trạng thái

`PLANNED`, chưa triển khai.

Tài liệu này khóa kế hoạch tăng độ khách quan và độ đúng đắn sau Step 11. Việc
lưu kế hoạch không đồng nghĩa với đã crawl context, sửa replay harness hoặc chạy
thí nghiệm.

## Mục tiêu

Step 11B trả lời ba câu hỏi còn mở:

1. Hiệu ứng quan sát trong Step 11 có lặp lại trên context chưa từng dùng hay
   không?
2. Kết luận thay đổi thế nào khi workload có 2, 5 hoặc 10 participant liên quan?
3. Một rule thật có đủ evidence để replay đúng semantics hay không?

Step 10, Step 11 và toàn bộ artifact cũ được giữ nguyên. Giá trị `+0.080` hiện
tại được mô tả là hiệu ứng của strategy `first alternative order`, chưa được
coi là lợi thế tối ưu của builder.

## 1. Khóa mẫu holdout trước khi chạy

- Dùng đúng 1.000 BSC context mới, không trùng 100 context của pilot.
- Tại thời điểm thu thập, lấy finalized block hiện tại làm mốc cuối và tạo
  sampling frame gồm 2.000.000 block gần nhất.
- Xếp hạng block number bằng `SHA256(seed | chain_id | block_number)` với seed
  cố định `6105`.
- Chọn 1.000 context hợp lệ đầu tiên và 200 context dự phòng theo đúng thứ tự
  đã xếp hạng.
- Chỉ loại context khi RPC thiếu dữ liệu hoặc block và parent không hợp lệ. Mọi
  exclusion phải có lý do trong sampling manifest.
- Thu thập block, parent header và receipt. Dữ liệu quá lớn có thể không đưa
  vào Git, nhưng phải có hash và script tái tạo.
- Ghi pre-registration manifest trước khi xem bất kỳ replay outcome nào.
- Dùng fixed sample size 1.000, không dừng sớm theo chiều hoặc significance của
  kết quả.

## 2. Confirmatory holdout batch

Chạy đúng cấu hình Step 10 trên 1.000 context mới:

- hai participant;
- hai rule family hiện tại;
- sáu scenario;
- bốn cost model;
- strategy variant `LEGACY_FIRST_ALTERNATIVE` để kiểm tra trực tiếp khả năng
  lặp lại của kết quả Step 11.

Đầu ra dự kiến:

```text
data/derived/confirmatory_holdout/
data/manifests/confirmatory_holdout_manifest.json
reports/confirmatory_holdout_report.md
```

Quy mô dự kiến là 6.000 scenario execution và 24.000 observation row. Replay
failure vẫn phải được lưu với `failure_reason`, không được loại khỏi mẫu.

## 3. Participant robustness batch

Chọn trước 200 context từ holdout bằng seed riêng
`6105-participant-robustness`. Trên cùng 200 context đó, chạy:

```text
participant_count in {2, 5, 10}
```

Batch này mang nhãn `EXPLORATORY`, được lưu riêng và không thay thế confirmatory
holdout. Quy mô dự kiến là 3.600 scenario execution và 14.400 observation row.

Contract synthetic mới phải tổng quát participant count từ 2 đến 10 nhưng giữ
nguyên randomness rule, payoff decoder và capability boundary.

Strategy variant `DECLARED_BEST_RESPONSE` được khóa như sau:

- `SEARCHER_ONLY` chỉ đổi input của attacker và giữ nguyên order.
- `BUILDER_REORDER` xét canonical cùng các vị trí có thể đặt attacker, đồng
  thời giữ nguyên thứ tự tương đối của honest participant. Strategy chọn order
  làm attacker thắng nếu tồn tại, nếu không thì giữ canonical.
- `BUILDER_SELECTIVE_INCLUSION` chỉ được cân nhắc loại honest transaction đã
  khai báo trước. Nếu omission không cải thiện outcome thì giữ canonical.
- Strategy chỉ được dùng target và thông tin có sẵn trước execution. Strategy
  không được đọc counterfactual outcome rồi mới chọn action.
- Safe reference phải nhận toàn bộ commitment trước khi entropy được finalize.
  Reorder play không được thay đổi winner đã chốt.

## 4. Thay đổi interface và schema khi triển khai

Runner mới hoặc runner được tổng quát hóa phải nhận:

```text
--contexts
--raw-root
--output
--participant-count
--strategy-variant
--limit
--workers
```

Schema phải giữ artifact cũ hợp lệ và bổ sung các field optional cho batch mới:

- `sampling_batch_id`;
- `participant_count`;
- `strategy_variant`;
- `sampling_stratum`.

`run_id` của batch mới phải bao gồm rule family, participant count và strategy
variant để tránh collision. Runner phải từ chối output trỏ vào pilot,
pre-experiment validation, Step 10 hoặc Step 11 artifact.

## 5. Phân tích Step 11B

Tạo notebook đã execute và báo cáo riêng:

```text
analysis/step_11b_confirmatory_robustness.ipynb
reports/step_11b_results.md
```

Phân tích phải có:

- paired `delta_p_win`, bốn transition count, validity và failure rate;
- percentile bootstrap 95% với 10.000 resample và seed `6105`;
- paired randomization test cho primary comparison;
- kết quả theo 10 block-range stratum để kiểm tra phụ thuộc thời gian;
- so sánh legacy strategy với best-response trên 200 matched context;
- kết quả theo participant count 2, 5 và 10;
- action rate của reorder và omission;
- worst-case bounds khi có missing outcome;
- economic sensitivity với bid và opportunity cost tiếp tục mang nhãn
  `MODELED`.

Không đặt acceptance criterion yêu cầu hiệu ứng phải dương hoặc có statistical
significance.

## 6. Real-rule feasibility gate

Chỉ đánh giá PancakeSwap Lottery, candidate BSC đã có trong catalog. Không đổi
sang dự án khác nếu candidate này không đạt gate.

Gate yêu cầu:

- deployed address và code hash;
- verified source và ABI;
- một historical lottery round;
- request và fulfillment randomness evidence;
- event, payout và storage evidence;
- exact pre-state fork;
- canonical replay khớp observed outcome.

Nếu thiếu một điều kiện bắt buộc, ghi `unsupported` hoặc `rule_unconfirmed` và
dừng. Nếu gate pass, chỉ replay một historical round trong batch riêng. Một
capability không phù hợp với semantics thật phải được ghi `unsupported`, không
được ép rule thật vào mô hình synthetic.

## 7. Kiểm tra và điều kiện hoàn thành

- Unit test sampling deterministic, pilot overlap và reserve handling.
- Foundry test contract tổng quát với participant count 2, 5 và 10.
- Test best-response không dùng thông tin hậu nghiệm.
- Test searcher không reorder và builder không sửa attacker input.
- Test safe reference finalize entropy sau commitment cuối và giữ winner khi
  chỉ reorder play.
- Smoke test một context trước mỗi full batch.
- Validate toàn bộ observation bằng JSON Schema.
- Mọi branch hợp lệ có receipt, trace, event và snapshot-restoration evidence.
- Hash của artifact Step 8 đến Step 11 cũ không đổi.
- Notebook chạy hai lần tạo cùng bảng số liệu.
- `git diff --check` và secret scan đều pass.

Step 11 vẫn giữ trạng thái `Complete`. Step 11B chỉ chuyển thành `Complete` sau
khi holdout, robustness analysis và real-rule feasibility gate được ghi nhận.
Step 12 bắt đầu sau đó, hoặc sau khi blocker của Step 11B được mô tả rõ.

## Giới hạn kết luận

- Holdout cải thiện precision và khả năng kiểm tra lặp lại, nhưng không chứng
  minh historical attack hoặc prevalence toàn BSC.
- Participant robustness đo số transaction cùng cạnh tranh trong workload,
  không mô phỏng toàn bộ transaction của block.
- Selective inclusion vẫn cần cảnh báo `liveness_checked=false` và không chứng
  minh historical censorship.
- Real-rule replay phụ thuộc evidence và không phải điều kiện bắt buộc để hoàn
  thành đồ án.
