add to the testing guide the missing information/instructions from the original version, that is, be more detailed in the current like it was in the original, give the complete:

# LUPA Contract Testing Guide

## Setup in Remix IDE

1. **Open Remix IDE**

   - Go to [https://remix.ethereum.org/](https://remix.ethereum.org/)
   - Create four new files in the File Explorer:
     - `SimpleCommit.sol`
     - `LUPA.sol`
     - `HashGenerator.sol`

2. **Paste Code**

   - In `SimpleCommit.sol`, paste the following:

     ```solidity
     // SPDX-License-Identifier: GPL-3.0
     pragma solidity ^0.8.19;

     library SimpleCommit {
         enum CommitStatesType {
             Waiting,
             Revealed
         }

         struct CommitType {
             bytes32 commited;
             uint value;
             bool verified;
             CommitStatesType myState;
         }

         function commit(CommitType storage c, bytes32 h) public {
             c.commited = h;
             c.verified = false;
             c.myState = CommitStatesType.Waiting;
         }

         function reveal(CommitType storage c, bytes32 nonce, uint v) public {
             require(c.myState == CommitStatesType.Waiting);
             bytes32 ver = sha256(abi.encodePacked(nonce, v));
             c.myState = CommitStatesType.Revealed;
             if (ver == c.commited) {
                 c.verified = true;
                 c.value = v;
             }
         }

         function isCommitted(CommitType storage c) public view returns (bool) {
             return c.commited != bytes32(0);
         }

         function isCorrect(CommitType storage c) public view returns (bool) {
             require(c.myState == CommitStatesType.Revealed, "Wait!");
             return c.verified;
         }

         function getValue(CommitType storage c) public view returns (uint) {
             require(c.myState == CommitStatesType.Revealed);
             require(c.verified == true);
             return c.value;
         }
     }
     ```

   - In `LUPA.sol`, paste the contract code from the original file
   - In `HashGenerator.sol`, paste the following:

     ```solidity
     // SPDX-License-Identifier: MIT
     pragma solidity ^0.8.0;

     contract HashGenerator {
         function generateCommitment(uint256 nonce, uint256 bidValue)
             public
             pure
             returns (bytes32)
         {
             return keccak256(abi.encodePacked(nonce, bidValue));
         }
     }
     ```

3. **Compile the Contracts**
   - Select Solidity Compiler in the left sidebar (icon looks like "S")
   - Choose compiler version 0.8.19
   - Click "Compile SimpleCommit.sol"
   - Click "Compile LUPA.sol"
   - Click "Compile HashGenerator.sol"
   - Ensure all compile without errors

## Deployment

1. **Select Environment**

   - Click on "Deploy & Run Transactions" in the left sidebar (icon looks like "<")
   - In the "ENVIRONMENT" dropdown, select "Remix VM (Shanghai)"

2. **Deploy SimpleCommit Library First**

   - In the "Contract" dropdown, select "SimpleCommit"
   - Click "Deploy"
   - Note the deployed address (you'll see it under "Deployed Contracts")

3. **Deploy LUPA Contract**

   - In the "Contract" dropdown, select "LUPA"
   - Before deploying, you need to set the constructor parameters:
     - `_biddingDuration`: Enter 100 (this is number of blocks)
     - `_requiredDeposit`: Enter 1000000000000000000 (1 ether in wei)
   - In the "Value" field above the Deploy button, enter 10000000000000000000 (10 ether - this will be the prize)
   - Click "Deploy"

4. **Deploy HashGenerator Contract**
   - In the "Contract" dropdown, select "HashGenerator"
   - Click "Deploy"

## Testing the Contract

### Phase 1: Bidding

1. **Prepare Bid Values**

   - We'll simulate two bidders with different values
   - For each bid, we need:
     - A nonce (random value)
     - The actual bid value
     - A commitment hash

2. **Calculate Bid Commitments**
   Use the `HashGenerator` contract to calculate the commitment hashes:

   ```solidity
   // Deploy the HashGenerator contract and use it to generate commitment hashes
   HashGenerator hashGen = HashGenerator(deployedAddress);

   bytes32 commitment1 = hashGen.generateCommitment(0x0000000000000000000000000000000000000000000000000000000000000001, 5000000000000000000);
   bytes32 commitment2 = hashGen.generateCommitment(0x0000000000000000000000000000000000000000000000000000000000000002, 7000000000000000000);
   ```

3. **Submit Bids**
   For each bid:
   - In Remix, select a different account address
   - Set "Value" to 1000000000000000000 (1 ether - the required deposit)
   - Call the `bid` function with the commitment hash
   - Repeat for the second bidder

### Phase 2: Reveal

1. **Move to Reveal Phase**

   - In Remix, click on the "Deploy & Run Transactions" tab
   - Click on the two up/down arrows next to the account address
   - Select "Remix VM (Shanghai)"
   - Click on the blue "+" icon next to it to mine a new block
   - Repeat about 100 times to pass the bidding duration

2. **Reveal Bids**
   For each bid:

   - Switch to the appropriate account
   - Call `revealBid` with:
     - nonce (the one used for that bidder)
     - bidValue (the actual bid value used)

3. **Check Results**
   - Call `findLowestUnmatchedBid` to see the winning bid
   - The account with that bid value should be able to claim the prize

## Expected Behaviors

1. **During Bidding**

   - All deposits should be 1 ETH
   - Bids less than 1 ETH should fail
   - Can't reveal during bidding phase

2. **During Reveal**

   - Can't place new bids
   - Incorrect reveals lose deposit
   - Correct reveals update bid counts

3. **After Auction**
   - Winner gets prize automatically
   - Non-winners can withdraw deposits

## Step-by-Step Interaction Example

1. **Start Bidding**

   ```solidity
   Account 1:
   - Select Account 1 from dropdown
   - Set Value to 1 ETH
   - Call bid() with commitment hash
   - Should see transaction succeed

   Account 2:
   - Switch to Account 2
   - Set Value to 1 ETH
   - Call bid() with different commitment hash
   - Should see transaction succeed
   ```

2. **Move to Reveal Phase**

   - Mine 100 blocks
   - Call getState() - should return 1 (Reveal state)

3. **Reveal Bids**

   ```solidity
   Account 1:
   - Switch back to Account 1
   - Call revealBid with:
     - nonce: 0x0000000000000000000000000000000000000000000000000000000000000001
     - bidValue: 5000000000000000000

   Account 2:
   - Switch to Account 2
   - Call revealBid with:
     - nonce: 0x0000000000000000000000000000000000000000000000000000000000000002
     - bidValue: 7000000000000000000
   ```

4. **Check Results**
   - Call findLowestUnmatchedBid
   - Winning bid gets prize automatically
   - Other account can withdraw deposit

## Troubleshooting

Common issues:

1. "Invalid state" error: Make sure you're in the correct phase
2. "Insufficient deposit" error: Check you're sending exactly 1 ETH
3. Reveal fails: Double check nonce and bid value match original commitment

## Privacy Verification

To verify bid privacy:

1. Use different accounts to place bids
2. Observe that all transactions show 1 ETH value
3. Try to guess bid values before reveal - should be impossible
4. Only during reveal phase are actual bid values visible
