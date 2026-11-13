// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @notice Minimal safe-reference fixture with commitments before play.
/// @dev The same participant set and payoff rule are used as the weak fixture.
contract CommitBeforeEntropyGame {
    uint256 public constant PRIZE_WEI = 1 ether;
    uint256 public constant PARTICIPANT_COUNT = 2;

    bytes32 public immutable pinnedBlockHash;
    uint256 public committedCount;
    uint256 public playCount;
    uint256 public targetIndex;
    bool public targetFinalized;
    address public winner;

    mapping(address => bytes32) public commitments;
    mapping(address => uint256) public participantIndex;
    mapping(address => bool) public played;
    address[2] public participants;

    event Commitment(address indexed participant, uint256 indexed participantIndex, bytes32 commitment);
    event Outcome(
        address indexed participant,
        uint256 indexed participantIndex,
        bytes32 entropy,
        uint256 targetIndex,
        bool attackerWon
    );

    constructor(bytes32 blockHash_) {
        require(blockHash_ != bytes32(0), "missing block hash");
        pinnedBlockHash = blockHash_;
    }

    function commit(bytes32 commitment_) external {
        require(commitment_ != bytes32(0), "missing commitment");
        require(committedCount < PARTICIPANT_COUNT, "commitments complete");
        require(commitments[msg.sender] == bytes32(0), "already committed");

        uint256 index = committedCount;
        commitments[msg.sender] = commitment_;
        participantIndex[msg.sender] = index;
        participants[index] = msg.sender;
        committedCount = index + 1;

        if (committedCount == PARTICIPANT_COUNT) {
            targetIndex = uint256(
                keccak256(abi.encode(pinnedBlockHash, commitments[participants[0]], commitments[participants[1]]))
            ) % PARTICIPANT_COUNT;
            targetFinalized = true;
        }

        emit Commitment(msg.sender, index, commitment_);
    }

    function play(bytes32 secret) external returns (uint256 participantIndex_, bool won) {
        require(committedCount == PARTICIPANT_COUNT, "commitments incomplete");
        require(!played[msg.sender], "already played");
        require(keccak256(abi.encode(secret)) == commitments[msg.sender], "invalid reveal");

        participantIndex_ = participantIndex[msg.sender];
        bytes32 entropy =
            keccak256(abi.encode(pinnedBlockHash, commitments[participants[0]], commitments[participants[1]]));
        won = participantIndex_ == targetIndex;
        if (won) {
            winner = msg.sender;
        }

        played[msg.sender] = true;
        playCount += 1;
        emit Outcome(msg.sender, participantIndex_, entropy, targetIndex, won);
    }
}
