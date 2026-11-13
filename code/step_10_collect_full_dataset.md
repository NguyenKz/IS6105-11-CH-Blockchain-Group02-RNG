# Step 10: Chạy nghiên cứu mở rộng có kiểm soát

## Vai trò của bước này

Step 10 đã hoàn tất dưới dạng một bước bổ sung nhỏ sau method-validation baseline. Đây không phải một dataset nhiều tầng hoặc khảo sát toàn hệ sinh thái.

### Baseline đã có

VERY_SIMPLE_RULES là workload synthetic rất đơn giản dùng trong pre-experiment validation. Step 8–9 đã Revalidated và các artifact trong data/derived/pilot/ cùng data/derived/pre_experiment_validation/ phải được giữ nguyên.

Baseline trả lời câu hỏi: pipeline có chạy đúng không? Nó chưa trả lời rule đơn giản này phổ biến đến đâu hoặc có historical attack trên BSC hay không.

### Phần bổ sung chính: public-informed synthetic rules

Mục tiêu là kiểm tra xem kết quả có còn giữ khi rule không còn do nhóm tự chọn hoàn toàn.

1. Khảo sát khoảng 3 dự án công khai.
2. Ghi cả candidate pass, fail và excluded vào research/public_rule_catalog.csv.
3. Chọn 1–2 rule family có evidence rõ ràng.
4. Tạo synthetic adapter tối giản, có mapping từ public mechanism sang abstraction và invariant được giữ.
5. Chạy cùng workload, context, participant count, target index, capability, seed, cost model và analysis như baseline.
6. Ghi output vào batch riêng, không ghi vào pilot hoặc pre-experiment batch.
7. So sánh baseline với từng public-informed rule family; không chọn top 3 hướng sau khi xem kết quả.

Đầu vào provenance tối thiểu:

- source hoặc bytecode và code hash;
- ABI/calldata;
- event/trace/storage evidence;
- randomness source;
- winner/payoff rule;
- mapping và giới hạn của synthetic abstraction.

Output đã tạo:

    final_project/code/data/derived/public_informed_synthetic/
    final_project/code/data/manifests/public_informed_synthetic_manifest.json
    final_project/code/reports/public_informed_synthetic_report.md

### Phần tùy chọn: một rule thật

Chỉ thực hiện nếu còn thời gian và có đủ:

- source hoặc bytecode;
- ABI/calldata;
- randomness/payoff evidence;
- trace/event/storage evidence;
- replay match tại đúng pre-state.

Chỉ chọn tối đa một application/rule. Nếu không đủ điều kiện, ghi unsupported hoặc rule_unconfirmed, không ép replay và không thay bằng target thuận tiện hơn.

Output nếu có:

    final_project/code/data/derived/real_rule_optional/
    final_project/code/reports/real_rule_optional_report.md

Rule inference từ nhiều context không nằm trong Step 10. Đây là future work; nếu triển khai sau này phải tách context dùng để suy đoán khỏi context dùng để validation.

## Điều kiện bắt đầu

- Step 8–9 vẫn ở trạng thái Revalidated.
- Baseline artifacts và pilot manifest đã được giữ nguyên.
- Public-rule catalog, provenance schema và mapping template đã được review.
- Workload và capability matrix đã khóa trước khi xem kết quả.
- Batch output mới đã được xác định.

## Kiểm tra bắt buộc

- Catalog có khoảng 3 candidate, gồm cả status pass/fail/excluded.
- Mỗi synthetic family có public evidence và mapping rõ ràng.
- Baseline và Tier 1 dùng cùng workload và pipeline; chỉ rule mechanism thay đổi.
- Canonical/counterfactual vẫn paired từ cùng pre-state.
- Receipts, traces, events, invariants và failure reasons đầy đủ.
- Schema validation và git diff --check pass.
- Không sửa pilot hoặc pre-experiment artifacts.
- Không gọi synthetic result là historical attack evidence.

## Tiêu chí hoàn thành

Phần bổ sung chính đã hoàn tất với:

- 3 public candidates: Fomo3D Long, Dice2Win v5 và PancakeSwap Lottery v2;
- 2 synthetic mappings được triển khai;
- 100/100 contexts thành công;
- 600 scenario executions và 2.400 observations hợp lệ;
- receipt, trace, event và invariant evidence đầy đủ trong batch riêng;
- report có so sánh với `VERY_SIMPLE_RULES`.

Dice2Win vẫn mang provenance status `RULE_UNCONFIRMED` vì chưa lấy lại được historical runtime bytecode, dù official source đã xác nhận cơ chế. PancakeSwap VRF chỉ là catalog-only reference và không được thay bằng mock VRF.

Kết quả Step 10 là synthetic replay có provenance. Nó không chứng minh historical attack trên Fomo3D, Dice2Win, PancakeSwap hoặc BSC. Phần rule thật vẫn là optional và không phải điều kiện hoàn thành.
