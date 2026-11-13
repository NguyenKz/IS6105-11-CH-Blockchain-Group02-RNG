# **Mini Proposal**

> **PROPOSAL CHÍNH CỦA TOPIC ĐANG THỰC HIỆN**
>
> Direction 1: đo lường khả năng khai thác RNG on-chain yếu theo năng lực searcher và builder trên BNB Smart Chain. Đây là nghiên cứu paired replay thực nghiệm/an ninh, không phải nghiên cứu machine learning.

# **A. Information**

- **Project / Tên đề tài:** Phân tích khả năng khai thác RNG on-chain yếu theo năng lực searcher và builder trên BNB Smart Chain (*Capability-Aware Analysis of Weak On-Chain RNG Exploitability on BNB Smart Chain*).  
- **Course / Môn học:** Công nghệ Blockchain, IS6105.11.CH.  
- **Duration / Thời gian thực hiện:** 09/2026 \- 11/2026.  
- **Group / Nhóm:** Nhóm 02 \- OnChainRNG.  
- **Members / Thành viên:**  
  1. Bùi Thái Hoàng, 250104008, [250104008@gm.uit.edu.vn](mailto:250104008@gm.uit.edu.vn).  
  2. Trần Thảo Nguyên, 250101049, [nguyentt.20@grad.uit.edu.vn](mailto:nguyentt.20@grad.uit.edu.vn).  
  3. Nguyễn Duy Trọng Nhân, 250104048, [250104048@gm.uit.edu.vn](mailto:250104048@gm.uit.edu.vn).  
  4. Nguyễn Phi Yến, 250104059, [250104059@grad.uit.edu.vn](mailto:250104059@grad.uit.edu.vn).  
- **Supervisor / Giảng viên hướng dẫn:** Trần Hưng Nghiệp, [nghiepth@uit.edu.vn](mailto:nghiepth@uit.edu.vn).

# **B. Content**

## **1\. Mini Problem Formulation**

Đây là nghiên cứu đo lường thực nghiệm / an ninh (empirical measurement), không huấn luyện mô hình học máy: dùng paired replay có kiểm soát để so sánh năng lực attacker, không classification hay regression.

Các ứng dụng xổ số và trò chơi trên blockchain cần kết quả ngẫu nhiên công bằng vì kết quả quyết định việc phân phối phần thưởng. Khi nguồn ngẫu nhiên phụ thuộc vào dữ liệu công khai hoặc thứ tự giao dịch, người tham gia có thể dự đoán hay tác động đến kết quả. Tuy nhiên, searcher và builder có quyền khác nhau nên mức khai thác và lợi ích kinh tế cũng khác nhau. Đề tài phân tích RNG yếu trên BNB Smart Chain (BSC), xác định ảnh hưởng của từng năng lực tấn công, điều kiện khai thác có lợi và mức giảm ảnh hưởng khi dùng cơ chế cam kết trước entropy. Mục tiêu là cung cấp bằng chứng thực nghiệm cho việc lựa chọn randomness trong ứng dụng có thưởng.

Nghiên cứu giới hạn ở workload có thưởng do nhóm xây dựng, sử dụng context khối finalized của BSC mainnet. Searcher chỉ biết thông tin công khai và điều chỉnh giao dịch của mình, builder được sắp xếp hoặc loại giao dịch trong tập đã nhận, nhưng phải giữ tính hợp lệ. Giả định mạng đồng thuận bình thường. Không xét reorg, thông đồng validator, giả chữ ký, sửa header hoặc tấn công ứng dụng thật.

Các nghiên cứu hiện có tập trung vào phát hiện weak RNG \[1\], thiết kế randomness theo động cơ kinh tế \[2\] hoặc đo MEV do thứ tự giao dịch \[3, 4, 7\]. Trong phạm vi tài liệu khảo sát, còn thiếu phép so sánh có kiểm soát kết nối quyền searcher/builder trên BSC với ảnh hưởng lên RNG và điều kiện hòa vốn.

