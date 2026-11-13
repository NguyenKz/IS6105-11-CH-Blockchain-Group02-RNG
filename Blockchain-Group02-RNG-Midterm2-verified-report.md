---
title: "Phân tích khả năng khai thác RNG on-chain yếu theo năng lực searcher và builder trên BNB Smart Chain"
subtitle: "Báo cáo giữa kỳ cập nhật — kết quả verified public-informed synthetic replay"
author: |
  Nhóm 02 — OnChainRNG\\
  Bùi Thái Hoàng (250104008), Trần Thảo Nguyên (250101049),\\
  Nguyễn Duy Trọng Nhân (250104048), Nguyễn Phi Yến (250104059)\\
  Môn: Công nghệ Blockchain, IS6105.11.CH\\
  Giảng viên: Trần Hưng Nghiệp
date: "09/2026 — 11/2026"
lang: vi-VN
geometry: margin=2.2cm
fontsize: 10.5pt
toc: true
toc-depth: 2
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{array}
  - \usepackage{graphicx}
  - \usepackage{float}
  - \usepackage{xcolor}
  - \usepackage{hyperref}
---

# Tóm tắt

Đây là nghiên cứu đo lường thực nghiệm/an ninh, không huấn luyện mô hình học máy. Nhóm dùng **paired replay** có kiểm soát để so sánh cùng một pre-state dưới nhánh canonical và counterfactual, qua đó đo ảnh hưởng của các quyền searcher và builder lên một workload RNG có thưởng.

Bản nộp này chỉ sử dụng artifact đã kiểm chứng trong workspace: 100 context BSC, 2.400 observation rows, sáu scenario và bốn cost model trên hai synthetic rule family có public-informed provenance. Kết quả chính là: searcher-only không làm thay đổi winner trong workload đã chạy; Fomo3D-inspired adapter có point estimate `delta_p_win = +0,080` cho builder reorder và declared selective inclusion, nhưng khoảng 95% `[-0,120; +0,280]` chứa 0; Dice2Win-inspired commit-before-entropy có `delta_p_win = 0`. Các con số này là kết quả **REPLAYED/DERIVED** trên synthetic adapter, không phải bằng chứng một actor lịch sử trên BSC đã tấn công và không ước lượng profitability thực tế.

## Trạng thái bằng chứng

| Nhãn | Ý nghĩa trong báo cáo |
|---|---|
| **OBSERVED** | Context, block metadata, receipt hoặc dữ liệu nguồn đọc được từ BSC qua pipeline đã lưu. |
| **REPLAYED** | Thực thi local trên Foundry/Anvil fork với pre-state và snapshot được kiểm soát. |
| **MODELED** | Prize, bid/bribe và opportunity-cost assumptions dùng cho sensitivity. |
| **DERIVED** | Metric tính từ observation rows và paired outcomes. |
| **HYPOTHESIS** | Giả thuyết cần kiểm tra, không phải kết luận. |

# 1. Mini Problem Formulation

Các lottery/game on-chain cần randomness công bằng vì kết quả quyết định phân phối phần thưởng. Nếu randomness phụ thuộc vào dữ liệu công khai hoặc thứ tự giao dịch, người chơi có thể dự đoán hoặc tác động đến kết quả. Searcher và builder có quyền khác nhau: searcher chỉ điều chỉnh giao dịch của mình trong phạm vi thông tin công khai, còn builder có thể sắp xếp hoặc loại transaction hợp lệ trong tập đã nhận. Nghiên cứu đo mức ảnh hưởng của từng capability, điều kiện hòa vốn theo cost model đã khai báo, và mức giảm ảnh hưởng của commit-before-entropy.

Phạm vi là workload synthetic có thưởng do nhóm xây dựng, chạy trên context block finalized của BSC và thực thi giao dịch thử nghiệm trên local fork. Không xét reorg, thông đồng validator, giả chữ ký, sửa finalized header, private order flow, historical attack hoặc ứng dụng thật. `BUILDER_RECEIVED` là giả định thực nghiệm về tập transaction builder đã nhận, không phải dữ liệu private flow quan sát được trên mainnet.

## Research questions

