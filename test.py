# from evmosgrpc.messages.irm import create_register_erc20_proposal
# from google.protobuf.json_format import MessageToDict
# proposal = create_register_erc20_proposal('title', 'description',
#                                           '0x00000000000000000000')
# from evmosgrpc.messages.gov import create_submit_proposal
# print(MessageToDict(proposal))
# from evmosproto.google.protobuf.any_pb2 import Any
# from evmosgrpc.constants import DENOM
# from evmosproto.cosmos.base.v1beta1.coin_pb2 import Coin
# any = Any()
# any.Pack(proposal, type_url_prefix='/')
# coin = Coin()
# coin.denom = DENOM
# coin.amount = '20'
# p = create_submit_proposal(any, coin,
#                            'evmos1w3ygakvq5snf30pca5g8pnyvvfr7x28djnj34m')
# print(p)
