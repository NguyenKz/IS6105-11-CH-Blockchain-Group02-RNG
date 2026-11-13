# Fomo3D Long rule evidence

- Deployed address: `0xA62142888ABa8370742bE823c1782D17A0389Da1` on Ethereum.
- Source mirror commit: `5f12c71fe4e9c92142bb0021e0e0da983daf9ceb`.
- Source file SHA-256: `d626428ad003ef937081d95d77722759fe2b742316f19da70e93a2d445f2698e`.
- Observed runtime bytecode: 21,488 bytes; Keccak-256 `0xe588f83d8349f89ec605d5a725f2a693158a8c7eb82b3dec0478465a3b4aeaba`.

`airdrop()` hashes `block.timestamp`, `block.difficulty`, `block.coinbase`, `block.gaslimit`, `msg.sender` and `block.number`. It then compares `seed % 1000` with `airDropTracker_`.

The adapter preserves public-context hashing and modulo selection. It deliberately omits the original tracker, caller-specific threshold, token economics and payout percentages. Therefore replay results describe the adapter, not Fomo3D history.

Sources:

- <https://etherscan.io/address/0xA62142888ABa8370742bE823c1782D17A0389Da1>
- <https://github.com/fanyinghao/Fomo3D/blob/5f12c71fe4e9c92142bb0021e0e0da983daf9ceb/FoMo3Dlong.sol#L1409-L1432>
