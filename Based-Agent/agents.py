import json
from swarm import Agent
#from cdp import *
from typing import List, Dict, Any
import os
from openai import OpenAI
from decimal import Decimal
from typing import Union
#import web3
from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from web3.exceptions import ContractLogicError
#from cdp.errors import ApiError, UnsupportedAssetError

API_URL = os.getenv('MAINNET_API_URL')

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
w3 = Web3(Web3.HTTPProvider(API_URL))
account_from = {
    'private_key': PRIVATE_KEY,
    'address': w3.eth.account.from_key(PRIVATE_KEY).address
}

contract_address = "0xb7EA491BEE079bD55D4A69caF6bba53232913BdA"
with open("./ManagerFacet.json") as f:
    manager_json = json.load(f)
with open("./NewTokenFacet.json") as f:
    newtoken_json = json.load(f)
with open("./OwnershipFacet.json") as f:
    ownership_json = json.load(f)
manager_abi = manager_json["abi"]
newtoken_abi = newtoken_json["abi"]
ownership_abi = ownership_json["abi"]

ca_manager = w3.eth.contract(address=contract_address, abi=manager_abi)
ca_newtoken = w3.eth.contract(address=contract_address, abi=newtoken_abi)
ca_ownership = w3.eth.contract(address=contract_address, abi=ownership_abi)
w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
token_launched = ca_manager.events.TokenLaunched()


# Function to create a new ERC-20 token
def create_token(name, symbol, initial_supply):
    """
    Create a new ERC-20 token.
    
    Args:
        name (str): The name of the token
        symbol (str): The symbol of the token
        initial_supply (int): The initial supply of tokens
    
    Returns:
        str: A message confirming the token creation with details
    """
    initial_supply = int(initial_supply)
    if initial_supply < 1000000:
        initial_supply = 1000000
    max_swap = initial_supply / 100
    taxSwapThreshold = initial_supply / 10000
    data = {
        "owner": account_from['address'],
        "taxWallet": account_from['address'],
        "stakingFacet": "0x58d0d610674C69F27B7519a6e2746E8b814548DE",
        "v2router": "0x58d0d610674C69F27B7519a6e2746E8b814548DE",
        "isFreeTier": True,
        "minLiq": 0,
        "supply": initial_supply,
        "initTaxType": 1,
        "initInterval": 30,
        "countInterval": 40,
        "maxBuyTax": 40,
        "minBuyTax": 0,
        "maxSellTax": 40,
        "minSellTax": 0,
        "lpTax": 0,
        "maxWallet": 100,
        "maxTx": 100,
        "preventSwap": 40,
        "maxSwap": max_swap,
        "taxSwapThreshold": taxSwapThreshold,
        "name": name,
        "symbol": symbol
    }
    my_struct = ((account_from['address'], account_from['address'],
                  account_from['address'], account_from['address'], True, 0,
                  initial_supply, 1, 30, 40, 40, 0, 40, 0, 0, 100, 100, 40,
                  int(max_swap), int(taxSwapThreshold), name, symbol))
    # Build the transaction
    txn = ca_manager.functions.launchTokenFree(my_struct).build_transaction({
        'from':
        account_from['address'],
        'nonce':
        w3.eth.get_transaction_count(account_from['address']),
        'gasPrice':
        w3.eth.generate_gas_price()
    })

    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(txn,
                                                 account_from['private_key'])

    # Send the transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    result = token_launched.process_receipt(txn_receipt)

    #print(result[0]['args']['params']['token'])

    return f"Token {name} ({symbol}) created with initial supply of {initial_supply} and contract address {result[0]['args']['params']['token']}"

    #deployed_contract = agent_wallet.deploy_token(name, symbol, initial_supply)
    #deployed_contract.wait()
    #return f"Token {name} ({symbol}) created with initial supply of {initial_supply} and contract address {deployed_contract.contract_address}"


def add_liquidity():
    return f"Added imaginary liquidity"


def set_socials():
    return f"set imaginary socials"


# Create the Based Agent with all available functions
deployyyyer_agent = Agent(
    name="deployyyyer Agent",
    instructions=
    "You are a helpful agent that can interact onchain using deployyyyer. You can deploy ERC20 token contracts, add liquidity and set socials. If you ever need to know your address, it is {account_from['address']}. If someone asks you to do something you can't do, you can say so, and encourage them to implement it themselves using deployyyyer, recommend they go to docs.deployyyyer.io for more informaton. You can also offer to help them implement it by writing the function and telling them to add it to the agents.py file and within your list of callable functions.",
    functions=[
        create_token, set_socials, add_liquidity
        #transfer_asset,
        #get_balance,
        #request_eth_from_faucet,
        #generate_art,  # Uncomment this line if you have configured the OpenAI API
        #deploy_nft,
        #mint_nft,
        #swap_assets,
        #register_basename
    ],
)

