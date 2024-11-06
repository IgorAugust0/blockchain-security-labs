import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Transaction:
    hash: str
    fee: Optional[int]
    inputs: int
    outputs: int
    receiving_addresses: List[str]

@dataclass
class Block:
    height: int
    hash: str
    coinbase_tx: Optional[Transaction]
    transactions: List[Transaction]

class BlockchainExplorer:
    BASE_URL = "https://blockchain.info"
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds

    async def get_latest_block(self) -> Block:
        """Fetch the latest block from the blockchain."""
        block_data = await self._make_request(f"{self.BASE_URL}/latestblock")
        block_hash = block_data["hash"]
        block_info = await self.get_block(block_hash)
        return self._build_block(block_info)

    async def get_block(self, block_hash: str) -> dict:
        """Fetch a block by its hash."""
        return await self._make_request(f"{self.BASE_URL}/rawblock/{block_hash}")

    async def _make_request(self, url: str) -> dict:
        """Helper method to handle retries for API requests."""
        async with aiohttp.ClientSession() as session:
            for attempt in range(self.MAX_RETRIES):
                try:
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
                except aiohttp.ClientError as e:
                    if attempt < self.MAX_RETRIES - 1:
                        print(f"Error occurred. Retrying in {self.RETRY_DELAY} seconds...")
                        await asyncio.sleep(self.RETRY_DELAY)
                    else:
                        raise e
        return {"error": "Failed after multiple attempts"}

    def _build_block(self, block_data: dict) -> Block:
        """Construct a Block object from the raw block data."""
        coinbase_tx = self._get_coinbase_transaction(block_data)
        transactions = [
            self._create_transaction(tx) for tx in block_data["tx"] if tx != coinbase_tx
        ]
        return Block(
            height=block_data["height"],
            hash=block_data["hash"],
            coinbase_tx=coinbase_tx,
            transactions=transactions,
        )

    def _get_coinbase_transaction(self, block_data: dict) -> Optional[Transaction]:
        """Retrieve the Coinbase transaction from a block (first transaction)."""
        if block_data["tx"]:
            tx = block_data["tx"][0] # Coinbase transaction is always the first one
            return self._create_transaction(tx)
        return None
    
    def _create_transaction(self, tx: dict) -> Transaction:
        """Create a Transaction object from the raw transaction data."""
        receiving_addresses = [out.get("addr", "unknown") for out in tx["out"] if "addr" in out]
        return Transaction(
            hash=tx["hash"],
            fee=tx["fee"],
            inputs=len(tx.get("inputs", [])),
            outputs=len(tx.get("out", [])),
            receiving_addresses=receiving_addresses,
        )

    def _calculate_fee(self, tx: dict) -> Optional[int]:
        """Calculate the fee paid for a transaction, if possible. Not being used because the API already provides the fee."""
        if "inputs" in tx and "out" in tx:
            total_input = sum(
                input_["prev_out"]["value"]
                for input_ in tx["inputs"]
                if "prev_out" in input_
            )
            total_output = sum(output["value"] for output in tx["out"])
            return total_input - total_output
        return None

async def explore_latest_block(max_transactions: Optional[int] = None):
    """Main function to explore the latest block. Optionally, limit the number of transactions."""
    explorer = BlockchainExplorer()
    latest_block = await explorer.get_latest_block()

    print("=" * 33 + " Block Summary " + "=" * 33 + "\n")
    print(f"Height: {latest_block.height}")
    print(f"Hash: {latest_block.hash}")
    if latest_block.coinbase_tx:
        print(f"Coinbase Transaction Hash: {latest_block.coinbase_tx.hash}")
        print(f"Addresses for Mined Bitcoins + Fees: {latest_block.coinbase_tx.receiving_addresses}") # or .outputs
        print(f"Total number of Transactions: {len(latest_block.transactions) + 1}")
    print()

    print("=" * 30 + " Transaction Details " + "=" * 30 + "\n")
    transactions = latest_block.transactions[:max_transactions] if max_transactions else latest_block.transactions
    for tx in transactions:
        print(f"Transaction Hash: {tx.hash}")
        print(f"  Fee: {tx.fee} satoshis" if tx.fee is not None else "  Fee: Unable to retrieve/calculate fee")
        print(f"  Inputs: {tx.inputs}, Outputs: {tx.outputs}")
        print("-" * 82)
    print()

if __name__ == "__main__":
    # if the output is truncated/cut off in the console, run:
    # python blockchain_explorer1.py > output.txt

    # pass an integer argument to limit the number of transactions displayed
    asyncio.run(explore_latest_block(11))
