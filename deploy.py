from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
print("Installing...")
install_solc("0.6.0")


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile our Solididty contract

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)
# Save comiled contract to json file
with open("compiled_code.json", "w") as file:
    file.write(json.dumps(compiled_sol))

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect to local testrpc
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
chain_id = w3.eth.chainId
my_address = os.getenv("MY_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

# Create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)
# Build transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# Sign transaction
signed_txn = w3.eth.account.signTransaction(transaction, private_key)
# Send transaction
tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Working with contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve())
