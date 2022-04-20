from brownie import (
    config,
    DappToken,
    TokenFarm
)
from scripts.utils import get_contract, get_account
from web3 import Web3

KEPT_DAPP_AMOUNT = Web3.toWei(100, "ether")
DAPP_TOTAL_SUPPLY = Web3.toWei(1000, "ether")

def deploy():
    account = get_account()
    dappToken = get_contract("DappToken", DAPP_TOTAL_SUPPLY)
    tokenFarm = get_contract("TokenFarm", dappToken.address)
    tx = dappToken.transfer(
        tokenFarm.address,
        DAPP_TOTAL_SUPPLY - KEPT_DAPP_AMOUNT,
        {"from": account})
    tx.wait(1)
    add_allowed_tokens(tokenFarm,ALLOWED_TOKENS_DICT,account)

ALLOWED_TOKENS_DICT = {}

def add_allowed_tokens(tokenFarm, allowed_tokens_dict, account):
    pass

def main():
    deploy()
