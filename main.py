import base64
import os
from typing import Any

import uvicorn
from evmosgrpc.accounts import get_account_all_balances
from evmosgrpc.accounts import get_account_grpc
from evmosgrpc.broadcaster import broadcast
from evmosgrpc.builder import ExternalWallet
from evmosgrpc.constants import CHAIN_ID
from evmosgrpc.constants import FEE
from evmosgrpc.constants import GAS_LIMIT
from evmosgrpc.messages.gov import register_coin_proposal_message
from evmosgrpc.messages.gov import register_erc20_proposal_message
from evmosgrpc.messages.gov import toggle_token_proposal_message
from evmosgrpc.messages.gov import update_token_pair_erc20_proposal_message
from evmosgrpc.messages.irm import create_convert_coin_message
from evmosgrpc.messages.irm import create_convert_erc20_message
from evmosgrpc.messages.irm import create_toggle_token_proposal
from evmosgrpc.messages.irm import create_update_token_pair_proposal
from evmosgrpc.messages.msgsend import create_msg_send
from evmosgrpc.messages.staking import create_msg_delegate
from evmosgrpc.messages.staking import create_msg_undelegate
from evmosgrpc.transaction import create_tx_raw
from evmosgrpc.transaction import Transaction
from evmoswallet.eth.ethereum import sha3_256
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.protobuf.json_format import MessageToDict
from web3 import Web3

from erc20 import create_abi
from erc20 import deploy_erc20_contract
from erc20 import getERC20Balance
from erc20 import getERC20Data
from erc20 import mint_ERC20
from schemas import AllBalances
from schemas import BroadcastData
from schemas import ConvertCoin
from schemas import ConvertErc20
from schemas import Delegate
from schemas import DeployERC20
from schemas import ERC20Balances
from schemas import ERC20SimpleBalance
from schemas import ERC20Transfer
from schemas import MessageData
from schemas import MintERC20
from schemas import MsgSend
from schemas import RegisterCoin
from schemas import RegisterErc20
from schemas import String
from schemas import ToggleToken
from schemas import UpdateTokenPair

origin = os.getenv('FRONTEND_WEBPAGE', '*')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def generate_message(tx: Transaction,
                     builder: ExternalWallet,
                     msg: Any,
                     memo: str = '',
                     fee: str = FEE,
                     gas_limit: str = GAS_LIMIT):
    tx.create_tx_template(builder,
                          msg,
                          memo=memo,
                          fee=fee,
                          gas_limit=gas_limit)
    to_sign = tx.create_sig_doc()
    bodyBytes = base64.b64encode(tx.body.SerializeToString())
    authInfoBytes = base64.b64encode(tx.info.SerializeToString())
    chainId = CHAIN_ID
    accountNumber = int(builder.account_number)
    return {
        'bodyBytes': bodyBytes,
        'authInfoBytes': authInfoBytes,
        'chainId': chainId,
        'accountNumber': accountNumber,
        'signBytes': base64.b64encode(sha3_256(to_sign).digest())
    }


@app.post('/msg_send', response_model=MessageData)
def create_msg(data: MsgSend):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    msg = create_msg_send(
        builder.address,
        data.destination,
        data.amount,
        denom=data.denom,
    )
    return generate_message(tx, builder, msg)


@app.post('/proposal_register_coin', response_model=MessageData)
def proposal_register_coin_endpoint(data: RegisterCoin):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()

    metadata = {
        'description':
        data.description,
        'denom_units': [{
            'denom': data.dnName,
            'exponent': data.dnExponent,
            'aliases': [data.dnAlias]
        }, {
            'denom': data.dn2Name,
            'exponent': data.dn2Exponent
        }],
        'base':
        data.base,
        'display':
        data.display,
        'name':
        data.name,
        'symbol':
        data.symbol,
    }

    msg = register_coin_proposal_message(data.wallet.address, metadata)
    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/proposal_register_erc20', response_model=MessageData)
def proposal_register_erc20_endpoint(data: RegisterErc20):
    print(data)
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    msg = register_erc20_proposal_message(data.wallet.address, data.contract)
    a = generate_message(tx,
                         builder,
                         msg,
                         fee=data.fee,
                         gas_limit=data.gasLimit)
    print(a)
    return a


@app.post('/convert_coin', response_model=MessageData)
def convert_coin_endpoint(data: ConvertCoin):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    msg = create_convert_coin_message(data.denom, data.amount, data.receiver,
                                      data.sender)
    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/toggle_token', response_model=MessageData)
