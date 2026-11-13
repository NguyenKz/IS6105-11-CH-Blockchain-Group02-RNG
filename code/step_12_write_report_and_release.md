# Step 12: Viết báo cáo và đóng gói artifact

## Mục tiêu

Biến protocol, dataset và analysis thành báo cáo có claim vừa đủ và artifact mà người khác có thể kiểm tra.

## Cấu trúc báo cáo

1. Introduction và research problem.
2. BSC builder background cần thiết cho threat model.
3. Related Work và gap.
4. Threat Model.
5. Dataset và provenance.
6. Replay methodology.
7. Economic model.
8. Results theo RQ-C1 đến RQ-C4.
9. Robustness checks.
10. Limitations và threats to validity.
11. Ethics.
12. Conclusion.

Background chỉ giữ nội dung cần để hiểu method. Không quay lại kiểu liệt kê mọi RNG mechanism.

## Claim audit

Đối chiếu từng claim trong `research/claims_register.csv`:

- `SUPPORTED`: có artifact trực tiếp.
- `PARTIALLY_SUPPORTED`: chỉ đúng trong một subset/model.
- `NOT_SUPPORTED`: dữ liệu không xác nhận.
- `OUT_OF_SCOPE`: không còn thuộc protocol.

Xóa hoặc hạ mức mọi claim không được dữ liệu hỗ trợ.

## Threats to validity

Ít nhất phải bàn:

- Construct validity của weak RNG patterns và safe reference.
- Internal validity của replay harness.
- External validity từ sampled contexts đến BSC rộng hơn.
- Sai lệch do private order flow không quan sát được.
- Hạn chế của modeled bid/opportunity cost.
- Khác biệt giữa capability counterfactual và hành vi lịch sử.

## Gói tái lập

Artifact cần có:

- README chạy lại từ môi trường sạch.
- Toolchain và dependency versions.
- Sample config không chứa secret.
- One-command hoặc documented sequence để tái lập một context.
- Data dictionary, schema và manifests.
- Analysis script tạo lại bảng/figure.
- License cho code và dữ liệu do nhóm tạo.

Nếu raw data không thể phát hành do kích thước hoặc điều khoản provider, phát hành manifest, hashes và script crawl để tái tạo.

## Kiểm tra cuối

- Chạy reproduction smoke test trên một máy hoặc môi trường sạch.
- Kiểm tra link nội bộ và file path.
- Kiểm tra không có API key, private URL hoặc secret.
- Kiểm tra figure/table number khớp phần tham chiếu.
- Kiểm tra mọi con số có source hoặc evidence label.
- Kiểm tra không còn claim `first`, `100% exploitable` hoặc threshold tuyệt đối nếu dữ liệu không chứng minh.

## Đầu ra

- Báo cáo cuối.
- Artifact README.
- Dataset release hoặc reproduction manifest.
- Code và analysis package.
- Slide/demo nếu môn học yêu cầu.

## Tiêu chí hoàn thành

- Người đọc trả lời được ai có capability gì và dữ liệu chứng minh điều gì.
- Một reviewer tái lập được ít nhất một replay context.
- Bốn RQ có câu trả lời cùng scope với protocol.
- Claims register không còn item chưa xử lý.
- Báo cáo tách rõ observed, replayed, modeled và derived results.

## Lỗi cần tránh

- Viết kết luận trước rồi chọn bảng hỗ trợ.
- Giấu negative result hoặc pipeline limitation.
- Gọi dataset derived replay là dữ liệu attack thực tế.

