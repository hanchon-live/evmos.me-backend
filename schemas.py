from typing import List

from pydantic import BaseModel


# Wallet info
class Wallet(BaseModel):
    address: str
    algo: str
    pubkey: str


# Generic
class String(BaseModel):
    value: str


# Message data
class MessageData(BaseModel):
    bodyBytes: str
    authInfoBytes: str
    chainId: str
    accountNumber: int
    signBytes: str


# Broadcasting
class BroadcastData(BaseModel):
    bodyBytes: str
    authBytes: str
    signature: str


# Grpc Messages
class MsgSend(BaseModel):
    wallet: Wallet
    amount: int
    destination: str
    denom: str
    memo: str


# All Balances
class Coin(BaseModel):
    denom: str
    amount: str


class Pagination(BaseModel):
    total: str
    nextKey: str


class AllBalances(BaseModel):
    balances: List[Coin]
    pagination: Pagination


class ERC20(BaseModel):
    name: str
    symbol: str
    decimals: str
    balance: str
    address: str


class ERC20Balances(BaseModel):
    balances: List[ERC20]


class ERC20Transfer(BaseModel):
    sender: str
    destination: str
    token: str
    amount: str


class DeployERC20(BaseModel):
    wallet: Wallet
    name: str
    symbol: str
    walletEth: str
