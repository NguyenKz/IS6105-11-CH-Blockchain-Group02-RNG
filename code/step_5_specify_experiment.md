# Step 5: Đặc tả thí nghiệm và dataset

## Mục tiêu

Viết protocol đủ chi tiết để chạy lại mà không phải quyết định thêm sau khi đã nhìn thấy kết quả.

## Đơn vị phân tích

Một observation là một lần chạy scenario trên một `context_id`:

```text
observation = block context + rng pattern + actor capability + strategy + cost model
```

Canonical và counterfactual phải được ghép cặp bằng cùng `context_id`.

## Chọn RNG patterns

Khóa một tập nhỏ đại diện cho các nguồn yếu khác nhau, ví dụ:

- Entropy đã biết trước lúc gửi transaction.
- Entropy phụ thuộc transaction sender/order.
- Entropy chịu ảnh hưởng của block construction context.

Không thêm pattern chỉ để tăng số lượng. Mỗi pattern phải có liên hệ với paper, vulnerability class hoặc contract pattern đã ghi trong Related Work.

## Chọn safe reference

Decision gate:

- Chọn `commit-before-entropy` nếu cần replay hoàn toàn deterministic và không phụ thuộc oracle.
- Chọn VRF nếu nhóm có thể mô hình đúng request/fulfillment và không dùng mock randomness như bằng chứng về security của VRF.
- Có thể giữ một cơ chế làm primary reference và cơ chế còn lại làm supplementary experiment.

Quyết định phải ghi lý do trong `research/decision_log.md`.

## Biến và metrics

### Biến độc lập

- `rng_pattern`
- `actor_model`
- `visibility_model`
- `ordering_strategy`
- `selective_inclusion`
- `prize_native`
- `cost_model_id`
- `safe_reference`

### Metrics chính

```text
p_win = wins / valid_replays
delta_p_win = p_win_manipulated - p_win_canonical
expected_payout = p_win * prize_native
incremental_expected_payout = expected_payout_manipulated - expected_payout_canonical
net_profit = incremental_expected_payout
             - attacker_tx_cost
             - explicit_bid_or_bribe
             - opportunity_cost
capability_uplift = metric_builder - metric_searcher
```

Mỗi thành phần chi phí phải có evidence label. Thành phần không quan sát được phải là `MODELED` và chạy sensitivity analysis.

## Dataset schema

Dùng schema trong `research_detail.md` làm lõi và bổ sung:

```text
schema_version
run_id
seed
source_rpc_id
source_block_hash
pre_state_block
evidence_label_tx_cost
evidence_label_bid
evidence_label_opportunity_cost
failure_reason
code_commit
created_at_utc
```

## Kế hoạch lấy mẫu

- Pilot dùng khoảng 100 finalized block contexts như proposal đã đặt ra.
- Full-run sample size chỉ khóa sau pilot, dựa trên replay success, variance và ngân sách RPC/compute.
- Cách chọn block phải viết trước khi chạy full experiment, ví dụ random sample từ một window đã khóa hoặc stratified sample theo observable context.
- Không chọn lại block vì outcome không đẹp.

## Kế hoạch thống kê

- Báo cáo số valid/failed replay và lý do fail.
- Dùng paired differences vì canonical và manipulated run chung context.
- Báo cáo effect size cùng uncertainty interval, không chỉ p-value.
- Với prize threshold, báo cáo theo từng cost model và sensitivity range.
- Tách confirmatory analysis đã đăng ký khỏi exploratory analysis phát sinh sau pilot.

## Đầu ra

- `research/experiment_protocol.md`
- `research/data_dictionary.md`
- `research/sampling_plan.md`
- `research/analysis_plan.md`
- `research/schema/bsc_rng_mev_replay.schema.json`

## Tiêu chí hoàn thành

- Mỗi RQ ánh xạ được đến biến, metric và output table/figure.
- Mỗi field có type, unit, nullable rule và evidence label.
- Canonical/counterfactual pairing có khóa duy nhất.
- Failure không bị xóa khỏi dữ liệu.
- Sampling và analysis plan được khóa trước full run.

## Lỗi cần tránh

- Dùng prize sweep để thay cho dữ liệu chi phí thực.
- Trộn BNB, wei, gwei hoặc USD mà không lưu unit và conversion source.
- So hai capability levels trên hai tập context khác nhau.

## Phạm vi bổ sung đã khóa

Pre-experiment validation dùng `VERY_SIMPLE_RULES` làm baseline method.
Public-informed synthetic evaluation chỉ thay rule mechanism bằng 1–2 family
được mapping từ khoảng 3 public projects; workload, context, capability,
participant count, seed và analysis giữ nguyên. Replay trên tối đa một rule
thật là tùy chọn, còn suy đoán rule từ context chỉ là future work.
