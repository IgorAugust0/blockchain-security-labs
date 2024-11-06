import hashlib

# height;author;previous_block_hash;proof_of_work
block_height = 14
block_author = "igoraugusto"
previous_block_hash = "00000000b3e790dd97874c54f6126fd9f42ad484c9a33de0587e2167bbcb2550"

pre = f"{block_height};{block_author};{previous_block_hash};"
proof_of_work = 1

while True:
    temp = pre + str(proof_of_work)
    hash_result = hashlib.sha256(temp.encode()).hexdigest()
    if hash_result[:7] == "0000000":
        break
    proof_of_work += 1

print(f"Bloco minerado: {temp}")
print(f"Hash: {hash_result}")
# print(f"Proof of Work: {proof_of_work}")
