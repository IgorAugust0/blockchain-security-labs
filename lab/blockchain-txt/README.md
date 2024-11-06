# Simple Blockchain Mining Script

A basic Python script that demonstrates the concept of Proof of Work (PoW) mining in blockchain technology.

## Description

This script simulates the mining process of a blockchain block by:

- Combining block data (height, author, previous block hash)
- Finding a valid Proof of Work that results in a hash starting with 7 zeros
- Using SHA-256 for hash generation

## Requirements

```python
import hashlib  # Built-in Python library
```

## Usage

1. Set the block parameters at the top of the script:

```python
block_height = 14
block_author = "igoraugusto"
previous_block_hash = "00000000b3e790dd97874c54f6126fd9f42ad484c9a33de0587e2167bbcb2550"
```

2. Run the script:

```bash
python blockchaintxt.py
```

3. The script will output:

- The mined block data
- The resulting hash that starts with "0000000"

## How it Works

The script uses a brute-force approach to find a Proof of Work value that, when combined with the block data, produces a hash with seven leading zeros. This simulates the mining difficulty mechanism used in real blockchain networks.
