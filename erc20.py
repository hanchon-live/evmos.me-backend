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


def deploy_erc20_contract(
    address: str,
    name: str,
    symbol: str,
    gas: str = '2100000000000000',
    gasPrice: str = '1',
):
    w3 = Web3(Web3.HTTPProvider(WEB3_ENDPOINT))
    path = pathlib.Path(__file__).parent.resolve()
    with open(path.as_posix() + '/erc20OpenZeppelin.json') as f:
        raw_data = json.load(f)
        print(raw_data)
        contract = w3.eth.contract(abi=raw_data['abi'],
                                   bytecode=raw_data['bin'])
        return contract.constructor(name, symbol).buildTransaction({
            'from':
            address,
            'gas':
            gas,
            'gasPrice':
            gasPrice,
            'nonce':
            str(w3.eth.getTransactionCount(Web3.toChecksumAddress(address)))
        })


# 0xb147e6e7360d4fdaba236c4858fec3a8cb7864ceaba8e8f4b5b4f5f1d12b7f99
# 0x4b4bf2cd23feb5e7e1a3d8f25e3cf0e9c9cb682bc5b7507358e02433072fbf7f
