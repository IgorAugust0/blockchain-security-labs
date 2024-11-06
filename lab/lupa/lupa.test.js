const {expect} = require('chai')
const {ethers} = require('hardhat')

describe('LUPA', function () {
    let LUPA, lupa, owner, bidder1, bidder2
    const requiredDeposit = ethers.utils.parseEther('1') // 1 ETH
    const biddingDuration = 50 // Blocks
    const prizeValue = ethers.utils.parseEther('10') // 10 ETH

    beforeEach(async function () {
        ;[owner, bidder1, bidder2] = await ethers.getSigners()
        LUPA = await ethers.getContractFactory('LUPA')
        lupa = await LUPA.deploy(biddingDuration, requiredDeposit, {
            value: prizeValue,
        })
        await lupa.deployed()
    })

    describe('Bidding phase', function () {
        it('should accept valid bids with the correct deposit', async function () {
            const commitHash = ethers.utils.keccak256(
                ethers.utils.toUtf8Bytes('secretBid')
            )

            await expect(
                lupa.connect(bidder1).bid(commitHash, {value: requiredDeposit})
            )
                .to.emit(lupa, 'DepositReceived')
                .withArgs(bidder1.address, requiredDeposit)
        })

        it('should revert if the deposit is insufficient', async function () {
            const commitHash = ethers.utils.keccak256(
                ethers.utils.toUtf8Bytes('lowBid')
            )
            const lowDeposit = ethers.utils.parseEther('0.5') // Less than required

            await expect(
                lupa.connect(bidder1).bid(commitHash, {value: lowDeposit})
            ).to.be.revertedWith('InsufficientDeposit')
        })
    })

    describe('Reveal phase', function () {
        const nonce = 'randomNonce'
        const bidValue = 3

        beforeEach(async function () {
            const commitHash = ethers.utils.sha256(
                ethers.utils.defaultAbiCoder.encode(
                    ['bytes32', 'uint256'],
                    [nonce, bidValue]
                )
            )
            await lupa
                .connect(bidder1)
                .bid(commitHash, {value: requiredDeposit})
            await ethers.provider.send('evm_mine', [biddingDuration + 1]) // Simulate end of bidding
        })

        it('should reveal the correct bid', async function () {
            await expect(lupa.connect(bidder1).revealBid(nonce, bidValue))
                .to.emit(lupa, 'AttemptedReveal')
                .withArgs(bidder1.address, requiredDeposit, bidValue, true)
        })

        it('should revert if the reveal is incorrect', async function () {
            await expect(lupa.connect(bidder1).revealBid(nonce, 5)) // Wrong bid value
                .to.emit(lupa, 'AttemptedReveal')
                .withArgs(bidder1.address, requiredDeposit, 5, false)
        })
    })

    describe('Auction results', function () {
        const nonce1 = 'nonce1',
            nonce2 = 'nonce2'
        const bidValue1 = 3,
            bidValue2 = 5

        beforeEach(async function () {
            const commitHash1 = ethers.utils.sha256(
                ethers.utils.defaultAbiCoder.encode(
                    ['bytes32', 'uint256'],
                    [nonce1, bidValue1]
                )
            )
            const commitHash2 = ethers.utils.sha256(
                ethers.utils.defaultAbiCoder.encode(
                    ['bytes32', 'uint256'],
                    [nonce2, bidValue2]
                )
            )

            await lupa
                .connect(bidder1)
                .bid(commitHash1, {value: requiredDeposit})
            await lupa
                .connect(bidder2)
                .bid(commitHash2, {value: requiredDeposit})

            await ethers.provider.send('evm_mine', [biddingDuration + 1]) // Simulate end of bidding
        })

        it('should declare the winner with the lowest unmatched bid', async function () {
            await lupa.connect(bidder1).revealBid(nonce1, bidValue1) // Correct reveal
            await lupa.connect(bidder2).revealBid(nonce2, bidValue2) // Correct reveal

            await expect(() =>
                lupa.connect(bidder1).withdrawDeposit()
            ).to.changeEtherBalance(bidder1, requiredDeposit)

            // Verify the auction winner
            await expect(() =>
                lupa.connect(bidder1).revealBid(nonce1, bidValue1)
            ).to.changeEtherBalance(bidder1, prizeValue)
        })
    })
})
