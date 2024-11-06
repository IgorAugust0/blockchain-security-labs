// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

import "./SimpleCommit.sol";
using SimpleCommit for SimpleCommit.CommitType;

contract LUPA {
    enum LUPAStates {
        Bid,
        Payment,
        Finished
    }

    struct BidValue {
        uint value; // Bid value
        bool isUnmatched; // Whether the bid is unmatched
        uint biddersCount; // Number of bidders with this value
    }

    // Mappings for bids and commitments
    mapping(uint => BidValue) public bids;
    mapping(address => SimpleCommit.CommitType) public players;

    uint public immutable blockLimit; // Time limit for the bidding phase
    uint public immutable prizeValue; // Prize value, set once in constructor
    address public immutable owner; // Contract owner

    LUPAStates public currentState; // Current state of the contract

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can execute this.");
        _;
    }

    modifier inState(LUPAStates _state) {
        require(currentState == _state, "Invalid state for this action.");
        _;
    }

    modifier withinBlockLimit() {
        if (block.number > blockLimit) {
            currentState = LUPAStates.Payment;
        }
        _;
    }

    modifier validValue() {
        require(msg.value > 0 && msg.value < 10e18, "Invalid bid value.");
        _;
    }

    constructor(uint biddingDuration) payable {
        require(msg.value > 0, "Initial prize must be a positive value.");
        blockLimit = block.number + biddingDuration;
        prizeValue = msg.value;
        owner = msg.sender;
        currentState = LUPAStates.Bid;
    }

    /**
     * @notice Commit a bid during the bidding phase
     * @param commitHash Hash of the bid value and a nonce
     */
    function bid(
        bytes32 commitHash
    ) public payable inState(LUPAStates.Bid) validValue withinBlockLimit {
        SimpleCommit.CommitType storage player = players[msg.sender];
        player.commit(commitHash);
        players[msg.sender] = player; // Store player's commit

        BidValue storage bidEntry = bids[msg.value];

        if (bidEntry.value == 0) {
            // First bidder at this value
            bidEntry.value = msg.value;
            bidEntry.biddersCount = 1;
            bidEntry.isUnmatched = true;
        } else {
            // Multiple bidders at the same value
            bidEntry.biddersCount += 1;
            bidEntry.isUnmatched = false;
        }
    }

    /**
     * @notice Reveal a bid during the payment phase
     * @param nonce The nonce used in the commit-reveal process
     * @param bidValue The actual bid value
     */
    function revealBid(
        bytes32 nonce,
        uint bidValue
    ) public inState(LUPAStates.Payment) withinBlockLimit {
        SimpleCommit.CommitType storage player = players[msg.sender];
        require(player.isCommitted(), "No bid to reveal.");

        player.reveal(nonce, bidValue);
        require(
            player.isCorrect(),
            "Revealed bid does not match the commitment."
        );

        // If player's bid was correct and unmatched, they receive the prize
        if (bids[bidValue].isUnmatched && player.isCorrect()) {
            payable(msg.sender).transfer(prizeValue);
            currentState = LUPAStates.Finished;
        }
    }

    /**
     * @notice Find the lowest unmatched bid during the payment phase
     * @return The lowest unmatched bid value, or -1 if none found
     */
    function findLowestUnmatchedBid()
        public
        view
        inState(LUPAStates.Payment)
        returns (int256)
    {
        for (uint i = 0; i < 10e18; i++) {
            BidValue storage bidEntry = bids[i];
            if (bidEntry.isUnmatched) {
                return int256(bidEntry.value);
            }
        }
        return -1;
    }

    /**
     * @notice End the bidding phase and transition to the payment phase
     */
    function finishAuction() public onlyOwner inState(LUPAStates.Bid) {
        currentState = LUPAStates.Payment;
    }

    /**
     * @notice Verify if the bidding phase is finished based on block number
     */
    function verifyTimeLimit() internal {
        if (block.number > blockLimit) {
            currentState = LUPAStates.Payment;
        }
    }
}
