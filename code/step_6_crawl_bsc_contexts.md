# Step 6: Thu thập block context từ BSC

## Mục tiêu

Tạo tập raw block contexts có provenance, đủ dữ liệu để fork/replay và kiểm tra canonical order.

## Nguồn dữ liệu

Ưu tiên RPC chính thức hoặc provider hỗ trợ các method cần thiết. BSC public RPC có rate limit và có thể tắt một số method, vì vậy Step 6 phải kiểm tra capability thay vì giả định.

Tài liệu tham chiếu:

- BSC JSON-RPC endpoints: https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/
- BSC finality APIs: https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/bsc-api-list/
- BSC hiện dùng block time 0.45 giây sau Fermi: https://docs.bnbchain.org/announce/fermi-bsc/

## Preflight RPC

Kiểm tra và lưu kết quả cho từng endpoint:

- `eth_chainId`
- `eth_blockNumber`
- `eth_getBlockByNumber` với tag `finalized`
- `eth_getBlockByHash` với full transaction objects
- `eth_getTransactionReceipt`
- Historical state access tại `block_number - 1`
- Trace methods nếu protocol yêu cầu

Gán `source_rpc_id` thay vì lưu URL có API key vào dataset.

## Dữ liệu raw cần lưu

Cho mỗi block:

- Header đầy đủ và block hash.
- Parent hash và block number.
- Canonical transaction list theo index.
- Transaction objects cần cho replay.
- Receipts và gas fields cần tính chi phí.
- Finality retrieval method và thời điểm crawl UTC.
- RPC response hash hoặc file checksum.

## Quy trình

1. Chọn block window theo sampling plan.
2. Chỉ lấy block đã finalized theo method đã xác minh.
3. Lưu JSON nguyên bản trước mọi transform.
4. Tạo normalized table từ raw JSON.
5. Kiểm tra continuity của `parentHash` trong các đoạn liên tiếp.
6. Kiểm tra transaction count, index uniqueness và receipt coverage.
7. Tạo manifest chứa checksum, crawler version và source metadata.

## Retry và lỗi

- Retry có backoff cho lỗi tạm thời.
- Không retry vô hạn với method không được provider hỗ trợ.
- Ghi `crawl_status` và `failure_reason` cho từng context.
- Không thay endpoint giữa chừng mà không đổi `source_rpc_id`.

## Bảo mật

- API key chỉ nằm trong biến môi trường hoặc secret store.
- Không commit `.env` hay raw URL chứa credential.
- Log phải redact query parameter nhạy cảm.

## Đầu ra

- `scripts/crawl/`
- `data/raw/blocks/`
- `data/raw/receipts/`
- `data/interim/block_contexts.parquet` hoặc định dạng cột tương đương
- `data/manifests/crawl_manifest.json`
- `reports/rpc_preflight.md`

## Tiêu chí hoàn thành

- Thu được khoảng 100 finalized contexts cho pilot hoặc ghi rõ lý do điều chỉnh.
- Mỗi raw file có checksum và source metadata.
- Canonical order khôi phục đúng từ transaction index.
- Có bằng chứng endpoint hỗ trợ historical state cần cho fork/replay.
- Context lỗi vẫn xuất hiện trong manifest với reason code.

## Lỗi cần tránh

- Dùng `latest` thay cho `finalized` mà không ghi nhận.
- Chỉ lưu normalized CSV rồi mất raw response.
- Giả định public RPC là archive RPC.

## Vai trò trong phần public-informed synthetic

Các context BSC được crawl vẫn là bối cảnh chain-specific cho cùng workload,
không phải bằng chứng một ứng dụng thật đã bị tấn công. Phần bổ sung chỉ dùng
sample/context policy giống baseline. Public project evidence được lưu riêng
trong `data/public_rule_evidence/`; không trộn source/ABI/trace của public
project vào pilot context artifacts. Nếu sau này có một target thật, target đó
phải được replay tại đúng pre-state trước khi được báo cáo.
- Crawl toàn bộ receipt tuần tự mà không tôn trọng rate limit.

