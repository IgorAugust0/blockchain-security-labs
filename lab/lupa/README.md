# LUPA (Lowest-Unmatched Price Auction) Smart Contract

## Overview

LUPA is a Solidity implementation of a sealed-bid auction where the lowest unique bid wins. It uses a commit-reveal scheme to ensure bid privacy and prevent manipulation. The contract implements a specialized auction mechanism where bidders submit sealed bids, and the winner is determined by having the lowest bid amount that no other participant matched.

## Features

- **Commit-Reveal Scheme**: Two-phase bidding process to ensure bid privacy
- **Automated Winner Selection**: Smart contract automatically determines the lowest unmatched bid
- **Deposit System**: Required deposits to prevent spam and ensure serious participation
- **State Management**: Clear auction phases (Bid, Reveal, Finished)
- **Security Measures**: Built-in protection against common attack vectors
- **Gas Optimization**: Uses custom errors and efficient data structures

## Contract Structure

The project consists of three main contracts:

1. **LUPA.sol**: Main auction contract
2. **SimpleCommit.sol**: Library for handling bid commitments
3. **HashGenerator.sol**: Helper contract for generating bid commitments

## Requirements

- Solidity ^0.8.19
- Ethereum development environment (Remix IDE, Hardhat, or Truffle)
- MetaMask or similar Web3 wallet for testing

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/IgorAugust0/tesi.git
   cd lab/lupa
   ```

2. **Deploy Contracts**:
   - Deploy SimpleCommit library first
   - Deploy LUPA contract with parameters:
     - `_biddingDuration`: Number of blocks for bidding phase
     - `_requiredDeposit`: Minimum deposit amount in wei

## Usage

### For Auction Creator

```solidity
// Deploy with 100 blocks duration and 1 ETH deposit requirement
LUPA auction = new LUPA{value: 10 ether}(100, 1 ether);
```

### For Bidders

1. **Bidding Phase**:

   ```solidity
   // Generate commitment
   bytes32 commitment = keccak256(abi.encodePacked(nonce, bidValue));

   // Submit bid with required deposit
   auction.bid{value: 1 ether}(commitment);
   ```

2. **Reveal Phase**:

   ```solidity
   // Reveal bid
   auction.revealBid(nonce, bidValue);
   ```

3. **After Auction**:
   ```solidity
   // Non-winners can withdraw deposits
   auction.withdrawDeposit();
   ```

## Key Concepts

- **Lowest Unmatched Price**: The winning bid is the lowest amount that no other bidder matched
- **Commit-Reveal**: Two-phase process prevents bid manipulation:
  - Commit: Submit encrypted bid
  - Reveal: Disclose actual bid value
- **Deposits**: Required to participate, returned to non-winners

## Events

- `DepositReceived`: Tracks received deposits
- `CommitmentStored`: Records bid commitments
- `AttemptedReveal`: Logs bid reveals
- `BidCounted`: Tracks bid processing
- `AuctionFinished`: Announces winner

## Security Considerations

- Sealed bids prevent front-running
- Required deposits prevent spam
- Time-based phases prevent manipulation
- Gas-efficient error handling
- Secure commitment scheme

## Testing Guide

For detailed testing instructions, please refer to the [Testing Guide](./Testing.md).

## License

This project is licensed under the GPL-3.0 [LICENSE](../../LICENSE).
