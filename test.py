import json

from web3 import Web3
def send_amount_contract(address,times, amounts):
    # verify that the amount is an integer or floating value

    # update the blockchain and sync to mysql
    web3_provider = Web3.HTTPProvider('HTTP://127.0.0.1:7545')
    web3 = Web3(web3_provider)
    contract_address = web3.to_checksum_address("0x21438DA416E0bE889DB8E8d22EF28134c54fC4e6")

    abi = json.loads(
        '[{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"consomations","outputs":[{"internalType":"uint256","name":"time","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getConsomation","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"}],"name":"getProfile","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sendConsomation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"times","type":"uint256[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"sendConsomation_csv","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"},{"internalType":"string","name":"newProfile","type":"string"}],"name":"updateProfile","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"users","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]')
    contract = web3.eth.contract(address=contract_address, abi=abi)

    # Specify the 'from' address for the transaction

        # update the blockchain and sync to MySQL

        # Specify the 'from' address for the transaction
    web3.eth.default_account = address

        # Build the transaction data
    address = contract.functions.getAddress().call()
    hash_value = contract.functions.getHash().call()
    # Add other function calls to fetch more data from the smart contract as needed
    return address, hash_value




print(send_amount_contract("0x9E3d82d44Bd0de3a5d1362E16aC8601F662e5F13",[5,4,3],[5,4,3]))
print()