- **RQ-C1:** Trong workload đã khai báo, searcher và builder có thể dự đoán hoặc ảnh hưởng RNG yếu bằng capability nào?
- **RQ-C2:** Reorder và selective inclusion thay đổi xác suất thắng và giá trị kỳ vọng bao nhiêu so với canonical/searcher-only?
- **RQ-C3:** Với chi phí thực thi và giả định chi phí đã nêu, điều kiện hòa vốn của từng strategy là gì?
- **RQ-C4:** Commit-before-entropy thay đổi mức ảnh hưởng của các strategy thế nào?

## Hypotheses

H1: Một số pattern RNG bị ảnh hưởng bởi capability đã khai báo. H2: Builder có thể tạo ảnh hưởng bổ sung so với searcher trong workload phù hợp. H3: Có thể tính điều kiện hòa vốn khi `delta_p_win > 0` theo cost model. H4: Commit-before-entropy giảm ảnh hưởng của ordering.

# 2. Related Work

| Nguồn | Đóng góp liên quan | Khoảng trống đối với đề tài |
|---|---|---|
| Qian et al. [1] | Taxonomy weak RNG và phát hiện lỗi/giao dịch tấn công trên Ethereum. | Chưa so sánh paired replay theo quyền builder trên BSC. |
| Yakira et al. [2] | Secrecy, robustness và động cơ kinh tế của distributed commit-reveal. | Chưa đo riêng ordering/inclusion trong workload BSC. |
| Daian et al. [3]; Torres et al. [4] | Transaction ordering, MEV và frontrunning. | Không trực tiếp đo weak RNG cùng randomness reference. |
| BNB Chain [5, 6] | Cơ sở phân biệt searcher, builder và proposer trên BSC. | Là tài liệu kiến trúc, không phải kết quả đo RNG. |
| Wang et al. [7] | Builder-driven MEV arbitrage trên BSC. | Đối tượng là arbitrage, không phải winner/payoff của RNG game. |

Đóng góp của nhóm là một phép đo capability-aware, paired và có snapshot restore. Kết luận chỉ áp dụng cho workload đã replay.

# 3. Experimental Plan

## 3.1 Dataset và pipeline

### Dữ liệu nguồn và khảo sát khả thi

| Thành phần | Quy mô đã kiểm chứng | Vai trò |
|---|---:|---|
| Context BSC mainnet | 100 finalized blocks, block 125053984–125054083, chain ID 56 | Cung cấp block context/pre-state cho local replay. |
| Giao dịch và receipts | 11.070 transactions | Kiểm tra pipeline thu thập và coverage. |
| Historical code/call/trace | 1 candidate transaction | Preflight; chưa chứng minh coverage cho mọi context. |
| Public-informed synthetic replay | 100 contexts × 6 scenarios × 4 cost models = 2.400 observations | Dataset kết quả đã kiểm chứng của bản nộp. |

Observation được định danh bởi `context_id + scenario_id + seed + cost_model_id`. Các scenario và cost model dùng chung context nên 2.400 rows không phải 2.400 mẫu độc lập.

Pipeline:

1. Khóa block range, seed, workload và source block hashes.
2. Thu block/receipt và lưu raw response, checksum cùng RPC identifier.
3. Tạo `context_id` và xác định `pre_state_block`.
4. Fork state trước source block và chạy synthetic contract trên local Anvil.
5. Chạy canonical, restore snapshot, rồi chạy counterfactual với đúng pre-state.
6. Lưu input, order, omission, event, receipt, trace, invariant và strategy trace.
7. Validate theo schema; giữ failure cùng stage/reason thay vì đổi thành zero outcome.

### Rule families và provenance

- `FOMO3D_PUBLIC_CONTEXT_HASH_MODULO` — synthetic adapter, mapping `MAP-FOMO3D-PUBLIC-CONTEXT`, provenance status `CONFIRMED` cho public-informed mechanism mapping.
- `DICE2WIN_COMMIT_BLOCKHASH` — synthetic adapter, mapping `MAP-DICE2WIN-COMMIT-BLOCKHASH`, deployed linkage vẫn `RULE_UNCONFIRMED`.

