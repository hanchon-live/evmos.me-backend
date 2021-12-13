import json
import os
import pathlib

from web3 import Web3

WEB3_ENDPOINT = os.getenv('WEB3_ENDPOINT', 'http://127.0.0.1:8545')


def create_abi(contract_address: str, contract='/erc20.json'):
    w3 = Web3(Web3.HTTPProvider(WEB3_ENDPOINT))
    path = pathlib.Path(__file__).parent.resolve()
    with open(path.as_posix() + contract) as f:
        abi = json.load(f)
    contract = w3.eth.contract(
        address=Web3.toChecksumAddress(contract_address), abi=abi)
    return contract


def getERC20Balance(contract_address: str, address: str) -> str:
    contract = create_abi(contract_address)
    try:
        balance = contract.functions.balanceOf(
            Web3.toChecksumAddress(address)).call()
    except Exception:
        return 0
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
    gas: str = '2100000000000',
    gasPrice: str = '2',
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
            Web3.toHex(int(gas)).encode('utf-8'),
            'gasPrice':
            Web3.toHex(int(gasPrice)).encode('utf-8'),
        })


def mint_ERC20(
    contract_address: str,
    owner: str,
    dest: str,
    amount: str,
    gas: str = '2100000000000',
    gasPrice: str = '2',
) -> str:
    contract = create_abi(contract_address)
    mint = contract.functions.mint(
        Web3.toChecksumAddress(dest), int(amount)).buildTransaction({
            'from':
            Web3.toChecksumAddress(owner),
            'gas':
            Web3.toHex(int(gas)).encode('utf-8'),
            'gasPrice':
            Web3.toHex(int(gasPrice)).encode('utf-8'),
        })
    return mint
