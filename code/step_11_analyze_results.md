# Step 11: Phân tích kết quả

## Trạng thái

`Complete` ngày 2026-10-10. Notebook đã chạy từ đầu đến cuối và lưu output tại
`analysis/step_11_results.ipynb`. Các bảng, biểu đồ và câu trả lời theo RQ nằm
trong `reports/tables/`, `reports/figures/` và `reports/results_by_rq.md`.

## Mục tiêu

Trả lời bốn RQ bằng phân tích ghép cặp, đồng thời giữ ranh giới giữa dữ liệu quan sát, replay và mô hình chi phí.

## Phân tích RQ-C1

Tạo capability matrix thực nghiệm:

- RNG pattern nào bị khai thác bởi searcher-only.
- Pattern nào chỉ thay đổi khi có reorder.
- Pattern nào cần selective inclusion.
- Preconditions và visibility model của từng kết quả.

Không gộp tất cả weak RNG thành một tỷ lệ duy nhất.

## Phân tích RQ-C2

Trên cùng context:

- So canonical với searcher-only.
- So searcher-only với builder reorder.
- So reorder với reorder plus selective inclusion.
- Báo cáo `delta_p_win`, `delta_ev` và capability uplift.

Dùng paired analysis. Báo effect size và uncertainty interval.

## Phân tích RQ-C3

Với từng RNG pattern, actor model và cost model:

- Tính `net_profit` theo prize grid.
- Xác định vùng break-even nếu tồn tại.
- Tách threshold dùng observed cost khỏi threshold dùng modeled opportunity cost.
- Chạy sensitivity analysis cho các cost component không quan sát được.

Không trình bày một threshold duy nhất như quy luật chung cho BSC.

## Phân tích RQ-C4

So weak RNG và safe reference trên cùng context:

- Chênh lệch exploitability.
- Chênh lệch attack success hoặc winning advantage.
- Chi phí/liveness phát sinh nếu protocol có đo.
- Residual risks nằm ngoài randomness primitive.

## Bảng và biểu đồ bắt buộc

1. Dataset coverage và failure reasons.
2. Capability matrix theo RNG pattern.
3. Paired effect plot cho `delta_p_win` hoặc `delta_ev`.
4. Net-profit curves theo prize và cost model.
5. Weak RNG so với safe reference trên cùng contexts.

Mỗi figure caption phải nêu evidence type và scope kết luận.

## Robustness checks

- Rerun với seed khác nếu strategy search dùng randomness.
- Kiểm tra kết quả theo context strata đã đăng ký.
- Kiểm tra ảnh hưởng của replay failures.
- So conclusion khi opportunity cost thay đổi.
- Tách confirmatory và exploratory findings.

### Độ nhạy theo số transaction liên quan

Workload hai transaction hiện tại là capability test tối thiểu. Nó đủ để
chứng minh rằng việc đổi thứ tự giữa một transaction honest và một transaction
attacker có thể làm thay đổi kết quả được decode. Nó không đủ để ước lượng độ
lớn hiệu ứng trong cạnh tranh thực tế hoặc suy rộng ra mọi transaction trong
một block.

Quy mô cần quan tâm là số transaction cùng cạnh tranh trong một workload,
không phải tổng số transaction của block. Không cần tái tạo transaction không
liên quan, trừ khi chúng tạo dependency, giới hạn gas hoặc tương tác state đã
được khai báo trong protocol.

Nếu còn thời gian, chạy một batch robustness mang nhãn `EXPLORATORY` với
`participant_count in {2, 5, 10}` trên cùng 100 contexts và các rule family
hiện có. Giữ nguyên capability definitions, canonical/counterfactual pairing,
seed, payoff decoder và validity checks. Lưu batch này riêng, không thay thế
hoặc gộp với batch Step 10 đã hoàn thành.

Với mỗi participant count, báo cáo:

- attacker win rate ở canonical và manipulated branch;
- paired `delta_p_win` kèm khoảng tin cậy 95%;
- winner-change rate;
- validity rate và failure rate;
- builder có tìm được một valid order có lợi theo strategy đã khai báo hay
  không.

Nếu không chạy batch robustness này, báo cáo cuối phải giữ rõ giới hạn hai
transaction và không được diễn giải kết quả thành độ lớn hiệu ứng thực tế.

## Ngôn ngữ kết luận

Dùng:

> Trong các context và capability models đã replay, strategy X đạt outcome Y.

Không dùng:

> Builder BSC đang thực hiện attack X.

trừ khi có dữ liệu quan sát trực tiếp bổ sung và phương pháp attribution phù hợp.

## Đầu ra

- `analysis/step_11_results.ipynb`: notebook có output đã render.
- `analysis/step_11_analysis.py`: phép tính và export có thể chạy độc lập.
- `analysis/analysis_manifest.json`: input hashes, seed và dependency versions.
- `reports/results_by_rq.md`: câu trả lời RQ-C1 đến RQ-C4.
- `reports/figures/` và `reports/tables/`: năm biểu đồ và các bảng CSV.
- `reports/robustness_checks.md`: uncertainty và giới hạn kết luận.

## Tiêu chí hoàn thành

- Mỗi RQ có một subsection kết quả và một câu trả lời ngắn.
- Mỗi số trong báo cáo truy ngược được đến dataset version và analysis code.
- Modeled cost không xuất hiện trong bảng measured results nếu không gắn nhãn.
- Negative result và replay failure được báo cáo.
- Kết luận không vượt quá threat model hoặc sampling frame.

## Lỗi cần tránh

- Chỉ báo mean khi phân phối lệch mạnh.
- Chọn figure sau khi thử nhiều biến thể nhưng không ghi exploratory.
- Diễn giải statistical significance như economic significance.
