// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.19;

import "./SimpleCommit.sol";
using SimpleCommit for SimpleCommit.CommitType;

/**
 * @title LUPA (Lowest-Unmatched Price Auction)
 * @notice An implementation of a sealed-bid auction where the lowest unique bid wins
 * @dev Uses a commit-reveal scheme to ensure bid privacy and prevent manipulation
 */
contract LUPA {
    // Custom errors for gas-efficient error handling
    error InvalidState();
    error InvalidValue();
    error NotOwner();
    error NoBidToReveal();
    error IncorrectReveal();
    error InsufficientDeposit();
    error NoDepositToWithdraw();
    error AuctionNotFinished();

    // Events for tracking auction activity
    event DepositReceived(address indexed bidder, uint256 depositAmount);
    event CommitmentStored(address indexed bidder, bytes32 commitHash);
    event AttemptedReveal(
        address indexed bidder,
        uint256 originalDeposit,
        uint256 revealedBid,
        bool isCorrect
    );
    event BidCounted(uint256 bidValue, uint256 bidderCount, bool isUnmatched);
    event AuctionFinished(address indexed winner, uint256 winningBid);

    // Auction states
    enum State {
        Bid, // Bidding phase
        Reveal, // Reveal phase
        Finished // Auction finished
    }

    // Stores information about bids at each price point
    struct BidValue {
        uint96 biddersCount; // Number of bidders at this price
        bool isUnmatched; // True if only one bidder at this price
    }

    // Stores individual bidder information
    struct PlayerInfo {
        SimpleCommit.CommitType commitment; // Bid commitment
        uint96 deposit; // Deposited ETH
        bool hasWithdrawn; // Whether deposit was withdrawn
    }

    // State variables
    State public currentState; // Current auction state
    uint48 public immutable endBlock; // Block number when bidding ends
    address public immutable owner; // Auction creator
    uint96 public immutable prizeValue; // Amount to be won
    uint96 public immutable requiredDeposit; // Required deposit to participate

    // Mappings
    mapping(uint256 => BidValue) public bids; // Tracks bids at each price
    mapping(address => PlayerInfo) public players; // Tracks individual bidder info

    /**
     * @dev Ensures function is called in the correct auction state
     */
    modifier onlyState(State _state) {
        if (getState() != _state) revert InvalidState();
        _;
    }

    /**
     * @notice Initializes the auction
     * @param _biddingDuration Number of blocks the bidding phase will last
     * @param _requiredDeposit Amount of ETH required as deposit
     * @dev The constructor is payable and the sent ETH becomes the prize
     */
    constructor(uint48 _biddingDuration, uint96 _requiredDeposit) payable {
        // Validate inputs
        if (msg.value == 0) revert InvalidValue();
        if (_requiredDeposit == 0) revert InvalidValue();

        // Initialize auction parameters
        owner = msg.sender;
        endBlock = uint48(block.number) + _biddingDuration;
        prizeValue = uint96(msg.value);
        requiredDeposit = _requiredDeposit;
        currentState = State.Bid;
    }

    /**
     * @notice Submit a bid commitment
     * @param commitHash Keccak256 hash of bid value and nonce
     * @dev Requires sending the required deposit amount
     */
    function bid(bytes32 commitHash) external payable onlyState(State.Bid) {
        // Ensure sufficient deposit
        if (msg.value < requiredDeposit) revert InsufficientDeposit();

        // Store player information
        PlayerInfo storage player = players[msg.sender];
        player.commitment.commit(commitHash);
        player.deposit = uint96(msg.value);

        // Emit events for deposit and commitment
        emit DepositReceived(msg.sender, msg.value);
        emit CommitmentStored(msg.sender, commitHash);
    }

    /**
     * @notice Reveal a previously committed bid
     * @param nonce Random value used in commitment
     * @param bidValue Original bid value
     * @dev Incorrect reveals forfeit deposit
     */
    function revealBid(
        bytes32 nonce,
        uint256 bidValue
    ) external onlyState(State.Reveal) {
        // Retrieve player information
        PlayerInfo storage player = players[msg.sender];
        if (!player.commitment.isCommitted()) revert NoBidToReveal();

        uint256 originalDeposit = player.deposit;

        // Reveal the bid
        player.commitment.reveal(nonce, bidValue);
        bool isCorrect = player.commitment.isCorrect();

        // Emit event for attempted reveal
        emit AttemptedReveal(msg.sender, originalDeposit, bidValue, isCorrect);

        // Handle incorrect reveals
        if (!isCorrect) {
            player.hasWithdrawn = true;
            return;
        }

        // Process correct reveals
        BidValue storage bidEntry = bids[bidValue];
        if (bidEntry.biddersCount == 0) {
            // First bid at this value
            bidEntry.biddersCount = 1;
            bidEntry.isUnmatched = true;
        } else {
            unchecked {
                bidEntry.biddersCount++;
            }
            bidEntry.isUnmatched = false;
        }

        emit BidCounted(bidValue, bidEntry.biddersCount, bidEntry.isUnmatched);

        // Finish auction if bid is unmatched
        if (bidEntry.isUnmatched) {
            _finishAuction(msg.sender, bidValue);
        }
    }

    /**
     * @notice Withdraw deposit after auction ends
     * @dev Can only be called after bidding phase and if deposit hasn't been withdrawn
     */
    function withdrawDeposit() external {
        // Check auction state
        State currentAuctionState = getState();
        if (currentAuctionState == State.Bid) revert AuctionNotFinished();

        // Retrieve player information
        PlayerInfo storage player = players[msg.sender];
        if (player.deposit == 0 || player.hasWithdrawn)
            revert NoDepositToWithdraw();

        // Process withdrawal
        uint96 depositAmount = player.deposit;
        player.deposit = 0;
        player.hasWithdrawn = true;

        // Transfer deposit back to player
        payable(msg.sender).transfer(depositAmount);
    }

    /**
     * @notice Get the current state of the auction
     * @return Current auction state
     */
    function getState() public view returns (State) {
        if (currentState == State.Finished) return State.Finished;
        if (block.number > endBlock) return State.Reveal;
        return currentState;
    }

    /**
     * @dev Internal function to finalize the auction
     * @param winner Address of the auction winner
     * @param winningBid Value of the winning bid
     */
    function _finishAuction(address winner, uint256 winningBid) private {
        currentState = State.Finished;

        // Transfer prize and mark deposit as withdrawn
        payable(winner).transfer(prizeValue);
        PlayerInfo storage winnerInfo = players[winner];
        winnerInfo.hasWithdrawn = true;

        emit AuctionFinished(winner, winningBid);
    }
}
