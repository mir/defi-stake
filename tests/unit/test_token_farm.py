from unittest import skip
from brownie import (
    accounts,
    network,
    config,
    TokenFarm,
    exceptions
)
import pytest
from scripts.utils import (
    get_account,
    get_contract,
    LOCAL_BLOCKHAIN_ENVIRONMENTS
)
import pytest
from scripts.deploy import (
    deploy
)
from web3 import Web3


@pytest.fixture
def amount_staked():
    return Web3.toWei(1, "ether")

def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip("Only for local blockchains")
    
    account = get_account()
    account_non_owner = get_account(index=1)
    token_farm, dapp_token = deploy()

    price_feed = get_contract("eth_usd_price_feed")

    token_farm.setPriceFeedAddress(
        dapp_token.address, 
        price_feed,
        {"from": account}
        )
    assert token_farm.tokenPriceFeedMap(dapp_token.address) == price_feed
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedAddress(
        dapp_token.address, 
        price_feed,
        {"from": account_non_owner}
        )

def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        pytest.skip("Only for local blockchains")
    
    account = get_account()    
    token_farm, dapp_token = deploy()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeToken(amount_staked, dapp_token.address, {"from": account})

    assert (
        token_farm.tokenStakerBalance(dapp_token.address, account.address) == amount_staked
    ) 

def test_issue_tokens_():
    pass