Các tên family không có nghĩa nhóm đã replay deployed application contract. `Fomo3dInspiredGame.sol` và `Dice2WinInspiredGame.sol` là fixture dùng để giữ cơ chế cần đo trong môi trường kiểm soát.

## 3.2 Threat model và capability boundary

| Actor | Visibility | Quyền trong replay |
|---|---|---|
| Searcher | `PUBLIC_ONLY` | Chỉ thay input/timing transaction của mình; không đổi order/inclusion của honest transactions. |
| Builder | `BUILDER_RECEIVED` | Reorder transaction hợp lệ hoặc omit candidate đã khai báo trước; không forge signature, sửa header hay tạo state invalid. |
| Proposer | Kiến trúc BSC | Không phải attacker được đo trong thí nghiệm. |

Strategy phải quyết định từ thông tin có trước execution. Không đọc post-execution outcome để chọn hành động. Với workload hai transaction, strategy xét các permutation hợp lệ; không gọi kết quả là global optimum.

## 3.3 Evaluation protocol và metrics

Canonical và counterfactual phải giữ cùng context, code, storage, participant set, workload, seed và honest inputs. Trước khi chạy, kiểm tra snapshot restoration, nonce/dependency, gas limit, outcome decoder và capability. Commitment của reference phải cố định trước entropy.

Với `W_i` là win flag và `V` là prize:

```text
p_win = mean(W_i)
delta_p_win = mean(W_i(counterfactual) - W_i(canonical))
expected_payout = p_win × V
net_profit = incremental_expected_payout - transaction_cost
             - bid_or_bribe - opportunity_cost
break_even_prize = total_cost / delta_p_win, nếu delta_p_win > 0
```

Transaction fee lấy từ local receipt và được gắn nhãn `REPLAYED`. Bid/bribe bằng 0 và opportunity cost là `MODELED`; bốn model được dùng là `FEE_ONLY`, `OPPORTUNITY_LOW`, `OPPORTUNITY_BASE`, `OPPORTUNITY_HIGH`. Uncertainty được báo bằng paired bootstrap 95% interval theo context. Failure không được coi là attacker thua.

## 3.4 Baselines, ablation và experiment specification

- **B0:** Weak context RNG, canonical order, attacker input cố định.
- **B1:** Searcher-only trên weak RNG.
- **Reference:** Commit-before-entropy, giữ participant set và payoff rule tương ứng.
- **Ablation:** loại reorder; loại selective inclusion; thay opportunity-cost model; so sánh weak với reference.

| Experiment | Mục tiêu | Dataset thực tế trong bản nộp |
|---|---|---|
| E0/Baseline | Kiểm tra pipeline, evidence và safe reference. | 100 contexts, `VERY_SIMPLE_RULES`, 2.400 rows pilot/pre-validation. |
| E1/Public-informed synthetic | Đo capability trên hai rule families. | 100 contexts, 2.400 observations, hoàn thành. |
| E2/Economic sensitivity | Tính break-even theo cost models. | Được tính từ E1; bid/opportunity cost là modeled. |
| E3/Confirmatory holdout | Replicate trên 1.000 holdout contexts. | Chưa chạy, không đưa kết quả vào kết luận. |
| E4/Participant robustness | So sánh 2/5/10 participants. | Chưa chạy, không đưa kết quả vào kết luận. |

# 4. Verified Experimental Results

## 4.1 Data integrity

Manifest của batch cho biết 100 successful contexts, 0 failed contexts, 2.400 observations, 600 invariant rows, 600 strategy traces, 2.500 receipts, 2.500 traces và 2.500 event rows. Validation theo `bsc_rng_mev_replay.schema.json` đạt `PASS` với 2.400 observations.

![Dataset coverage và run summary.](../main_direction/reports/figures/01_dataset_coverage.png)

## 4.2 Baseline và preliminary public-informed results

