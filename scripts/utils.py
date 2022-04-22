from brownie import (
    accounts, config, network, Contract,
    DappToken,
    TokenFarm,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    MockDAI,
    MockWETH
    )
from web3 import Web3
from scripts import (
    NoContract
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-forked", "mainnet-fork-dev"]
LOCAL_BLOCKHAIN_ENVIRONMENTS = ["development", "ganache-local"]

CONTRACT_NAMES = {
    "DappToken": DappToken,
    "TokenFarm":TokenFarm,
    "eth_usd_price_feed": MockV3Aggregator,
    "weth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "VRFCoordinatorV2Mock": VRFCoordinatorV2Mock,
    "fau_token": MockDAI,
    "weth_token": MockWETH
    }

DECIMALS = 18
INITIAL_VALUE = Web3.toWei(2000, "ether")
BASE_FEE = 100000000000000000  # The premium
GAS_PRICE_LINK = 1e9  # Some value calculated depending on the Layer 1 cost and Link

def get_contract(name, *args):
    print(f"Get contract {name}")
    if name not in CONTRACT_NAMES:
        raise NoContract(f"Contract {name} is not known")    
    contract_type = CONTRACT_NAMES[name]
    
    if network.show_active() in LOCAL_BLOCKHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
            print(f'  {network.show_active()} address: {contract_address}')
        except KeyError:
            print(
                f"{network.show_active()} address of {name} not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
            )
    return contract

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

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print("Deploying mock DAI")
    mock_dai = MockDAI.deploy(initial_value, {"from": account})
    print(f"Deployed to {mock_dai.address}")
    print("Deploying mock WETH")
    mock_weth = MockWETH.deploy(initial_value, {"from": account})
    print(f"Deployed to {mock_weth.address}")

def listen_for_event(brownie_contract, event, timeout=200, poll_interval=2):
    """Listen for an event to be fired from a contract.
    We are waiting for the event to return, so this function is blocking.

    Args:
        brownie_contract ([brownie.network.contract.ProjectContract]):
        A brownie contract of some kind.

        event ([string]): The event you'd like to listen for.

        timeout (int, optional): The max amount in seconds you'd like to
        wait for that event to fire. Defaults to 200 seconds.

        poll_interval ([int]): How often to call your node to check for events.
        Defaults to 2 seconds.
    """
    web3_contract = web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    while current_time - start_time < timeout:
        for event_response in event_filter.get_new_entries():
            if event in event_response.event:
                print("Found event!")
                return event_response
        time.sleep(poll_interval)
        current_time = time.time()
    print("Timeout reached, no event found.")
    return {"event": None}

