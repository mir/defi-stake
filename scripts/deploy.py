from brownie import (
    config,
    DappToken,
    TokenFarm
)
from scripts.utils import get_contract, get_account
from web3 import Web3

KEPT_DAPP_AMOUNT = Web3.toWei(100, "ether")
DAPP_TOTAL_SUPPLY = Web3.toWei(1e6, "ether")

def deploy():
    account = get_account()
    dapp_token = DappToken.deploy(DAPP_TOTAL_SUPPLY, {"from":account})
    token_farm = TokenFarm.deploy(dapp_token.address, {"from":account})    
    tx = dapp_token.transfer(
        token_farm.address,
        DAPP_TOTAL_SUPPLY - KEPT_DAPP_AMOUNT,
        {"from": account})
    tx.wait(1)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    allowed_tokens_dict = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed")
        }
    add_allowed_tokens(token_farm,allowed_tokens_dict,account)
    return token_farm, dapp_token

def add_allowed_tokens(token_farm, allowed_tokens_dict, account):
    for token in allowed_tokens_dict:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedAddress(
            token.address,
            allowed_tokens_dict[token],
             {"from": account}
             )
        set_tx.wait(1)
    return token_farm

def main():
    deploy()
