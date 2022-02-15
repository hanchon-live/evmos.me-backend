# import json
# a = '''{
# "types": {
#     "EIP712Domain":
#     [
#         {"name":"name","type":"string"},
#         {"name":"version","type":"string"},
#         {"name":"chainId","type":"uint256"},
#         {"name":"verifyingContract","type":"string"},
#         {"name":"salt","type":"string"}
#     ],
#     "Tx":[
#         {"name":"account_number","type":"string"},
#         {"name":"chain_id","type":"string"},
#         {"name":"fee","type":"Fee"},
#         {"name":"memo","type":"string"},
#         {"name":"msgs","type":"Msg[]"},
#         {"name":"sequence","type":"string"},
#         {"name":"timeout_height","type":"string"}
#     ],
#     "Fee":[
#         {"name":"amount","type":"Coin[]"},
#         {"name":"gas","type":"string"}
#     ],
#     "Coin":[
#         {"name":"denom","type":"string"},
#         {"name":"amount","type":"string"}
#     ],
#     "Msg":[
#         {"name":"type","type":"string"},
#         {"name":"value","type":"msgTypeName"}
#     ],
#     "msgTypeName":{}
# },
# "primaryType":"Tx",
# "domain":{
#     "name":"Cosmos Web3",
#     "version":"1.0.0",
#     "chainId":9000,
#     "verifyingContract":"cosmos",
#     "salt":"0"
# },
# "message":{
#     "account_number":"1",
#     "chain_id":"9000",
#     "fee":{
#         "amount":
#         [
#             {
#                 "denom":"aphoton",
#                 "amount":"20"
#             }
#         ],
#         "gas":"20aphoton"
#     },
#     "memo":"",
#     "msgs":[],
#     "sequence":"1",
#     "timeout_height":"1000000"
# }
# }'''
# eip_base = json.loads(a)
import json

a = '''{
"types": {
    "EIP712Domain":
    [
        {"name":"name","type":"string"},
        {"name":"version","type":"string"},
        {"name":"chainId","type":"uint256"},
        {"name":"verifyingContract","type":"string"},
        {"name":"salt","type":"string"}
    ],
    "Tx":[
        {"name":"account_number","type":"string"},
        {"name":"chain_id","type":"string"},
        {"name":"fee","type":"Fee"},
        {"name":"memo","type":"string"},
        {"name":"msgs","type":"Msg[]"},
        {"name":"sequence","type":"string"},
        {"name":"timeout_height","type":"string"}
    ],
    "Fee":[
        {"name":"amount","type":"Coin[]"},
        {"name":"gas","type":"string"}
    ],
    "Coin":[
        {"name":"denom","type":"string"},
        {"name":"amount","type":"string"}
    ],
    "Msg":[
        {"name":"type","type":"string"},
        {"name":"value","type":"string"}
    ]
},
"primaryType":"Tx",
"domain":{
    "name":"Cosmos Web3",
    "version":"1.0.0",
    "chainId":9000,
    "verifyingContract":"cosmos",
    "salt":"0"
},
"message":{
    "account_number":"1",
    "chain_id":"9000",
    "fee":{
        "amount":
        [
            {
                "denom":"aphoton",
                "amount":"20"
            }
        ],
        "gas":"20aphoton"
    },
    "memo":"",
    "msgs":[],
    "sequence":"1",
    "timeout_height":"1000000"
}
}'''

eip_base = json.loads(a)
