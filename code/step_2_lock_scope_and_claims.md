# Step 2: Khóa phạm vi và các claim

## Mục tiêu

Chuyển nội dung trong `research_detail.md` thành một protocol ngắn, không còn thuật ngữ mơ hồ hoặc nhánh nghiên cứu ngoài scope.

## Đầu vào

- `research_detail.md`
- `step_1_research_map.md`
- Các draft cũ chỉ dùng để kiểm tra lịch sử quyết định, không tự động đưa trở lại scope.

## Công việc

### 1. Khóa đối tượng nghiên cứu

Ghi rõ:

- Chain thực nghiệm: BNB Smart Chain mainnet, dùng finalized block context.
- Đối tượng: weak RNG dựa trên block/transaction context trong ứng dụng có payoff.
- Attack core: prediction/timing, reorder và selective inclusion.
- Safe reference: chọn một cơ chế chính để so sánh. Ưu tiên cơ chế chạy được trên cùng replay harness.
- Actor chính: searcher và builder. Proposer được mô tả để đúng kiến trúc, không dùng làm attacker chính.

### 2. Khóa phần ngoài phạm vi

Không đưa trở lại nghiên cứu chính:

- Multi-block reorg, majority collusion hoặc consensus attack.
- Benchmark tổng quát Pseudo-RNG, Commit-Reveal và VRF về gas/latency.
- Selective abort và bài toán tối ưu deposit.
- Quét prevalence toàn BSC.
- Arbitrage hoặc sandwich không liên quan weak RNG.
- Thiết kế một RNG protocol mới.

### 3. Chuẩn hóa thuật ngữ

Tạo glossary cho ít nhất các từ sau:

- weak RNG
- block context
- canonical order
- manipulated order
- selective inclusion
- searcher
- builder
- proposer
- exploitability
- economic viability
- safe reference

Mỗi thuật ngữ phải có định nghĩa dùng được trong code và dữ liệu. Ví dụ, `replay_success` phải có điều kiện boolean cụ thể, không chỉ là mô tả bằng văn xuôi.

### 4. Lập claim register

Tạo bảng có các cột:

```text
claim_id,claim_text,claim_type,required_evidence,status,source_or_artifact
```

Các claim ban đầu cần đăng ký:

- Builder có quyền chọn transaction set/order trong mô hình BSC builder.
- Weak RNG có thể tạo lợi thế trong một số capability models.
- Builder capability tạo thêm exploitability so với searcher-only.
- Có một prize threshold làm `net_profit` đổi dấu dưới từng cost model.
- Safe reference giảm exploitability trong cùng context.

Claim chưa đo phải có trạng thái `HYPOTHESIS`, không viết như kết quả.

### 5. Chốt ethical boundary

- Chỉ đọc mainnet và replay local/fork.
- Không gửi attack transaction lên mainnet.
- Không công bố private endpoint, credential hoặc dữ liệu chưa được phép chia sẻ.
- Nếu phát hiện contract đang hoạt động có rủi ro cụ thể, tách responsible disclosure khỏi báo cáo môn học.

## Đầu ra

- `research/protocol.md`
- `research/glossary.md`
- `research/claims_register.csv`
- `research/decision_log.md`

## Tiêu chí hoàn thành

- Mỗi RQ có một câu diễn giải đo được.
- Không còn cụm từ gộp actor như `bot/validator`.
- Mọi claim định lượng đang ở trạng thái hypothesis hoặc có nguồn dữ liệu.
- Safe reference chính đã được chọn hoặc có decision gate cụ thể ở Step 5.
- Scope không chứa reorg, deposit sweep hoặc three-RNG benchmark.

## Lỗi cần tránh

- Đổi RQ sau khi xem kết quả mà không ghi vào decision log.
- Dùng `builder` và `proposer` như cùng một vai trò.
- Gọi một contract là exploitable khi mới chỉ nhận diện source pattern.