Phạm vi thực nghiệm được chia thành ba mức, theo thứ tự ưu tiên. **Baseline `VERY_SIMPLE_RULES`** là workload synthetic rất đơn giản đã dùng trong pre-experiment validation; mục tiêu của nó là kiểm tra phương pháp. Phần bổ sung chính là **public-informed synthetic evaluation**: khảo sát khoảng 3 dự án công khai, chọn 1–2 rule family có bằng chứng, rồi tái tạo các đặc điểm đó trong rule synthetic và chạy cùng workload, context, participant count, capability và pipeline như baseline. **Replay trên một rule thật** chỉ là hướng tùy chọn nếu còn thời gian và có đủ replay match. Không có bước chọn top 3 hướng hay mở rộng thành khảo sát hệ sinh thái.

| RQ | Câu hỏi nghiên cứu |
| :---- | :---- |
| **RQ-C1** | Trong workload đã khai báo, searcher và builder có thể dự đoán hoặc ảnh hưởng đến kết quả RNG yếu bằng những năng lực nào? |
| **RQ-C2** | Reorder và selective inclusion thay đổi xác suất thắng, giá trị kỳ vọng bao nhiêu so với canonical và searcher-only? |
| **RQ-C3** | Với chi phí thực thi và giả định chi phí được ghi rõ, điều kiện hòa vốn của từng chiến lược là gì? |
| **RQ-C4** | Đối chứng commit-before-entropy thay đổi mức ảnh hưởng của các chiến lược thế nào trong điều kiện so sánh tương ứng? |

Giả thuyết:

- H1 có pattern RNG chịu ảnh hưởng bởi quyền đã nêu.  
- H2 quyền builder tạo lợi thế thêm so với searcher.  
- H3 có điều kiện hòa vốn trong mô hình chi phí xét đến.  
- H4 commit-before-entropy giảm ảnh hưởng lên kết quả. Các giả thuyết đều cần kiểm định.

Mục tiêu và đóng góp dự kiến: xây dựng ma trận năng lực khai thác, bộ dữ liệu thí nghiệm ghép cặp có thể tái lập và phân tích lợi ích kinh tế có điều kiện. Kết luận chỉ áp dụng cho workload và giả định đã kiểm tra.

## **2\. Related Work**

| Nguồn | Nội dung liên quan | Giới hạn đối với bài toán |
| :---- | :---- | :---- |
| Qian et al. \[1\] | Phân loại weak RNG và dùng RNVulDet để phát hiện lỗi và giao dịch tấn công trên Ethereum. | Chưa cung cấp so sánh ghép cặp theo quyền builder BSC. |
| Yakira et al. \[2\] | Phân tích secrecy, robustness và động cơ kinh tế của distributed commit-reveal. | Không đo ảnh hưởng của từng quyền ordering/inclusion đến workload của BSC. |
| Daian et al. \[3\] Torres et al. \[4\] | Transaction ordering, MEV và các dạng frontrunning trên Ethereum. | Không trực tiếp đánh giá RNG yếu cùng đối chứng randomness. |
| Wang et al. \[7\] | Khảo sát builder-driven MEV arbitrage trên BSC. | Đối tượng là arbitrage, không phải kết quả RNG. |

BEP-322 và tài liệu BNB Chain \[5, 6\] cung cấp cơ sở để tách searcher, builder và proposer. Nghiên cứu kế thừa các khái niệm này để thiết kế phép đo, không đề xuất một protocol RNG mới.

## **3\. Data**

Bộ dữ liệu chung bsc\_rng\_mev\_replay gồm context BSC mainnet lấy qua Pinax JSON-RPC và kết quả thí nghiệm local liên kết bằng context\_id. Context cung cấp block hash, parent hash và pre-state, replay bổ sung input, thứ tự giao dịch, outcome, receipt và trace để cả bốn RQ dùng chung một đơn vị so sánh.

Khảo sát khả thi ban đầu đã thu 100 finalized blocks, 11.070 giao dịch và receipts, kiểm tra liên tục parent hash, index và coverage. Nhóm đã chạy fixture và pipeline trên fork cục bộ. Kết quả này bước đầu chứng minh khả năng lấy dữ liệu và vận hành phương pháp, chưa kiểm định giả thuyết. Quy mô và nguồn kiểm tra nằm ở Phụ lục 3.1.

