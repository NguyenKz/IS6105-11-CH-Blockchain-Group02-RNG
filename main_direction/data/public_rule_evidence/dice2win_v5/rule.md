# Dice2Win v5 rule evidence

- Source-declared address: `0xD1CEeeeee83F8bCF3BEDad437202b6154E9F5405` on Ethereum.
- Official repository commit: `b0a0412f0301623dc3af2743dcace8e86cc6036b`.
- Source file SHA-256: `775b1fb819998e20838621f8fc4951c64c266d2967f8d1743bca0f68ac2bf49a`.

`placeBet()` records a signed commitment. `settleBet()` verifies `keccak256(reveal)`, verifies the place-block hash and passes both to `settleBetCommon()`. The final dice value is `keccak256(reveal, entropyBlockHash) % modulo`.

The adapter preserves immutable commitment before later block entropy and modulo selection. It omits the croupier signature, house edge, expiry, uncle proof and actual transfer logic.

The latest-state Ethereum RPC returned empty code at the historical address. Without an archive runtime-code retrieval, this candidate remains `RULE_UNCONFIRMED` even though the official source and explorer identify the contract.

Sources:

- <https://github.com/dice2-win/contracts/blob/b0a0412f0301623dc3af2743dcace8e86cc6036b/Dice2Win.sol#L221-L365>
- <https://etherscan.io/address/0xD1CEeeeee83F8bCF3BEDad437202b6154E9F5405>