| Rule family | Capability | Canonical win rate | Manipulated win rate | `delta_p_win` | 95% interval |
|---|---:|---:|---:|---:|---:|
| Fomo3D-inspired | Searcher-only | 0,460 | 0,460 | 0,000 | [0,000; 0,000] |
| Fomo3D-inspired | Builder reorder | 0,460 | 0,540 | +0,080 | [-0,120; +0,280] |
| Fomo3D-inspired | Selective inclusion | 0,460 | 0,540 | +0,080 | [-0,120; +0,280] |
| Dice2Win-inspired | Searcher-only | 0,510 | 0,510 | 0,000 | [0,000; 0,000] |
| Dice2Win-inspired | Builder reorder | 0,510 | 0,510 | 0,000 | [0,000; 0,000] |
| Dice2Win-inspired | Selective inclusion | 0,510 | 0,510 | 0,000 | [0,000; 0,000] |

Trên Fomo3D-inspired adapter, builder reorder và selective inclusion thay đổi winner trong các pair đã chạy nhưng point estimate không đủ để xác nhận lợi thế ổn định vì interval chứa 0. Searcher-only không thay đổi decoded winner. Trên Dice2Win-inspired adapter, commit-before-entropy giữ nguyên mapping winner trước và sau replay.

![Capability matrix.](../main_direction/reports/figures/02_capability_matrix.png)

![Paired delta và khoảng bất định.](../main_direction/reports/figures/03_paired_delta_ci.png)

## 4.3 Economic sensitivity

Với Fomo3D-inspired builder reorder, `delta_p_win = 0,080` được dùng như point estimate để tính sensitivity. Đây là **MODELED/DERIVED**, không phải bằng chứng profitability thực tế.

| Cost model | Mean total cost (wei) | Break-even prize (BNB) |
|---|---:|---:|
| `FEE_ONLY` | 58.220.900.000.000 | 0,000728 |
| `OPPORTUNITY_LOW` | 116.441.800.000.000 | 0,001456 |
| `OPPORTUNITY_BASE` | 174.662.700.000.000 | 0,002183 |
| `OPPORTUNITY_HIGH` | 291.104.500.000.000 | 0,003639 |

Nếu delta thực sự không dương thì không có break-even prize hữu hạn theo công thức này. Vì interval của delta chứa 0, bảng chỉ là sensitivity theo giả định chi phí.

![Net profit sensitivity.](../main_direction/reports/figures/04_net_profit_sensitivity.png)

## 4.4 Weak versus safe reference

Commit-before-entropy adapter cho `delta_p_win = 0` dưới các capability đã chạy. Điều này phù hợp với cơ chế: participant index được khóa trong commit phase trước khi entropy được finalize, nên reorder ở play phase không đổi mapping. Kết luận chỉ áp dụng cho synthetic adapter; deployed Dice2Win linkage là `RULE_UNCONFIRMED`.

![Weak RNG versus safe reference.](../main_direction/reports/figures/05_weak_vs_safe.png)

# 5. Comparison and Answers to RQ

| RQ | Kết quả đã kiểm chứng | Giới hạn |
|---|---|---|
| RQ-C1 | Searcher-only không đổi winner trong batch; builder capability đổi outcome trên Fomo3D-inspired adapter. | Controlled synthetic replay, không phải historical actor behavior. |
| RQ-C2 | Fomo3D-inspired builder point estimate `+0,080`; Dice2Win-inspired `0,000`. | Interval Fomo3D chứa 0; effect phụ thuộc workload/strategy. |
| RQ-C3 | Có thể tính break-even sensitivity khi dùng point estimate dương. | Fee replayed; bid và opportunity cost modeled; không chứng minh profitability. |
| RQ-C4 | Commit-before-entropy giữ `delta_p_win = 0` trong adapter. | Deployed linkage chưa confirmed; không suy rộng sang mọi protocol. |

![Summary comparison.](../main_direction/reports/figures/02_capability_matrix.png)

## Interpretation

Kết quả phân biệt hai điều thường bị trộn lẫn: capability có thể làm winner thay đổi, nhưng chưa chắc tạo lợi thế ròng. Trong Fomo3D-inspired adapter, builder có thể thay đổi mapping participant/position khi strategy chọn order theo public context; searcher không có quyền đó. Trong reference adapter, participant identity được commit trước entropy nên ordering ở play phase không tạo kênh ảnh hưởng đã đo.

