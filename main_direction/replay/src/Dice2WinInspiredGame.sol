// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @notice Two-player abstraction of Dice2Win's commit-before-block-entropy rule.
/// @dev This omits the croupier, house edge, expiry and reorg proof machinery.
contract Dice2WinInspiredGame {
    uint256 public constant PRIZE_WEI = 1 ether;
    uint256 public constant PARTICIPANT_COUNT = 2;

    uint256 public committedCount;
    uint256 public playCount;
    uint256 public targetIndex;
    bool public targetFinalized;
    bytes32 public entropyBlockHash;
    address public winner;

    mapping(address => bytes32) public commitments;
    mapping(address => uint256) public participantIndex;
    mapping(address => bool) public played;
    address[2] public participants;

    event Commitment(address indexed participant, uint256 indexed participantIndex, bytes32 commitment);
    event EntropyFinalized(bytes32 indexed entropyBlockHash, uint256 targetIndex);
    event Outcome(
        address indexed participant,
        uint256 indexed participantIndex,
        bytes32 entropy,
        uint256 targetIndex,
        bool won
    );

    function commit(bytes32 commitment_) external {
        require(!targetFinalized, "entropy already finalized");
        require(commitment_ != bytes32(0), "missing commitment");
        require(committedCount < PARTICIPANT_COUNT, "commitments complete");
        require(commitments[msg.sender] == bytes32(0), "already committed");

        uint256 index = committedCount;
        commitments[msg.sender] = commitment_;
        participantIndex[msg.sender] = index;
        participants[index] = msg.sender;
        committedCount = index + 1;
        emit Commitment(msg.sender, index, commitment_);
    }

    function finalizeEntropy(bytes32 entropyBlockHash_) external {
        require(committedCount == PARTICIPANT_COUNT, "commitments incomplete");
        require(!targetFinalized, "entropy already finalized");
        require(entropyBlockHash_ != bytes32(0), "missing entropy");

        entropyBlockHash = entropyBlockHash_;
        targetIndex = uint256(
            keccak256(
                abi.encode(
                    commitments[participants[0]],
                    commitments[participants[1]],
                    entropyBlockHash_
                )
            )
        ) % PARTICIPANT_COUNT;
        targetFinalized = true;
        emit EntropyFinalized(entropyBlockHash_, targetIndex);
    }

    function play(bytes32 secret) external returns (uint256 participantIndex_, bool won) {
        require(targetFinalized, "entropy not finalized");
        require(!played[msg.sender], "already played");
        require(keccak256(abi.encode(secret)) == commitments[msg.sender], "invalid reveal");

        participantIndex_ = participantIndex[msg.sender];
        bytes32 entropy = keccak256(
            abi.encode(
                commitments[participants[0]],
                commitments[participants[1]],
                entropyBlockHash
            )
        );
        won = participantIndex_ == targetIndex;
        if (won) {
            winner = msg.sender;
        }

        played[msg.sender] = true;
        playCount += 1;
        emit Outcome(msg.sender, participantIndex_, entropy, targetIndex, won);
    }
}
