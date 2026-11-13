# Step 3: Khảo sát nghiên cứu liên quan

## Mục tiêu

Xây research gap từ bằng chứng, không dựa trên nhận định chung rằng chưa ai nghiên cứu vấn đề này.

## Câu hỏi khảo sát

1. Công trình nào phân loại hoặc phát hiện weak randomness trong smart contract?
2. Công trình nào đo front-running, transaction ordering hoặc MEV?
3. Công trình nào mô tả builder/proposer model trên BSC?
4. Có công trình nào kết hợp weak RNG, actor-specific capability, BSC context và economic threshold không?

## Phạm vi tìm kiếm

Ưu tiên nguồn gốc:

- Paper từ IEEE, USENIX, ACM, arXiv hoặc publisher của bài.
- BNB Chain BEP và tài liệu chính thức cho kiến trúc hiện hành.
- Source code chính thức khi paper hoặc spec trỏ đến implementation.

Tài liệu kỹ thuật như SWC-120 chỉ dùng làm background hoặc terminology. Nó không thay thế paper related work.

## Seed sources đã xác minh để bắt đầu

- Qian et al., *Demystifying Random Number in Ethereum Smart Contract: Taxonomy, Vulnerability Identification, and Attack Detection*: https://arxiv.org/abs/2304.12645
- Daian et al., *Flash Boys 2.0*: https://ieeexplore.ieee.org/document/9152675
- Torres et al., *Frontrunner Jones and the Raiders of the Dark Forest*: https://www.usenix.org/conference/usenixsecurity21/presentation/torres
- Yakira et al., *Economically Viable Randomness*: https://arxiv.org/abs/2007.03531
- BNB Chain, BEP-322 Builder API Specification: https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP322.md
- *MEV in Binance Builder*: https://arxiv.org/abs/2602.15395
- BNB Chain introduction và finality: https://docs.bnbchain.org/bnb-smart-chain/introduction/

Danh sách trên là seed, không phải kết quả systematic review.

## Quy trình

### 1. Tạo search log

Ghi lại:

```text
search_id,date,database,query,filters,result_count,selected_count,notes
```

Nhóm query gợi ý:

- `smart contract weak randomness attack detection`
- `on-chain randomness exploit transaction ordering`
- `BNB Smart Chain builder MEV transaction ordering`
- `blockchain randomness economic attack threshold`

### 2. Sàng lọc

Giữ tài liệu nếu nó đóng góp ít nhất một trong các phần:

- Weak RNG taxonomy/detection/exploit.
- Actor capability hoặc transaction-ordering attack.
- BSC builder architecture hoặc empirical MEV measurement.
- Economic model liên quan payoff, fee, bid hoặc opportunity cost.

Loại tài liệu tutorial lặp lại kiến thức mà không có phương pháp hoặc dữ liệu riêng khỏi bảng related work chính.

### 3. Điền ma trận

Tạo `research/related_work_matrix.csv` với schema:

```text
work_id,citation,year,chain,problem,actor_model,
rng_pattern,attack_capability,data,method,metrics,
main_result,limitation,relevance_to_rq,url
```

### 4. Nhóm theo hai trục

- Trục A: weak RNG và randomness security.
- Trục B: MEV, ordering và BSC builder.

Với từng nhóm, viết rõ họ đã trả lời gì và chưa trả lời gì. Sau đó kiểm tra giao điểm giữa hai trục.

### 5. Viết gap có điều kiện

Gap chỉ được viết theo mẫu:

> Trong tập tài liệu đã khảo sát theo tiêu chí X, nhóm chưa thấy công trình đồng thời thỏa các điều kiện A, B, C và D.

Không dùng câu `đây là nghiên cứu đầu tiên` nếu chưa có bằng chứng đủ mạnh.

## Đầu ra

- `research/search_log.csv`
- `research/related_work_matrix.csv`
- `research/related_work_notes.md`
- Một đoạn research gap đã gắn với các limitation cụ thể.

## Tiêu chí hoàn thành

- Mỗi claim trong research gap truy ngược được đến ít nhất một hàng trong matrix.
- Related Work có paper về weak RNG, MEV và BSC builder model.
- Tài liệu kỹ thuật được tách khỏi công trình nghiên cứu.
- Nhóm ghi rõ ngày khóa tìm kiếm để tránh claim bao quát vô thời hạn.

## Lỗi cần tránh

- Chỉ đọc abstract rồi suy luận limitation.
- Dùng số citation làm thước đo chất lượng duy nhất.
- Trích một paper Ethereum để mô tả quyền builder trên BSC.

## Bổ sung public-rule ở quy mô đồ án

Related work cũng cung cấp provenance cho một phần mở rộng nhỏ, không phải
systematic review toàn hệ sinh thái. Sau khi khóa các nguồn chính, nhóm chỉ
screen khoảng 3 dự án công khai có reward/winner logic dễ kiểm tra. Ghi cả
candidate không đạt vào `research/public_rule_catalog.csv`, rồi chọn tối đa
1–2 rule family có bằng chứng để tái tạo thành synthetic adapter. Rule family
chỉ được đưa vào Tầng 1 khi mapping từ mechanism công khai sang abstraction,
randomness, payoff và invariant được ghi rõ.

