from brownie import (
    accounts, config, network, Contract,
    DappToken,
    TokenFarm    
    )
from web3 import Web3
from scripts import (
    NoContract
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-forked", "mainnet-fork-dev"]
LOCAL_BLOCKHAIN_ENVIRONMENTS = ["development", "ganache-local"]
CONTRACT_NAMES = {"DappToken": DappToken, "TokenFarm":TokenFarm}

def get_contract(name, *args):
    if name not in CONTRACT_NAMES:
        raise NoContract(f"Contract {name} is not known")    
    contract_type = CONTRACT_NAMES[name]
    if not contract_type:
        deploy_contract(contract_type, *args)
    return contract_type[-1]

def deploy_contract(contract, *args):
    contract.deploy(
        *args,
        {"from": get_account()},
        publish_source=config["networks"][network.show_active()].get("verify", False))

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS
            or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

