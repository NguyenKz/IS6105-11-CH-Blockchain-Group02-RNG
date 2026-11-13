# PancakeSwap Lottery v2 rule evidence

- Deployed address: `0x5aF6D33DE2ccEC94efb1bDF8f92Bd58085432d2c` on BNB Smart Chain.
- Observed runtime bytecode: 20,240 bytes; Keccak-256 `0x162b6e63cc0f75d55e6cd1d80c9325385a43896a031c910673377f13fa179bba`.
- Archived official lottery repository commit: `d2ebe90700f842bd62280e0ecc7bb95c2475f2c4`.

Official documentation identifies Chainlink VRF as the randomness source. The implementation separates closing/requesting a lottery draw from the random-generator callback that stores winning numbers. The deployed v2 ABI exposes `LotteryNumberDrawn`, ticket purchase and claim evidence.

This project is a catalog-only safe reference. Step 10 does not emulate a VRF proof and does not use a mock callback as security evidence.

Sources:

- <https://docs.pancakeswap.finance/play/lottery>
- <https://bscscan.com/address/0x5af6d33de2ccec94efb1bdf8f92bd58085432d2c>
- <https://github.com/pancakeswap/lottery-contract/tree/d2ebe90700f842bd62280e0ecc7bb95c2475f2c4>
- <https://bscscan.com/tx/0x717fc63d364c0b5e75d40ba13712abc08ec9c6c5ba7d0762703523cbfdcceafd>
