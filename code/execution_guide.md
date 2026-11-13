# Execution guide — phạm vi hiện tại

## Trạng thái

- Step 8–9: Revalidated trên VERY_SIMPLE_RULES method-validation fixture.
- Pilot cũ và pre-experiment batch phải giữ nguyên.
- Step 10: chưa bắt đầu.
- Phần tiếp theo chỉ gồm public-informed synthetic rules ở quy mô nhỏ.
- Real-rule replay và rule inference là tùy chọn/future work.

## Công cụ

| Việc | Công cụ | Kết quả |
| --- | --- | --- |
| Thu block context | Python, BSC JSON-RPC, raw JSON + checksum | context và crawl manifest |
| Kiểm tra rule công khai | browser/RPC/explorer, ABI/source/bytecode, trace/event | provenance record |
| Chạy replay | Foundry/Anvil, Python runner | canonical/counterfactual evidence |
| Validate | Python virtualenv, JSON Schema | validation report |
| Phân tích | Python standard library; chỉ thêm thư viện khi protocol yêu cầu | paired metrics và report |

Mọi lệnh Python phải chạy trong virtualenv hiện có:

    source venv/bin/activate
    python ...

## Cấu hình môi trường

Nếu chưa có file cấu hình local, tạo từ template trước khi chạy crawl hoặc replay:

    cd final_project/code
    cp -n .env.example .env

Sau đó điền `PINAX_API_KEY` trong `.env`. `PINAX_RPC_BASE_URL` là tùy chọn;
nếu bỏ trống, script dùng `https://bsc.rpc.pinax.network`. Có thể dùng biến môi
trường thay cho file `.env`:

    export PINAX_API_KEY="<local-only-secret>"
    export PINAX_RPC_BASE_URL="https://bsc.rpc.pinax.network"

Không commit `.env` và không đưa API key vào artifact, report hoặc log.

## Cách chạy bằng Docker Compose

Docker là cách dễ nhất cho thành viên chưa có Python, Foundry hoặc Anvil. Cần
cài Docker Desktop, sau đó chạy từ thư mục này:

    cd final_project/code
    cp -n .env.example .env

Mở `.env`, điền `PINAX_API_KEY`, rồi build image:

    docker compose build

Image đã chứa Python, các package trong `analysis/requirements.txt`, `forge`,
`anvil` và `cast`. Repo được mount vào container nên các file output vẫn nằm
trong máy local.

Kiểm tra runner và schema trước khi replay:

    docker compose run --rm topic1 python scripts/replay/test_public_informed.py
    docker compose run --rm topic1 python scripts/replay/validate_result.py \
      --self-test \
      --schema research/schema/bsc_rng_mev_replay.schema.json

Chạy smoke test một context. Output nằm trong thư mục local bị ignore và không
đụng vào các batch nghiên cứu đã có:

    docker compose run --rm topic1 python scripts/replay/run_public_informed.py \
      --limit 1 --workers 1 \
      --output data/derived/docker_smoke \
      --manifest data/manifests/docker_smoke.json \
      --report reports/docker_smoke.md

Validate smoke output:

    docker compose run --rm topic1 python scripts/replay/validate_result.py \
      --input data/derived/docker_smoke/observations.jsonl \
      --schema research/schema/bsc_rng_mev_replay.schema.json

Sau khi smoke test pass, có thể chạy đủ 100 context bằng output riêng:

    docker compose run --rm topic1 python scripts/replay/run_public_informed.py \
      --limit 100 --workers 4 \
      --output data/derived/docker_public_informed \
      --manifest data/manifests/docker_public_informed.json \
      --report reports/docker_public_informed.md

Lệnh đầy đủ cần `PINAX_API_KEY`, kết nối BSC RPC và có thể mất nhiều phút.
Không dùng output mặc định nếu chưa chắc muốn tạo lại batch
`public_informed_synthetic`. Muốn mở shell trong container:

    docker compose run --rm topic1 bash

## Luồng bổ sung

1. Điền khoảng 3 candidate vào public-rule catalog.
2. Thu code/bytecode, ABI, randomness, payoff và trace/event evidence.
3. Đánh dấu candidate pass/fail/excluded; không bỏ im lặng.
4. Tạo 1–2 synthetic mapping có preserved invariant.
5. Chạy cùng workload và capability matrix của VERY_SIMPLE_RULES.
6. Ghi output vào batch public-informed-synthetic riêng.
7. Validate observations và so sánh với baseline.

Không chạy Step 10 chỉ vì catalog template đã tồn tại. Không dùng synthetic result
để nói rằng ứng dụng thật hoặc builder lịch sử đã bị tấn công.

## Rule thật tùy chọn

Chỉ tạo real-rule adapter khi có replay match tại đúng pre-state và đầy đủ
randomness/payoff evidence. Tối đa một target. Nếu thiếu điều kiện, ghi
unsupported hoặc rule_unconfirmed.

## Rule inference tương lai

Nếu sau này triển khai, phải tách context discovery khỏi context validation,
không để outcome của validation lọt vào bước suy đoán. Hiện tại không cài model,
không thêm dependency và không chạy bước này.

## Kiểm tra trước khi báo cáo

- baseline và public-informed synthetic dùng cùng workload;
- paired branches bắt đầu cùng pre-state;
- validity, receipts, traces, events và failure reasons đầy đủ;
- schema validation pass;
- pilot và pre-experiment artifacts không đổi;
- git diff --check pass.