Dữ liệu không chứa nhãn tấn công lịch sử, mempool, private flow hay builder bid. `BUILDER_RECEIVED` là giả định về tập giao dịch sẵn có cho builder trong thí nghiệm, không phải private order flow quan sát từ mainnet. Historical code/call/trace mới được thử trên một candidate transaction nên coverage state chưa xác nhận cho mọi context. Workload có thưởng là synthetic do nhóm xây trên context khối thật, phù hợp phép so sánh có kiểm soát, không đại diện tỷ lệ lỗ hổng hay lợi nhuận trên toàn BSC. Điều kiện tái phân phối dữ liệu nguồn chưa được xác nhận, việc phát hành phải tuân thủ điều khoản của nhà cung cấp.

Để giảm thiên lệch do baseline quá dễ, public-rule catalog sẽ lưu cả candidate pass, fail và excluded. Mỗi synthetic rule family phải trỏ được về code/bytecode, ABI, event, trace, randomness và payoff evidence của public project; nhóm không tự tạo rule chỉ vì nó làm kết quả đẹp.

## **4\. Evaluation**

Giá trị ứng dụng là chỉ ra điều kiện rủi ro và hiệu quả đối chứng cho workload đã kiểm tra. Thành công thực nghiệm là phép so sánh hợp lệ, tái lập được và trả lời RQ kể cả khi giả thuyết bị bác bỏ.

Đánh giá trên mẫu context nghiên cứu chính, tách khỏi khảo sát ban đầu. Đo xác suất thắng, chênh lệch xác suất thắng, phần thưởng kỳ vọng, lợi thế tăng thêm của builder, lợi nhuận ròng và ngưỡng hòa vốn theo mô hình chi phí. So sánh ghép cặp, báo khoảng bất định 95% và toàn bộ replay failures. Không suy rộng thành tỷ lệ tấn công hoặc lợi nhuận thực tế trên BSC.

Ý nghĩa thực tế của metrics (trong phạm vi workload và cost model đã khai báo): `delta_p_win` và capability uplift cho biết quyền nào làm lệch kết quả đáng kể. `break_even_prize` là ngưỡng giải thưởng mà dưới đó thao túng không có lời theo mô hình chi phí, là tín hiệu cho dApp cân nhắc tránh weak RNG hoặc chuyển sang commit-before-entropy. Hiệu quả đối chứng RQ-C4 cho biết cơ chế tham chiếu giảm ảnh hưởng đến mức nào. Các số này không ước lượng prevalence hay lợi nhuận lịch sử trên toàn BSC.

## **5\. Baselines**

B0 là weak RNG chạy theo thứ tự chuẩn (canonical), với input attacker cố định. B1 là searcher-only, làm mốc đánh giá phần quyền tăng thêm của builder. Commit-before-entropy là đối chứng cơ chế: commitment phải được cố định trước khi biết entropy, giữ cùng tập người tham gia và quy tắc thưởng.

## **6\. Proposed Method**

Dùng replay có kiểm soát trên Foundry/Anvil fork cục bộ. Từ cùng pre-state, chạy canonical và từng chiến lược trên workload cố định, khôi phục snapshot trước mỗi nhánh. Chỉ thay input/thời điểm thuộc attacker, thứ tự hoặc inclusion theo quyền đang xét. Baseline và public-informed synthetic dùng cùng pipeline; rule family là biến thay đổi đã được ghi provenance. Mainnet chỉ được đọc, mọi giao dịch thử nghiệm được gửi tới local.

**Plan B / fallback:** nếu H2 bị bác bỏ hoặc builder uplift ≈ 0 trong khoảng tin cậy, báo kết quả âm và thu hẹp claim (không kết luận “builder luôn lợi thế”). Nếu thiếu pre-state/trace trên nhiều context, giảm N về subset có evidence đầy đủ và ưu tiên RQ-C1/C2. Nếu commit-before-entropy chưa đạt điều kiện cố định commitment trước entropy, giữ RQ-C4 ở trạng thái failure/incomplete và chỉ kết luận RQ-C1-C3. Mọi thu hẹp scope được ghi trong báo cáo cùng số context/valid pairs còn lại.

## **7\. Expected Results**

