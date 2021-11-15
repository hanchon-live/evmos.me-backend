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
class SendAphotons(BaseModel):
    wallet: Wallet
    amount: int
    destination: str


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
