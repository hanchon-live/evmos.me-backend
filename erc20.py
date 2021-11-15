import json
import os
import pathlib

from web3 import Web3

WEB3_ENDPOINT = os.getenv('WEB3_ENDPOINT', 'http://127.0.0.1:8545')


def create_abi(contract_address: str):
    w3 = Web3(Web3.HTTPProvider(WEB3_ENDPOINT))
    path = pathlib.Path(__file__).parent.resolve()
    with open(path.as_posix() + '/erc20.json') as f:
        abi = json.load(f)
    contract = w3.eth.contract(
        address=Web3.toChecksumAddress(contract_address), abi=abi)
    return contract


def getERC20Balance(contract_address: str, address: str) -> str:
    contract = create_abi(contract_address)
    balance = contract.functions.balanceOf(
        Web3.toChecksumAddress(address)).call()
    return balance


def getERC20Data(contract_address: str):
    contract = create_abi(contract_address)
    name = contract.functions.name().call()
    symbol = contract.functions.symbol().call()
    decimals = contract.functions.decimals().call()
    return name, symbol, decimals
