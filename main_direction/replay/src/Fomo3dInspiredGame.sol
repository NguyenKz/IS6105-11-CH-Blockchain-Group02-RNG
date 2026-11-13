// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @notice Two-player abstraction of Fomo3D's public-context hash and modulo rule.
/// @dev This is a synthetic adapter, not the deployed Fomo3D contract.
contract Fomo3dInspiredGame {
    uint256 public constant PRIZE_WEI = 1 ether;
    uint256 public constant PARTICIPANT_COUNT = 2;

    bytes32 public immutable publicEntropy;
    uint256 public immutable targetIndex;
    address public immutable attacker;

    uint256 public turn;
    address public winner;

    event Outcome(
        address indexed participant, uint256 indexed turnIndex, bytes32 entropy, uint256 targetIndex, bool attackerWon
    );

    constructor(
        bytes32 sourceBlockHash,
        uint256 sourceTimestamp,
        uint256 sourceDifficulty,
        address sourceCoinbase,
        uint256 sourceGasLimit,
        uint256 sourceBlockNumber,
        address attacker_
    ) {
        require(sourceBlockHash != bytes32(0), "missing block hash");
        require(attacker_ != address(0), "missing attacker");

        publicEntropy = keccak256(
            abi.encode(
                sourceBlockHash,
                sourceTimestamp,
                sourceDifficulty,
                sourceCoinbase,
                sourceGasLimit,
                sourceBlockNumber
            )
        );
        targetIndex = uint256(publicEntropy) % PARTICIPANT_COUNT;
        attacker = attacker_;
    }

    function play(uint256) external returns (uint256 turnIndex, bool attackerWon) {
        require(turn < PARTICIPANT_COUNT, "round complete");

        turnIndex = turn;
        attackerWon = msg.sender == attacker && turnIndex == targetIndex;
        if (turnIndex == targetIndex) {
            winner = msg.sender;
        }

        turn = turnIndex + 1;
        emit Outcome(msg.sender, turnIndex, publicEntropy, targetIndex, attackerWon);
    }
}