# add the following import to the top of the file, add the code below it, and add the new functions to the based_agent.functions list

# from twitter_utils import TwitterBot

# # Initialize TwitterBot with your credentials
# twitter_bot = TwitterBot(
#     api_key="your_api_key",
#     api_secret="your_api_secret",
#     access_token="your_access_token",
#     access_token_secret="your_access_token_secret"
# )

# # Add these new functions to your existing functions list

# def post_to_twitter(content: str):
#     """
#     Post a message to Twitter.
#
#     Args:
#         content (str): The content to tweet
#
#     Returns:
#         str: Status message about the tweet
#     """
#     return twitter_bot.post_tweet(content)

# def check_twitter_mentions():
#     """
#     Check recent Twitter mentions.
#
#     Returns:
#         str: Formatted string of recent mentions
#     """
#     mentions = twitter_bot.read_mentions()
#     if not mentions:
#         return "No recent mentions found"

#     result = "Recent mentions:\n"
#     for mention in mentions:
#         if 'error' in mention:
#             return f"Error checking mentions: {mention['error']}"
#         result += f"- @{mention['user']}: {mention['text']}\n"
#     return result

# def reply_to_twitter_mention(tweet_id: str, content: str):
#     """
#     Reply to a specific tweet.
#
#     Args:
#         tweet_id (str): ID of the tweet to reply to
#         content (str): Content of the reply
#
#     Returns:
#         str: Status message about the reply
#     """
#     return twitter_bot.reply_to_tweet(tweet_id, content)

# def search_twitter(query: str):
#     """
#     Search for tweets matching a query.
#
#     Args:
#         query (str): Search query
#
#     Returns:
#         str: Formatted string of matching tweets
#     """
#     tweets = twitter_bot.search_tweets(query)
#     if not tweets:
#         return f"No tweets found matching query: {query}"

#     result = f"Tweets matching '{query}':\n"
#     for tweet in tweets:
#         if 'error' in tweet:
#             return f"Error searching tweets: {tweet['error']}"
#         result += f"- @{tweet['user']}: {tweet['text']}\n"
#     return result

# ABIs for smart contracts (used in basename registration)
l2_resolver_abi = [{
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "address",
        "name": "a",
        "type": "address"
    }],
    "name":
    "setAddr",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "string",
        "name": "newName",
        "type": "string"
    }],
    "name":
    "setName",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}]

registrar_abi = [{
    "inputs": [{
        "components": [{
            "internalType": "string",
            "name": "name",
            "type": "string"
        }, {
            "internalType": "address",
            "name": "owner",
            "type": "address"
        }, {
            "internalType": "uint256",
            "name": "duration",
            "type": "uint256"
        }, {
            "internalType": "address",
            "name": "resolver",
            "type": "address"
        }, {
            "internalType": "bytes[]",
            "name": "data",
            "type": "bytes[]"
        }, {
            "internalType": "bool",
            "name": "reverseRecord",
            "type": "bool"
        }],
        "internalType":
        "struct RegistrarController.RegisterRequest",
        "name":
        "request",
        "type":
        "tuple"
    }],
    "name":
    "register",
    "outputs": [],
    "stateMutability":
    "payable",
    "type":
    "function"
}]

# To add a new function:
# 1. Define your function above (follow the existing pattern)
# 2. Add appropriate error handling
# 3. Add the function to the based_agent's functions list
# 4. If your function requires new imports or global variables, add them at the top of the file
# 5. Test your new function thoroughly before deploying

# Example of adding a new function:
# def my_new_function(param1, param2):
#     """
#     Description of what this function does.
#
#     Args:
#         param1 (type): Description of param1
#         param2 (type): Description of param2
#
#     Returns:
#         type: Description of what is returned
#     """
#     try:
#         # Your function logic here
#         result = do_something(param1, param2)
#         return f"Operation successful: {result}"
#     except Exception as e:
#         return f"Error in my_new_function: {str(e)}"

# Then add to based_agent.functions:
# based_agent = Agent(
#     ...
#     functions=[
#         ...
#         my_new_function,
#     ],
# )
