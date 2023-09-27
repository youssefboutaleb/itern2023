from web3 import Web3, HTTPProvider

# Setup
alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/ETibxxHb8A1gqOu_4hLMVhX5VI31v7oi"
web3 = Web3(HTTPProvider(alchemy_url))

# Your account details
my_address = '0x998F8D37669199d9171c704791661a4Aa3024eF8'
my_private_key = 'your-private-key'  # Replace with your private key

# Contract details
contract_address = web3.to_checksum_address("0x87c68B642c5A9ab7b42B11717E9ef4B5c0e475A8") # Replace with your contract's address
abi = '[{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"sendConsomation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256[]","name":"times","type":"uint256[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"sendConsomation_csv","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"},{"internalType":"string","name":"newProfile","type":"string"}],"name":"updateProfile","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"consomations","outputs":[{"internalType":"uint256","name":"time","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getConsomation","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"},{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"userAddress","type":"address"}],"name":"getProfile","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"users","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}]'


# Create a contract object
contract = web3.eth.contract(address=contract_address, abi=abi)

# Call a function (example: getProfile)
user_profile = contract.functions.getProfile(my_address).call()
print(user_profile)

# Send a transaction (example: updateProfile)
transaction = contract.functions.updateProfile(my_address, 'new-profile').transact()

# Sign the transaction
tx_receipt = web3.eth.wait_for_transaction_receipt(transaction)

# Send the transaction
Contract = web3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi
    )
print(f'Transaction hash: {Contract}')
