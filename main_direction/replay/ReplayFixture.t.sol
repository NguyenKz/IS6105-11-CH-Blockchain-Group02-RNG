// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {CommitBeforeEntropyGame} from "../src/CommitBeforeEntropyGame.sol";
import {Dice2WinInspiredGame} from "../src/Dice2WinInspiredGame.sol";
import {Fomo3dInspiredGame} from "../src/Fomo3dInspiredGame.sol";
import {WeakContextRngGame} from "../src/WeakContextRngGame.sol";

interface Vm {
    function prank(address sender) external;
    function snapshotState() external returns (uint256 snapshotId);
    function revertToState(uint256 snapshotId) external returns (bool success);
}

contract ReplayFixtureTest {
    Vm internal constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));

    bytes32 internal constant PINNED_BLOCK_HASH = 0x58a593cca45d16077845890739c4d4e17b226e84879cd7201ad80a913360273e;
    bytes32 internal constant HONEST_SECRET = 0x1111111111111111111111111111111111111111111111111111111111111111;
    bytes32 internal constant ATTACKER_SECRET = 0x2222222222222222222222222222222222222222222222222222222222222222;
    bytes32 internal constant HONEST_COMMITMENT = 0xb569321de72d0af89c2fb48a484de3fc9343f31600ae1f3e13d633cb48cbf816;
    bytes32 internal constant ATTACKER_COMMITMENT = 0xc4bd59e1394781d1c7bf20a2c0b30c2acc9fbdd52dc5e0d76917de4034ebdf59;

    address internal constant HONEST = address(0x1001);
    address internal constant ATTACKER = address(0x2002);

    function testWeakOrderChangesWinner() external {
        WeakContextRngGame game = new WeakContextRngGame(PINNED_BLOCK_HASH, ATTACKER);
        uint256 snapshotId = vm.snapshotState();

        vm.prank(HONEST);
        game.play(0);
        vm.prank(ATTACKER);
        game.play(1);
        address canonicalWinner = game.winner();

        require(vm.revertToState(snapshotId), "snapshot restore failed");

        vm.prank(ATTACKER);
        game.play(1);
        vm.prank(HONEST);
        game.play(0);
        address counterfactualWinner = game.winner();

        require(canonicalWinner != counterfactualWinner, "order did not change winner");
    }

    function testSafeOrderDoesNotChangeWinner() external {
        CommitBeforeEntropyGame game = _committedSafeGame();
        uint256 snapshotId = vm.snapshotState();

        vm.prank(HONEST);
        game.play(HONEST_SECRET);
        vm.prank(ATTACKER);
        game.play(ATTACKER_SECRET);
        address canonicalWinner = game.winner();

        require(vm.revertToState(snapshotId), "snapshot restore failed");

        vm.prank(ATTACKER);
        game.play(ATTACKER_SECRET);
        vm.prank(HONEST);
        game.play(HONEST_SECRET);
        address counterfactualWinner = game.winner();

        require(canonicalWinner == counterfactualWinner, "safe reference changed winner");
    }

    function testCommitCannotBeChanged() external {
        CommitBeforeEntropyGame game = new CommitBeforeEntropyGame(PINNED_BLOCK_HASH);

        bool reverted;
        vm.prank(HONEST);
        game.commit(HONEST_COMMITMENT);
        require(!game.targetFinalized(), "entropy finalized too early");
        vm.prank(HONEST);
        try game.commit(ATTACKER_COMMITMENT) {
            reverted = false;
        } catch {
            reverted = true;
        }

        require(reverted, "commitment was mutable");
        vm.prank(ATTACKER);
        game.commit(ATTACKER_COMMITMENT);
        require(game.targetFinalized(), "entropy was not finalized");
    }

    function testSnapshotRestoresWeakState() external {
        WeakContextRngGame game = new WeakContextRngGame(PINNED_BLOCK_HASH, ATTACKER);
        uint256 snapshotId = vm.snapshotState();

        vm.prank(HONEST);
        game.play(0);
        require(game.turn() == 1, "weak state did not advance");

        require(vm.revertToState(snapshotId), "snapshot restore failed");
        require(game.turn() == 0, "weak state leaked across branches");
    }

    function testFomoInspiredRuleIsInputIndependentAndOrderSensitive() external {
        Fomo3dInspiredGame game = new Fomo3dInspiredGame(
            PINNED_BLOCK_HASH,
            1_700_000_000,
            2,
            address(0x3003),
            30_000_000,
            125_053_984,
            ATTACKER
        );
        uint256 snapshotId = vm.snapshotState();

        vm.prank(HONEST);
        game.play(7);
        vm.prank(ATTACKER);
        game.play(99);
        address canonicalWinner = game.winner();

        require(vm.revertToState(snapshotId), "snapshot restore failed");

        vm.prank(ATTACKER);
        game.play(0);
        vm.prank(HONEST);
        game.play(0);
        address counterfactualWinner = game.winner();

        require(canonicalWinner != counterfactualWinner, "order did not change winner");
    }

    function testDiceInspiredFinalizesAfterCommitmentsAndResistsPlayReorder() external {
        Dice2WinInspiredGame game = new Dice2WinInspiredGame();

        vm.prank(HONEST);
        game.commit(HONEST_COMMITMENT);
        require(!game.targetFinalized(), "entropy finalized after first commitment");
        vm.prank(ATTACKER);
        game.commit(ATTACKER_COMMITMENT);
        require(!game.targetFinalized(), "entropy finalized before explicit finalization");
        game.finalizeEntropy(PINNED_BLOCK_HASH);
        require(game.targetFinalized(), "entropy was not finalized");

        uint256 snapshotId = vm.snapshotState();
        vm.prank(HONEST);
        game.play(HONEST_SECRET);
        vm.prank(ATTACKER);
        game.play(ATTACKER_SECRET);
        address canonicalWinner = game.winner();

        require(vm.revertToState(snapshotId), "snapshot restore failed");

        vm.prank(ATTACKER);
        game.play(ATTACKER_SECRET);
        vm.prank(HONEST);
        game.play(HONEST_SECRET);
        address counterfactualWinner = game.winner();

        require(canonicalWinner == counterfactualWinner, "play order changed finalized winner");
    }

    function testDiceInspiredCommitmentCannotChange() external {
        Dice2WinInspiredGame game = new Dice2WinInspiredGame();
        bool reverted;

        vm.prank(HONEST);
        game.commit(HONEST_COMMITMENT);
        vm.prank(HONEST);
        try game.commit(ATTACKER_COMMITMENT) {
            reverted = false;
        } catch {
            reverted = true;
        }

        require(reverted, "commitment was mutable");
    }

    function _committedSafeGame() internal returns (CommitBeforeEntropyGame game) {
        game = new CommitBeforeEntropyGame(PINNED_BLOCK_HASH);

        vm.prank(HONEST);
        game.commit(HONEST_COMMITMENT);
        vm.prank(ATTACKER);
        game.commit(ATTACKER_COMMITMENT);
    }
}