# 6. Limitations, Missing Runs and Academic Integrity

1. 100 contexts là batch đã hoàn thành, không phải bằng chứng đủ để suy rộng prevalence hoặc all-block behavior.
2. Hai rule family là synthetic adapters; không gọi chúng là deployed application replay.
3. `BUILDER_RECEIVED` là assumption của threat model, không phải private order flow trên mainnet.
4. Selective inclusion chưa có đánh giá liveness đầy đủ trong batch này.
5. Các số break-even dùng point estimate và cost assumptions; không phải observed prize, bid hay historical profit.
6. Confirmatory holdout 1.000 contexts và participant robustness 2/5/10 chưa chạy trong workspace, nên không được trình bày như kết quả.
7. Slide deck và speaker script không có trong artifact hiện tại; bản ZIP ghi rõ trạng thái này thay vì tạo file giả.
8. Không đưa API key, private RPC URL, credential hoặc private order flow vào package.

# 7. Reproducibility and Submission Contents

Các artifact chính:

- `main_direction/data/derived/public_informed_synthetic/observations.jsonl`
- `main_direction/data/manifests/public_informed_synthetic_manifest.json`
- `main_direction/data/derived/public_informed_synthetic/validation_output.json`
- `main_direction/scripts/replay/run_public_informed.py`
- `main_direction/scripts/replay/validate_result.py`
- `main_direction/scripts/replay/test_public_informed.py`
- `main_direction/analysis/step_11_analysis.py`
- `main_direction/analysis/step_11_results.ipynb`
- `main_direction/reports/results_by_rq.md`
- `main_direction/reports/tables/`
- `main_direction/reports/figures/`
- `main_direction/repro_check_public_informed_results.zip`

Lệnh validation từ `main_direction/`:

```bash
source ../../venv/bin/activate
python scripts/replay/test_public_informed.py
python scripts/replay/validate_result.py \
  --self-test \
  --schema research/schema/bsc_rng_mev_replay.schema.json
python scripts/replay/validate_result.py \
  --input data/derived/public_informed_synthetic/observations.jsonl \
  --schema research/schema/bsc_rng_mev_replay.schema.json
```

Mainnet chỉ được đọc. Replay chạy local/forked chain. Khi cần crawl/replay mới, tạo `.env` từ `.env.example` và điền secret local; không commit `.env`.

# 8. Timeline and Next Work

| Giai đoạn | Công việc | Trạng thái |
|---|---|---|
| Tuần 1–4 | Literature, RQ, scope, data feasibility | Hoàn thành |
| Tuần 5–6 | Fixture, capability boundary, schema, replay harness | Hoàn thành |
| Tuần 7–8 | Public-informed synthetic replay và evidence | Hoàn thành |
| Tuần 9–10 | Paired analysis, uncertainty, cost sensitivity | Hoàn thành cho batch 100 contexts |
| Tuần 11–12 | Báo cáo, artifact package, presentation | Bản nộp này hoàn thành; slide deck chưa có |
| Sau giữa kỳ | Confirmatory holdout/participant robustness nếu được phê duyệt | Chưa chạy |

# References

1. Qian, P., et al. (2023). *Demystifying Random Number in Ethereum Smart Contract: Taxonomy, Vulnerability Identification, and Attack Detection*. arXiv:2304.12645.
2. Yakira, D., Asayag, A., Grayevsky, I., & Keidar, I. (2020). *Economically Viable Randomness*. arXiv:2007.03531.
3. Daian, P., et al. (2019). *Flash Boys 2.0: Frontrunning, Transaction Reordering, and Consensus Instability in Decentralized Exchanges*. arXiv:1904.05234.
4. Torres, C. F., Camino, R., & State, R. (2021). *Frontrunner Jones and the Raiders of the Dark Forest*. USENIX Security 2021.
5. BNB Chain (2023). *BEP-322: Builder API Specification for BNB Smart Chain*.
6. BNB Chain. *BSC MEV Overview*.
7. Wang, Q., Li, R., Yu, G., Gramoli, V., & Chen, S. (2026). *MEV in Binance Builder*. arXiv:2602.15395v2.