def toggle_token_endpoint(data: ToggleToken):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    toggle_token = create_toggle_token_proposal('Enable',
                                                f'Token: {data.token}',
                                                data.token)
    msg = toggle_token_proposal_message(data.wallet.address, toggle_token)

    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/update_token_pair', response_model=MessageData)
def update_token_pair_endpoint(data: UpdateTokenPair):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    update = create_update_token_pair_proposal(
        'Update hanchon', f'Token: {data.token} - New: {data.newToken}',
        data.token, data.newToken)
    msg = update_token_pair_erc20_proposal_message(data.wallet.address, update)

    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/convert_erc20', response_model=MessageData)
def convert_erc20_endpoint(data: ConvertErc20):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    msg = create_convert_erc20_message(data.contract, data.amount,
                                       data.receiver, data.sender)
    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/undelegate')
def undelegate(data: Delegate):
    builder = ExternalWallet(data.wallet.address, data.wallet.algo,
                             base64.b64decode(data.wallet.pubkey))
    tx = Transaction()
    msg = create_msg_undelegate(builder.address, data.destination, data.amount)
    return generate_message(tx, builder, msg)


@app.post('/delegate')
def delegate(data: Delegate):
    builder = ExternalWallet(data.wallet.address, data.wallet.algo,
                             base64.b64decode(data.wallet.pubkey))
    tx = Transaction()
    msg = create_msg_delegate(builder.address, data.destination, data.amount)
    return generate_message(tx, builder, msg)


@app.post('/get_pubkey', response_model=String)
def get_pubkey(data: String):
    _, _, pubkey = get_account_grpc(data.value)
    if pubkey is None:
        pubkey = ''
    return {'value': pubkey}


@app.post('/get_all_balances', response_model=AllBalances)
def get_all_balances(data: String):
    try:
        res = get_account_all_balances(data.value)
        return res
    except Exception as e:
        print(e)
        return {'balances': [], 'pagination': {'total': 0, 'nextKey': 0}}


erc20Contracts = [
    '0x60861177776f63e9dd400e5644af7edf3810c7b7',
]


@app.post('/get_all_erc20_balances', response_model=ERC20Balances)
def get_all_erc20_balances(data: String):
    ret = []
    try:
        for c in erc20Contracts:
            balance = getERC20Balance(c, data.value)
            name, symbol, decimals = getERC20Data(c)
            ret.append({
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'balance': balance,
                'address': c
            })
    except Exception as e:
        print(e)
    return {'balances': ret}


@app.post('/get_erc20_balance', response_model=ERC20Balances)
def get_erc20_balance_endpoint(data: ERC20SimpleBalance):
    ret = []
    try:
        balance = getERC20Balance(data.contract, data.wallet)
        name, symbol, decimals = getERC20Data(data.contract)
        ret.append({
            'name': name,
            'symbol': symbol,
            'decimals': decimals,
            'balance': balance,
            'address': data.wallet
        })
    except Exception as e:
        print(e)
    return {'balances': ret}


@app.post('/deploy_erc_20_contract')
def deploy_erc20_contract_endpoint(data: DeployERC20):
    print(data)
    tx = deploy_erc20_contract(data.walletEth, data.name, data.symbol,
                               data.gas, data.gasPrice)
    return {'tx': tx}


@app.post('/mint_erc20_coins')
def mint_erc20_coins_endpoint(data: MintERC20):
    tx = mint_ERC20(data.contract, data.walletEth, data.destination,
                    data.amount, data.gas, data.gasPrice)
    return {'tx': tx}


@app.post('/create_erc20_transfer')
def create_erc20_transfer(data: ERC20Transfer):
    try:
        abi = create_abi(data.token)
        tx = abi.functions.transfer(Web3.toChecksumAddress(
            data.destination), int(data.amount)).buildTransaction({
                'from':
                data.sender,
                'gas':
                Web3.toHex(int(data.gas)).encode('utf-8'),
                'gasPrice':
                Web3.toHex(int(data.gasPrice)).encode('utf-8'),
            })
        return {'tx': tx}
    except Exception as e:
        print(e)
        return


@app.post('/broadcast')
def signed_msg(data: BroadcastData):
    raw = create_tx_raw(
        body_bytes=base64.b64decode(data.bodyBytes),
        auth_info=base64.b64decode(data.authBytes),
        signature=base64.b64decode(data.signature),
    )
    result = broadcast(raw)
    dictResponse = MessageToDict(result)
    print(dictResponse)
    if 'code' in dictResponse['txResponse'].keys():
        return {'res': False, 'msg': dictResponse['txResponse']['rawLog']}
    return {'res': True, 'msg': dictResponse['txResponse']['txhash']}


if __name__ == '__main__':
    uvicorn.run(app)
