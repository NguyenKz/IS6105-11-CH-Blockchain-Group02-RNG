# Kiểm tra cần hoàn tất trước thí nghiệm chính

Tài liệu nội bộ, không thuộc mini-proposal nộp môn học. Ghi lại các vấn đề phát hiện khi đối chiếu code và artifacts khảo sát; chưa sửa code hoặc chạy lại thí nghiệm trong bước biên tập tài liệu.

### 2.3. Các điều kiện còn cần kiểm chứng

Nhóm chưa dùng các tuyên bố PASS tổng hợp trong pilot report để thay thế kiểm chứng nghiên cứu. Đọc code hiện có xác định các điều kiện sau:

1. Builder reorder hiện chọn permutation cuối theo lexicographic; với cặp `honest`, `attacker`, order đó trùng canonical. Cần chứng minh candidate alternative thực sự được thực thi và strategy không thay input ngoài capability reorder.
2. Input trong weak fixture ảnh hưởng event `attackerWon`, nhưng winner được gán theo vị trí. Cần thống nhất outcome decoder với payoff rule; chưa thể lấy fixture này làm bằng chứng searcher-input advantage.
3. Reference nhận pinned block hash ở constructor trước commit; mới kiểm tra được commitment trước `play`, chưa chứng minh commitment trước khi biết entropy. Cần kiểm chứng thứ tự thông tin và participant/payoff comparability trước RQ-C4.
4. Nonce, gas-limit và một số validity flags đang được đặt sẵn trong strategy generator. Nghiên cứu chính phải tính từ giao dịch, state và receipts; snapshot restore cần evidence về cùng pre-state, không chỉ một flag.
5. Evidence bundle phải chứa cả canonical và counterfactual receipts/events/traces. Schema hiện không biểu diễn `net_profit` âm; cần thống nhất biểu diễn số có dấu trước phân tích hòa vốn.

Đây là điều kiện hoàn thiện phương pháp đã chọn, không phải các hướng nghiên cứu mới. Chưa sửa code hoặc chạy lại dữ liệu trong lần viết proposal này.

## Provenance của run khảo sát

Commit đóng gói pilot là `282cb4a`. Manifest hiện ghi `74926d6` là HEAD khi chạy, nhưng runner/fixture Step 8–9 lúc đó còn chưa commit. Khi chạy nghiên cứu chính phải dùng code đã đóng băng, ghi đúng phiên bản và giữ riêng manifest pilot này.
