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


# ERC20 Balance request
class ERC20SimpleBalance(BaseModel):
    contract: str
    wallet: str


# Message data
class MessageData(BaseModel):
    bodyBytes: str
    authInfoBytes: str
    chainId: str
    accountNumber: int
    signBytes: str
    eip: str


# Broadcasting
class BroadcastData(BaseModel):
    bodyBytes: str
    authBytes: str
    signature: str
    eip: str


# Grpc Messages
class MsgSend(BaseModel):
    wallet: Wallet
    amount: int
    destination: str
    denom: str
    memo: str


# Grpc Messages
class Delegate(BaseModel):
    wallet: Wallet
    amount: int
    destination: str


# Test
class RegisterErc20(BaseModel):
    wallet: Wallet
    contract: str
    fee: str
    gasLimit: str
    proposalTitle: str
    proposalDescription: str


class RegisterCoin(BaseModel):
    wallet: Wallet
    description: str
    base: str
    display: str
    name: str
    symbol: str
    dnName: str
    dnExponent: str
    dnAlias: str
    dn2Name: str
    dn2Exponent: str
    fee: str
    gasLimit: str
    proposalTitle: str
    proposalDescription: str


class ConvertErc20(BaseModel):
    wallet: Wallet
    contract: str
    amount: str
    receiver: str
    sender: str
    fee: str
    gasLimit: str


class ConvertCoin(BaseModel):
    wallet: Wallet
    denom: str
    amount: str
    receiver: str
    sender: str
    fee: str
    gasLimit: str


class ToggleToken(BaseModel):
    wallet: Wallet
    token: str
    fee: str
    gasLimit: str
    proposalTitle: str
    proposalDescription: str


class UpdateTokenPair(BaseModel):
    wallet: Wallet
    token: str
    newToken: str
    fee: str
    gasLimit: str
    proposalTitle: str
    proposalDescription: str


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
    gas: str
    gasPrice: str


class DeployERC20(BaseModel):
    wallet: Wallet
    name: str
    symbol: str
    walletEth: str
    gas: str
    gasPrice: str


class MintERC20(BaseModel):
    wallet: Wallet
    contract: str
    destination: str
    amount: str
    walletEth: str
    gas: str
    gasPrice: str