Dự kiến thu được ma trận năng lực, bảng chênh lệch outcome, phân tích hòa vốn và so sánh đối chứng qua các thí nghiệm ở Phụ lục 3.6. Không đặt trước mức lợi thế hay lợi nhuận. Nếu không ghi nhận ảnh hưởng, báo kết quả âm, nếu thiếu state hoặc đối chứng chưa đạt điều kiện, giữ failure và giới hạn câu hỏi trả lời được. Không diễn giải replay thành bằng chứng builder lịch sử đã tấn công.

## **8\. Phần mở rộng có kiểm soát**

- **Tầng 1:** dùng cùng workload của baseline, thay rule bằng 1–2 synthetic rule family có public provenance. Kết quả được báo riêng với method-validation result.
- **Tầng 2 tùy chọn:** nếu đủ thời gian, chọn tối đa một ứng dụng/rule thật có source hoặc bytecode, ABI/calldata, randomness/payoff evidence và replay match tại đúng pre-state. Thiếu evidence thì ghi `unsupported` hoặc `rule_unconfirmed`, không ép replay.
- **Future work:** có thể thu nhiều context để suy đoán rule rồi kiểm tra trên context độc lập; hiện tại không thêm model hoặc dependency cho hướng này.

# **References**

1. Qian, P., et al. (2023). *Demystifying Random Number in Ethereum Smart Contract: Taxonomy, Vulnerability Identification, and Attack Detection*. [arXiv:2304.12645](https://arxiv.org/abs/2304.12645).  
2. Yakira, D., Asayag, A., Grayevsky, I., & Keidar, I. (2020). *Economically Viable Randomness*. [arXiv:2007.03531](https://arxiv.org/abs/2007.03531).  
3. Daian, P., et al. (2019). *Flash Boys 2.0: Frontrunning, Transaction Reordering, and Consensus Instability in Decentralized Exchanges*. Bản preprint: [arXiv:1904.05234](https://arxiv.org/abs/1904.05234).  
4. Torres, C. F., Camino, R., & State, R. (2021). *Frontrunner Jones and the Raiders of the Dark Forest: An Empirical Study of Frontrunning on the Ethereum Blockchain*. [USENIX Security 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/torres).  
5. BNB Chain (2023). *BEP-322: Builder API Specification for BNB Smart Chain*. [Đặc tả chính thức](https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP322.md). Truy cập 01/10/2026.  
6. BNB Chain. *BSC MEV Overview*. [Tài liệu chính thức](https://docs.bnbchain.org/bnb-smart-chain/validator/mev/overview/). Truy cập 01/10/2026.  
7. Wang, Q., Li, R., Yu, G., Gramoli, V., & Chen, S. (2026). *MEV in Binance Builder*. Preprint: [arXiv:2602.15395v2](https://arxiv.org/abs/2602.15395v2).

# **Appendix**

## **1\. Timeline**

| Tuần (09/2026 \- 11/2026) | Công việc và đầu ra | Phụ trách |
| :---- | :---- | :---- |
| 1 đến 4 | Khảo sát tài liệu, thu hẹp RQ, xác định dữ liệu và thử khả năng thu thập/thực thi. | Cả nhóm |
| 5 đến 6 | Kiểm chứng logic hợp đồng, chiến lược và đối chứng. Hoàn thiện quy trình thí nghiệm, cấu trúc dữ liệu, workload và kế hoạch lấy mẫu. | Cả nhóm |
| 7 đến 8 | Thu mẫu nghiên cứu chính. Chạy replay ghép cặp và lưu đầy đủ evidence/failures. | Cả nhóm |
| 9 đến 10 | Phân tích theo RQ, kiểm tra bất định và sensitivity chi phí. Tái lập kết quả. | Cả nhóm |
| 11 đến 12 | Hoàn thiện báo cáo, artifacts và bài trình trình bày. | Cả nhóm |

## **2\. Additional Content**

### **2.1. Threat model**

| Actor | Visibility và quyền |
| :---- | :---- |
| **User** | Cung cấp giao dịch và input trung thực, cố định. |
| **Searcher** | **PUBLIC\_ONLY**: biết state và thông tin công khai tại thời điểm quyết định, chỉ điều chỉnh input/thời điểm giao dịch của mình, giữ thứ tự và inclusion của honest. |
| **Builder** | **BUILDER\_RECEIVED**: biết tập giao dịch giả định đã nhận, reorder hợp lệ hoặc omit candidate khai báo trước. Không giả chữ ký, tạo state invalid hay sửa finalized chain. |
| **Proposer** | Chọn, ký và đề xuất khối theo kiến trúc \[5, 6\], không phải là attacker thực nghiệm. |

BUILDER\_RECEIVED là giả định về tập giao dịch sẵn có cho builder, không phải private flow quan sát từ mainnet. Searcher không được dùng entropy tương lai dù harness đã biết dữ liệu lịch sử.

### **2.2. Ánh xạ RQ với dữ liệu và chỉ số đánh giá**

| RQ | Trường dữ liệu cần dùng | Metric / đầu ra |
| :---- | :---- | :---- |
| **RQ-C1** | RNG pattern, actor, visibility, input/timing, strategy trace, outcome và validity checks. | Ma trận predictability/influence cùng điều kiện thông tin và quyền. |
| **RQ-C2** | Canonical/counterfactual win flags, order, omissions và payoff. | **p\_win**, **delta\_p\_win**, expected payout và capability uplift. |
| **RQ-C3** | Win difference, prize, receipt fee, bid/bribe và opportunity-cost model. | Net profit và break-even theo từng giả định chi phí. |
| **RQ-C4** | Các cặp weak/reference cùng context, workload, participant và payoff rule. | Chênh lệch ảnh hưởng chiến lược, báo riêng liveness khi có omission. |

## **3\. Experimental Plan**

### **3.1. Dataset**

Mỗi observation ghép cặp được định danh duy nhất bằng bộ trường context\_id \+ scenario\_id \+ seed \+ cost\_model\_id. Các thành phần raw mainnet và kết quả local cùng phục vụ bộ dữ liệu bsc\_rng\_mev\_replay.

| Thành phần khảo sát ban đầu | Quy mô | Nguồn và vai trò |
| :---- | :---- | :---- |
| Context mainnet | 100 khối finalized trên BSC Mainnet (chain ID 56), từ block 125053984 đến 125054083\. | Thu từ BSC mainnet qua Pinax JSON-RPC để cung cấp block context cho thí nghiệm, không chứa nhãn tấn công. |
| Giao dịch và receipts | 11.070 giao dịch, đã lấy receipt cho toàn bộ giao dịch trong 100 khối. | Thu qua Pinax JSON-RPC để kiểm tra khả năng thu thập và tính đầy đủ của dữ liệu. |
| Historical code/call/trace | Kiểm tra một candidate transaction. | Đã thử truy vấn code, gọi hợp đồng tại state lịch sử và lấy trace qua Pinax. Chưa xác nhận coverage cho mọi contract/context. |
| Pipeline replay local | 100 contexts × 6 scenarios × 4 cost models \= 2.400 bản ghi. | Sinh bằng Foundry/Anvil trên fork cục bộ để kiểm tra khả năng vận hành pipeline và cấu trúc output. |

Sáu scenarios và bốn cost models chia sẻ context. Vì vậy, 2.400 rows không phải 2.400 mẫu độc lập. Khảo sát ban đầu không thuộc tập kết luận chính và không xác nhận lợi thế của attacker hay hiệu quả đối chứng.

Nghiên cứu chính dùng cửa sổ finalized và seed cố định, chọn context theo hash ordering trước khi xem outcome và không chủ ý overlap với khảo sát ban đầu. Kế hoạch lấy mẫu gồm tối thiểu 100 và tối đa 1.000 contexts. Nhóm xác định các đợt lấy mẫu và thời điểm kiểm tra thống kê trước khi chạy thí nghiệm. Dừng khi Wilson 95% interval của tỷ lệ paired outcome change đạt half-width 0,05, hoặc tại giới hạn tối đa và báo interval thực tế. Quy tắc này không bảo đảm 100 context là đủ. Đã thu thập đủ data cho 100 contexts, và có thể tăng thêm data tùy theo nhu cầu thực tế.

Data pipeline:

1. Xác định trước khoảng block lấy mẫu, seed, workload và danh sách source block hashes.  
2. Thu blocks/receipts và lưu raw response, checksum, thời điểm và source RPC ID.  
3. Ghim context\_id \= bsc-mainnet:\<block\_hash\> và pre\_state\_block \= source\_block\_number \- 1\. Sau đó, fork state trước source block.  
4. Chạy hợp đồng thử nghiệm trên local. Canonical là thứ tự quy ước của workload, không phải toàn bộ lịch sử giao dịch BSC.  
5. Khôi phục cùng pre-state cho mỗi counterfactual và lưu input, order, omission, receipts/events/traces cho cả hai nhánh.  
6. Kiểm tra bản ghi theo schema và kiểm tra tính duy nhất của bộ trường định danh. Giữ failure cùng stage/lý do, sau đó tính metrics trên các cặp hợp lệ.

Giữ tách nhãn OBSERVED cho dữ liệu chain, REPLAYED cho thực thi local, MODELED cho giả định chi phí/prize và DERIVED cho metrics tính toán. Không dùng dữ liệu giả để thay cho historical state bị thiếu.

### **3.2. Evaluation Protocol**

Trong cùng cơ chế, canonical và counterfactual phải có cùng context, code, storage, participant set, workload, seed và honest inputs. Giữa weak RNG và reference, chỉ có cơ chế randomness khác nhau. Quy tắc tham gia, thắng và thưởng phải so sánh được. Không sửa timestamp, block number/hash hoặc header tùy ý.

Trước run chính, kiểm tra snapshot restoration, nonce/dependency, gas limit, outcome decoder khớp payoff và strategy thực sự áp dụng capability khai báo. Commitment trong cơ chế đối chứng phải được cố định trước khi entropy khả dụng và không được thay đổi sau đó. Chạy lại cùng context/seed/code phải cho cùng outcome hash. Nhóm lưu mọi failure và không tính failure hoặc vòng chưa hoàn tất như một lần attacker thua.

Với W\_i là win flag của attacker và V là phần thưởng cố định:

- p\_win \= mean(W\_i) trên các vòng hợp lệ.  
- delta\_p\_win \= mean(W\_i(counterfactual) \- W\_i(canonical)) trên cùng tập context ghép cặp.  
- expected\_payout \= p\_win × V.  
- incremental\_expected\_payout \= delta\_p\_win × V.  
- Capability uplift là chênh lệch hiệu ứng của builder và searcher trên cùng context, với các thay đổi ngoài capability được kiểm soát.  
- net\_profit \= incremental\_expected\_payout \- transaction\_cost \- bid\_or\_bribe \- opportunity\_cost.  
- break\_even\_prize \= total\_cost / delta\_p\_win nếu delta\_p\_win \> 0\. Nếu không, không có ngưỡng hòa vốn hữu hạn theo mô hình này.

Chi phí transaction lấy từ receipt local bằng gasUsed × effectiveGasPrice, mang nhãn REPLAYED, không phải tiền đã trả trên mainnet. Bid/bribe bằng 0 là giả định MODELED. Phân tích độ nhạy dùng bốn mô hình opportunity cost: không tính chi phí cơ hội, thấp, cơ sở và cao, tương ứng với 0, 1, 2 và 4 lần phí giao dịch. Không lấy block reward làm opportunity cost.

Tiền tệ lưu bằng integer wei. Lợi nhuận phải biểu diễn được giá trị âm. Nếu thiếu cost evidence, ghi kết quả kinh tế chưa xác định thay vì tự điền số. Prize là biến phân tích, không phải giải thưởng quan sát của một trò chơi thật.

Báo số context và valid/failed pairs theo scenario, failure breakdown và liveness. Ước lượng uncertainty bằng paired bootstrap theo context, giữ các scenario cùng context trong một cluster và báo khoảng 95%. Tách phân tích xác nhận theo protocol khỏi khám phá bổ sung. Kết quả trên workload synthetic không ước lượng prevalence, historical attack hoặc lợi nhuận toàn BSC.

**Error analysis:** không chỉ đếm failure. Phân loại theo stage (thu context, fork/pre-state, snapshot restore, strategy apply, decode outcome, cost evidence) và theo scenario/capability; ghi pattern lặp (ví dụ thiếu code tại height, nonce/dependency, gas limit, decoder lệch payoff, strategy vượt visibility). Phân tích này quyết định context nào bị loại khỏi metric chính, có cần thu hẹp RQ, và gợi ý sửa harness trước run bổ sung. Artifact tái lập tối thiểu: schema, seed, source block hashes, phiên bản Foundry/Anvil và dependency, manifest checksum, raw evidence và bảng failure.

### **3.3. Baselines**

- B0: weak context RNG, canonical order, input attacker cố định.  
- B1: searcher-only trên weak RNG, cùng honest workload/inclusion, làm mốc để so sánh với builder.  
- Đối chứng: commit-before-entropy, cùng participant set và payoff rule, chạy canonical và các capability tương ứng.

| Scenario | Cơ chế / actor / visibility | Thay đổi được phép |
| :---- | :---- | :---- |
| **SC-001** | Weak / searcher / **PUBLIC\_ONLY** | Input hoặc timing thuộc về attacker trong search budget cố định. |
| **SC-002** | Weak / builder / **BUILDER\_RECEIVED** | Đổi thứ tự cùng transaction set và giữ input. |
| **SC-003** | Weak / builder / **BUILDER\_RECEIVED** | Omit transaction honest khai báo trước và ghi lý do và liveness. |
| **SC-004** | Reference/searcher / **PUBLIC\_ONLY** | Cùng capability SC-001 và không đổi commitment sau khi biết entropy. |
| **SC-005** | Reference/builder / **BUILDER\_RECEIVED** | Cùng capability SC-002. |
| **SC-006** | Reference/builder / **BUILDER\_RECEIVED** | Cùng candidate omission và capability SC-003. |

### **3.4. Proposed Method**

Thiết kế paired replay theo năng lực của attacker. Strategy engine nhận context, visibility, tập giao dịch, canonical order, seed và gas limit. Kết quả gồm candidate set, selected order, exclusions, validity evidence, search budget và stop reason.

Với workload hai giao dịch, xét đủ hai permutation hợp lệ. Khi mở rộng workload, giới hạn tối đa 32 candidate orders theo thứ tự lexicographic. Không gọi kết quả là global optimum. Searcher chỉ quyết định dựa trên thông tin khả dụng trước khi thực thi. Giao dịch bị loại được chọn trước khi xem outcome và không thay đổi theo kết quả. Mỗi cơ chế có canonical và ba nhánh tương ứng, chạy tuần tự trên Anvil local.

### **3.5. Ablation**

1. Loại quyền reorder của builder, giữ input/inclusion và các điều kiện khác, để đo phần ảnh hưởng riêng của thứ tự.  
2. Loại quyền selective inclusion, giữ order/input tương thích, để tách tác động của omission khỏi reorder.  
3. Giữ cùng replay outcomes, thay opportunity-cost model để kiểm tra độ nhạy của điều kiện hòa vốn.

So sánh weak RNG với commit-before-entropy là đối chứng của cơ chế. Nếu hai nhánh khác đồng thời có nhiều quyền hoặc workload, không gán toàn bộ chênh lệch cho một capability.

### **3.6. Experiment Specifications**

| Thí nghiệm | Thực hiện | Kết quả cần để trả lời RQ |
| :---- | :---- | :---- |
| **E1: Capability trên weak RNG** | Chạy B0, SC-001, SC-002 và SC-003 trên mẫu nghiên cứu chính. Lưu validity và paired evidence. | Ma trận năng lực, win/outcome differences và capability uplift cho RQ-C1 và RQ-C2. |
| **E2: Đối chứng randomness** | Chạy canonical reference và SC-004, SC-005 và SC-006 trên cùng context, participant/payoff rule. | Chênh lệch mức ảnh hưởng và liveness cho RQ-C4, sau khi kiểm chứng commitment được cố định trước entropy. |
| **E3: Kinh tế có điều kiện** | Dùng paired outcomes của E1 và E2 để tính sensitivity theo prize và cost models. | Net profit và ngưỡng hòa vốn kèm giả định cho RQ-C3. Báo chưa xác định khi thiếu bằng chứng. |

Sau khi kiểm chứng logic, nhóm ghi rõ phiên bản code, schema, seed và kế hoạch phân tích trước khi thu mẫu và chạy nghiên cứu chính. Các lựa chọn này được giữ nguyên trong suốt thí nghiệm. Lưu manifest, raw evidence và mọi failure để tái lập. Không nâng giả thuyết thành kết luận chỉ vì một fixture thay đổi winner.
