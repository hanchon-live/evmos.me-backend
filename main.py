import base64
import json
import os
from typing import Any

import uvicorn
from evmosgrpc.accounts import get_account_all_balances
from evmosgrpc.accounts import get_account_grpc
from evmosgrpc.broadcaster import broadcast
from evmosgrpc.builder import ExternalWallet
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
from evmosgrpc.transaction import Transaction
from evmoswallet.eth.ethereum import sha3_256
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.protobuf.json_format import MessageToDict
from web3 import Web3

from eip712 import eip_base
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
# from evmosgrpc.constants import CHAIN_ID
# from evmosgrpc.transaction import create_tx_raw

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
    chainId = '9000'
    accountNumber = int(builder.account_number)

    eip_base['message']['account_number'] = str(builder.account_number)
    eip_base['message']['sequence'] = str(builder.sequence)

    eip_base['message']['msgs'] = [[
        123, 34, 116, 121, 112, 101, 34, 58, 34, 99, 111, 115, 109, 111, 115,
        45, 115, 100, 107, 47, 77, 115, 103, 83, 101, 110, 100, 34, 44, 34,
        118, 97, 108, 117, 101, 34, 58, 123, 34, 97, 109, 111, 117, 110, 116,
        34, 58, 91, 123, 34, 97, 109, 111, 117, 110, 116, 34, 58, 34, 49, 34,
        44, 34, 100, 101, 110, 111, 109, 34, 58, 34, 97, 112, 104, 111, 116,
        111, 110, 34, 125, 93, 44, 34, 102, 114, 111, 109, 95, 97, 100, 100,
        114, 101, 115, 115, 34, 58, 34, 101, 116, 104, 109, 49, 116, 102, 101,
        103, 102, 53, 48, 110, 53, 120, 108, 48, 104, 100, 53, 99, 120, 102,
        122, 106, 99, 97, 51, 121, 108, 115, 102, 112, 103, 48, 102, 110, 101,
        100, 53, 103, 113, 109, 34, 44, 34, 116, 111, 95, 97, 100, 100, 114,
        101, 115, 115, 34, 58, 34, 101, 116, 104, 109, 49, 116, 102, 101, 103,
        102, 53, 48, 110, 53, 120, 108, 48, 104, 100, 53, 99, 120, 102, 122,
        106, 99, 97, 51, 121, 108, 115, 102, 112, 103, 48, 102, 110, 101, 100,
        53, 103, 113, 109, 34, 125, 125
    ]]

    print(eip_base)
    # print(json.dumps(eip_base))

    res = {
        'bodyBytes': bodyBytes,
        'authInfoBytes': authInfoBytes,
        'chainId': chainId,
        'accountNumber': accountNumber,
        'signBytes': base64.b64encode(sha3_256(to_sign).digest()),
        'eip': json.dumps(eip_base)
    }
    print(f'{res=}')
    return res


@app.post('/msg_send', response_model=MessageData)
def create_msg(data: MsgSend):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    # print(data.wallet.address)
    # print(data.wallet.algo)
    # print(base64.b64decode(data.wallet.pubkey))
    # print(data.wallet.pubkey)
    tx = Transaction()
    msg = create_msg_send(
        builder.address,
        data.destination,
        data.amount,
        denom=data.denom,
    )
    print('--------- TESTING MSG ---------')
    print(msg)
    print(msg.SerializeToString())
    print(list(msg.SerializeToString()))
    print('--------- END MSG ---------')

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
    msg = register_coin_proposal_message(data.wallet.address, metadata,
                                         data.proposalTitle,
                                         data.proposalDescription)
    return generate_message(tx,
                            builder,
                            msg,
                            fee=data.fee,
                            gas_limit=data.gasLimit)


@app.post('/proposal_register_erc20', response_model=MessageData)
def proposal_register_erc20_endpoint(data: RegisterErc20):
    builder = ExternalWallet(
        data.wallet.address,
        data.wallet.algo,
        base64.b64decode(data.wallet.pubkey),
    )
    tx = Transaction()
    msg = register_erc20_proposal_message(data.wallet.address, data.contract,
                                          data.proposalTitle,
                                          data.proposalDescription)
    a = generate_message(tx,
                         builder,
                         msg,
                         fee=data.fee,
                         gas_limit=data.gasLimit)
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
    toggle_token = create_toggle_token_proposal(data.proposalTitle,
                                                data.proposalDescription,
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
    update = create_update_token_pair_proposal(data.proposalTitle,
                                               data.proposalDescription,
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
    '0x60861177776f63e9dd400e5644af7edf3810c7b7',  # Hanchon
    '0x00819E780C6e96c50Ed70eFFf5B73569c15d0bd7',  # Aphoton
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
    print(data)
    # raw = create_tx_raw(
    #     body_bytes=base64.b64decode(data.bodyBytes),
    #     auth_info=base64.b64decode(data.authBytes),
    #     signature=base64.b64decode(data.signature),
    # )
    from evmosproto.cosmos.tx.v1beta1.tx_pb2 import TxBody
    from evmosproto.ethermint.types.v1.web3_pb2 import ExtensionOptionsWeb3Tx
    from evmosproto.google.protobuf.any_pb2 import Any

    a = base64.b64decode(data.bodyBytes)
    print(a)
    m = TxBody()
    m.ParseFromString(a)

    ext = ExtensionOptionsWeb3Tx()
    ext.typed_data_chain_id = 9000
    ext.fee_payer = 'ethm1tfegf50n5xl0hd5cxfzjca3ylsfpg0fned5gqm'
    ext.fee_payer_sig = bytes(bytearray.fromhex(data.signature.split('0x')[1]))
    any = Any()
    any.Pack(ext, type_url_prefix='/')
    print(any)
    m.extension_options.append(any)

    # print(m)
    # # tx.
    # extension_options
    # # return tx

    from evmosproto.cosmos.tx.v1beta1.tx_pb2 import TxRaw
    tx = TxRaw()
    tx.body_bytes = m.SerializeToString()
    # tx.extension_options = ext
    tx.auth_info_bytes = base64.b64decode(data.authBytes)
    tx.signatures.append(b'')

    result = broadcast(tx)
    dictResponse = MessageToDict(result)
    print(dictResponse)
    if 'code' in dictResponse['txResponse'].keys():
        return {'res': False, 'msg': dictResponse['txResponse']['rawLog']}
    return {'res': True, 'msg': dictResponse['txResponse']['txhash']}


# @app.get('get_proposals')
# def get_proposals():
#     return get_IRM_proposals(get_proposals_grpc())

if __name__ == '__main__':
    uvicorn.run(app)
