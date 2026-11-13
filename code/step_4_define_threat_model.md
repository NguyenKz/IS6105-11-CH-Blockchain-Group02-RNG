# Step 4: Xác định threat model

## Mục tiêu

Khóa thông tin, quyền và giới hạn của từng actor trước khi viết attack code.

## Actor model tối thiểu

| Actor | Quan sát | Hành động hợp lệ trong model | Bị cấm giả định |
| --- | --- | --- | --- |
| User | Confirmed state | Gửi transaction của mình | Không nhìn hoặc điều khiển block construction |
| Searcher | Public state và public order flow nhìn thấy được | Chọn lúc gửi, thay input, gửi transaction hoặc bundle của mình | Không reorder transaction của người khác; không thấy private flow |
| Builder | Pre-state và transaction/bundle nhận được | Chọn transaction set, tạo thứ tự hợp lệ, chèn transaction của mình | Không giả chữ ký; không tạo state invalid; không rewrite finalized chain |
| Proposer | Candidate bids và local mempool | Chọn và seal block hợp lệ | Không phải attacker chính; không giả định majority collusion |

Kiểm tra lại quyền builder bằng BEP-322 và implementation hiện hành trước khi khóa matrix.

## Visibility models

Tách ít nhất hai visibility models:

- `PUBLIC_ONLY`: actor chỉ biết public state và public order flow quan sát được.
- `BUILDER_RECEIVED`: builder biết các transaction/bundle đã nhận trực tiếp trước khi chốt candidate block.

Không ghi rằng public mempool đại diện cho toàn bộ order flow trên BSC.

## Scenario catalog

Mỗi scenario cần các trường:

```text
scenario_id
actor_model
visibility_model
rng_pattern
preconditions
allowed_actions
forbidden_actions
attacker_goal
canonical_run
counterfactual_run
success_condition
required_fields
rq_mapping
```

Scenario core:

1. Searcher prediction/timing.
2. Builder reorder với cùng transaction set.
3. Builder reorder và selective inclusion.
4. Cùng ba capability levels trên safe reference.

## Invariants

Mọi counterfactual run phải giữ:

- Cùng chain ID và parent/pre-state.
- Cùng contract code và initial storage.
- Cùng honest inputs, trừ transaction bị loại trong scenario selective inclusion.
- Thứ tự mới vẫn thỏa nonce và transaction dependency.
- Block không vượt gas limit và không chứa transaction invalid.
- Chỉ capability đang kiểm tra được thay đổi.

## Kết quả không được suy diễn

Replay chứng minh outcome khả thi dưới model, không chứng minh:

- Một builder lịch sử đã thực hiện attack.
- Searcher nhìn thấy private transaction.
- Builder có quyền sửa tùy ý timestamp hoặc block header.
- Một outcome local chắc chắn xuất hiện với cùng tần suất trên mainnet.

## Đầu ra

- `research/threat_model.md`
- `research/scenario_catalog.csv`
- `research/invariants.md`

## Tiêu chí hoàn thành

- Mỗi scenario có đúng một actor model và visibility model.
- Mỗi action đều xuất hiện trong capability matrix.
- Searcher scenario không reorder honest transaction.
- Reorg và validator collusion không xuất hiện trong scenario core.
- Success condition có thể kiểm tra tự động.

## Lỗi cần tránh

- Gộp builder và proposer vì cả hai liên quan tạo block.
- Tạo upper-bound attacker quá mạnh rồi mô tả kết quả như rủi ro thực tế.
- Không kiểm tra nonce/dependency khi sinh transaction order mới.

