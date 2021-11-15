import base64
import os
from typing import Any

import uvicorn
from evmosgrpc.accounts import get_account_all_balances
from evmosgrpc.accounts import get_account_grpc
from evmosgrpc.broadcaster import broadcast
from evmosgrpc.builder import ExternalWallet
from evmosgrpc.constants import CHAIN_ID
from evmosgrpc.messages.msgsend import create_msg_send
from evmosgrpc.messages.staking import create_msg_delegate
from evmosgrpc.transaction import create_tx_raw
from evmosgrpc.transaction import Transaction
from evmoswallet.eth.ethereum import sha3_256
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.protobuf.json_format import MessageToDict
from web3 import Web3

from erc20 import create_abi
from erc20 import getERC20Balance
from erc20 import getERC20Data
from schemas import AllBalances
from schemas import BroadcastData
from schemas import ERC20Balances
from schemas import ERC20Transfer
from schemas import MessageData
from schemas import SendAphotons
from schemas import String

origin = os.getenv('FRONTEND_WEBPAGE', '*')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def generate_message(tx: Transaction, builder: ExternalWallet, msg: Any):
    tx.create_tx_template(builder, msg)
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


@app.post('/send_aphotons', response_model=MessageData)
def create_msg(data: SendAphotons):
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
    )
    return generate_message(tx, builder, msg)


@app.post('/delegate')
def delegate(data: SendAphotons):
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


erc20Contracts = ['0x283DA9217d4aEBeeddABf4C8F9d4bd3d21d260c2']


@app.post('/get_all_erc20_balances', response_model=ERC20Balances)
def get_all_erc20_balances(data: String):
    try:
        balance = getERC20Balance(erc20Contracts[0], data.value)
        name, symbol, decimals = getERC20Data(erc20Contracts[0])
        return {
            'balances': [{
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'balance': balance,
                'address': erc20Contracts[0]
            }]
        }
    except Exception as e:
        print(e)
        return


@app.post('/create_erc20_transfer')
def create_erc20_transfer(data: ERC20Transfer):
    try:
        abi = create_abi(data.token)
        tx = abi.functions.transfer(Web3.toChecksumAddress(data.destination),
                                    int(data.amount)).buildTransaction({
                                        'from':
                                        data.sender,
                                        'gas':
                                        '210000',
                                        'gasPrice':
                                        '1',
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
    if 'code' in dictResponse['txResponse'].keys():
        return {'res': False, 'msg': dictResponse['txResponse']['rawLog']}
    return {'res': True, 'msg': dictResponse['txResponse']['txhash']}


if __name__ == '__main__':
    uvicorn.run(app)
