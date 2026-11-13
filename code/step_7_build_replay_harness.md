# Step 7: Xây replay harness

## Mục tiêu

Chạy canonical và counterfactual executions từ cùng pre-state, ghi kết quả theo schema đã khóa và tái lập được bằng seed.

## Tooling decision

Foundry/Anvil là lựa chọn mặc định để đánh giá vì hỗ trợ fork EVM, pin block, điều khiển mining và state snapshot. Tài liệu: https://getfoundry.sh/anvil/

Chỉ đổi sang Hardhat hoặc custom BSC node nếu preflight cho thấy Foundry/Anvil không mô phỏng được field hoặc behavior cần thiết. Ghi quyết định vào decision log.

## Thành phần harness

```text
contracts/
├── rng/
│   ├── weak/
│   └── safe/
├── app/
└── test/

scripts/replay/
├── load_context
├── run_canonical
├── run_counterfactual
├── collect_result
└── validate_result
```

Tên file cụ thể phụ thuộc toolchain, nhưng trách nhiệm của từng phần phải giữ nguyên.

## Contract workload

Dùng một application harness tối thiểu có:

- Danh sách participant hoặc candidate outcomes.
- Hàm gọi weak RNG.
- Một payoff rule rõ ràng.
- Event ghi input, entropy source, outcome và winner.
- Cùng application logic cho weak RNG và safe reference.

Không cần xây DApp hoặc UI.

## Replay flow

1. Pin fork tại `pre_state_block`.
2. Deploy hoặc load đúng contract version.
3. Áp canonical transaction set/order.
4. Lưu snapshot và canonical result.
5. Restore cùng pre-state.
6. Áp counterfactual strategy.
7. Lưu manipulated result và execution trace.
8. Validate invariants rồi xuất một observation row.

## Determinism checks

- Cùng context, code commit, strategy và seed phải cho cùng outcome.
- Snapshot restore không được rò state từ run trước.
- Event và storage outcome phải khớp.
- Gas accounting phải lấy từ receipt của run tương ứng.
- Harness không được thay timestamp hoặc header field nếu threat model không cấp quyền đó.

## Safe reference

Nếu dùng commit-before-entropy:

- Commitment phải được cố định trước entropy future context.
- Attacker không được chọn lại commitment sau khi thấy entropy.
- Replay phải giữ cùng participant set và payoff rule.

Nếu dùng VRF:

- Tách integration/liveness test khỏi security claim.
- Mock chỉ kiểm tra application wiring, không chứng minh oracle security.
- Không gọi random local seed là VRF nếu không có proof verification.

## Kết quả xuất ra

Mỗi run cần:

- Observation row theo schema.
- Transaction receipts.
- Contract events.
- Strategy trace.
- Invariant check result.
- Failure reason nếu run không hợp lệ.

## Đầu ra

- `contracts/`
- `scripts/replay/`
- Unit tests và integration tests.
- `reports/replay_harness_validation.md`

## Tiêu chí hoàn thành

- Chạy lại cùng fixture nhiều lần cho cùng kết quả.
- Canonical và counterfactual bắt đầu từ cùng pre-state.
- Có ít nhất một weak RNG pattern và safe reference chạy end-to-end.
- Mọi result row qua schema validation.
- Harness không dùng capability ngoài threat model.

## Lỗi cần tránh

- So canonical ở block A với manipulated run ở block B.
- Deploy contract sau khi đã dùng block field cần đo mà không ghi rõ.
- Dùng mock VRF output để claim VRF ngăn attack.

## Adapter cho phần bổ sung

Không sửa fixture cũ để làm thay đổi kết quả method validation. Nếu triển khai
Tầng 1, thêm adapter cho 1–2 public-informed synthetic rule families và giữ
nguyên interface workload, capability, paired replay, evidence và schema. Mỗi
adapter phải tham chiếu public-rule mapping và ghi rõ invariant được giữ. Một
real-rule adapter chỉ là tùy chọn cho tối đa một target có replay match; không
thêm predictor hoặc model rule inference vào harness hiện tại.

