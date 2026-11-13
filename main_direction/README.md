# Direction 1 — Builder-aware weak RNG on BSC

> **TOPIC CHÍNH ĐANG THỰC HIỆN**

Nghiên cứu đo lường thực nghiệm/an ninh về khả năng khai thác RNG on-chain yếu theo quyền của searcher và builder trên BNB Smart Chain. Nhóm dùng paired replay có kiểm soát để so sánh các nhánh canonical và counterfactual. Không huấn luyện machine-learning model, không classification hoặc regression.

## Trạng thái hiện tại

- Step 1–7: đã có thiết kế, dữ liệu khảo sát và replay harness.
- Step 8: đã revalidate bằng Foundry/Anvil fixture; **Revalidated**.
- Step 9: batch pre-experiment mới đã pass; pilot 100 context lịch sử vẫn giữ nguyên; **Revalidated**.
- Step 10: public-informed synthetic replay đã hoàn thành với 2.400 observations; **Complete**.
- Step 11: notebook phân tích paired replay, năm biểu đồ và báo cáo theo RQ đã hoàn thành; **Complete**.
- Step 12: chưa bắt đầu.
- [Progress log](./progress.md) ghi chi tiết gate, test và blocker hiện tại.
- [Pre-experiment checks](./research/pre_experiment_checks.md) lưu lịch sử các gate đã được xử lý trước Step 10.
- [Kế hoạch mở rộng hẹp](./research/public_rule_collection_plan.md) mô tả public-informed synthetic rules và hai hướng tùy chọn.

Pilot Step 8–9 chỉ chứng minh pipeline có thể chạy và tạo observation hợp lệ. Không dùng pilot để kết luận prevalence, historical attack, exploitability trên toàn BSC hoặc profitability.

**Mini-proposal:** [proposal_v2.md](./proposal_v2.md). Bản nộp độc lập theo template môn học.

**Giải thích cho người mới:** [overview_for_beginners.md](./overview_for_beginners.md). Bản diễn giải dễ hiểu về đề tài, cách làm và giới hạn kết luận.

**Chạy local:** xem [execution_guide.md](./execution_guide.md), rồi copy [`.env.example`](./.env.example) thành `.env` trước khi chạy crawl hoặc replay.

**Setup cho teammate:** Docker Compose đã có sẵn trong [docker-compose.yml](./docker-compose.yml). Xem [execution_guide.md](./execution_guide.md) để build image, chạy smoke test và validate output.

**Research detail:** [research_detail.md](./research_detail.md). Bản nháp trước đây mang tên `proposal.md`; giữ nguyên nội dung để tra cứu thiết kế, không phải proposal v1 được thầy feedback.

**Proposal v1 và feedback:** [mini-proposal.md](../direction_2_rejected/archive/mini-proposal.md), [feedback.md](../direction_2_rejected/archive/feedback.md).

Step 1–9 phục vụ thu hẹp thiết kế và kiểm tra tính khả thi. Step 10 chạy phần bổ sung public-informed synthetic, còn Step 11 phân tích paired outcomes và uncertainty. Các kết luận chỉ áp dụng cho workload đã replay; không phải bằng chứng về historical attack hoặc prevalence trên toàn BSC.

## Kế hoạch nghiên cứu từng bước

Bắt đầu từ [step_1_research_map.md](./step_1_research_map.md). Mỗi step có đầu vào, công việc, đầu ra và tiêu chí hoàn thành riêng.

| Step | File | Mục tiêu | Trạng thái |
| --- | --- | --- | --- |
| 1 | [Research map](./step_1_research_map.md) | Nắm toàn bộ luồng và quy tắc bằng chứng | Có artifact |
| 2 | [Lock scope and claims](./step_2_lock_scope_and_claims.md) | Khóa RQ, scope, thuật ngữ và claim register | Có artifact |
| 3 | [Review related work](./step_3_review_related_work.md) | Xây related-work matrix và research gap | Có artifact |
| 4 | [Define threat model](./step_4_define_threat_model.md) | Khóa actor, visibility và capabilities | Có artifact |
| 5 | [Specify experiment](./step_5_specify_experiment.md) | Khóa protocol, schema và analysis plan | Có artifact |
| 6 | [Crawl BSC contexts](./step_6_crawl_bsc_contexts.md) | Thu block contexts và kiểm tra RPC/finality | Có artifact |
| 7 | [Build replay harness](./step_7_build_replay_harness.md) | Chạy paired canonical/counterfactual replay | Có artifact |
| 8 | [Implement attack strategies](./step_8_implement_attack_strategies.md) | Cài ba capability levels và cost models | Revalidated |
| 9 | [Run pilot](./step_9_run_pilot.md) | Kiểm tra pipeline và quyết định go/no-go | Revalidated |
| 10 | [Collect full dataset](./step_10_collect_full_dataset.md) | Chạy cùng workload trên 1–2 public-informed synthetic rules; rule thật là tùy chọn | Complete |
| 11 | [Analyze results](./step_11_analyze_results.md) | Trả lời RQ-C1 đến RQ-C4 | Complete |
| 12 | [Write and release](./step_12_write_report_and_release.md) | Viết báo cáo và đóng gói artifact tái lập | Chưa bắt đầu |

| Path | Dùng để |
|---|---|
| [proposal_v2.md](./proposal_v2.md) | Bản proposal theo template: bài toán, RQ, dữ liệu chung, phương pháp và kế hoạch |
| [research_detail.md](./research_detail.md) | Bản nháp thiết kế Direction 1; nội dung được giữ để tra cứu |
| [analysis/step_11_results.ipynb](./analysis/step_11_results.ipynb) | Notebook Step 11 đã execute, gồm bảng trung gian và năm biểu đồ |
| [reports/team_meeting_report.md](./reports/team_meeting_report.md) | Báo cáo tổng kết phục vụ họp nhóm: phương pháp, kết quả, giới hạn và agenda Step 11B |
| [reports/results_by_rq.md](./reports/results_by_rq.md) | Kết quả và giới hạn kết luận theo RQ-C1 đến RQ-C4 |
| [research/](./research/) | Related work, threat model, protocol, schema và sampling/analysis plan |
| [reports/pilot_100_assessment.md](./reports/pilot_100_assessment.md) | Khảo sát khả năng lấy dữ liệu mainnet |
| [data/manifests/pilot_manifest.json](./data/manifests/pilot_manifest.json) | Thống kê run khảo sát pipeline local |
| [proposals/unused/work/](./proposals/unused/work/) | Làm sâu từng mục |
| [drafts/](./drafts/) | Bản review / detail rộng cũ — chỉ đọc |
| [proposals/unused/](./proposals/unused/) | Mini proposal lịch sử + work stubs |

Phương án cũ chỉ để tra cứu: [Direction 3 fallback](../direction_3_fallback/README.md). Mini-proposal hiện chỉ theo Direction 1.
