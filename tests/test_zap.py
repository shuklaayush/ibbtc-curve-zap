import time

from brownie import *
import brownie

from rich.console import Console

console = Console()

from dotmap import DotMap
import pytest

@pytest.fixture
def setup(deployer, ibbtc, renbtc, wBTC):
    metapool = Contract.from_explorer("0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B")
    ibbtc_zap = DepositZapibBTC.deploy({"from": deployer})

    ## Uniswap some tokens here
    router = Contract.from_explorer("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")
    router.swapExactETHForTokens(
        0,  ## Mint out
        ["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", wBTC.address, ibbtc.address],
        deployer,
        9999999999999999,
        {"from": deployer, "value": 100e18},
    )

    router.swapExactETHForTokens(
        0,  ## Mint out
        ["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", renbtc.address],
        deployer,
        9999999999999999,
        {"from": deployer, "value": 100e18},
    )

    router.swapExactETHForTokens(
        0,  ## Mint out
        ["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", wBTC.address],
        deployer,
        9999999999999999,
        {"from": deployer, "value": 200e18},
    )

    
    curve_sbtc_pool = Contract.from_explorer("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")

    balance_wbtc = wBTC.balanceOf(deployer)

    wBTC.approve(curve_sbtc_pool, 999999999999999999999999999999, {"from": deployer})
    curve_sbtc_pool.exchange(1, 2, balance_wbtc / 2, 0, {"from": deployer})

    # now the deployer has ibbtc, renbtc, wBTC
    return DotMap(
        ibbtc_zap=ibbtc_zap,
        metapool=metapool
    )

def test_add_liquidity(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, coins):
    
    ibbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    renbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    wBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    sBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})

    # initialize pool by depositing all coins
    amounts = [ibbtc.balanceOf(deployer) / 2, renbtc.balanceOf(deployer) / 2, renbtc.balanceOf(deployer) / 2, sBTC.balanceOf(deployer) / 2]
    ibbtc_zap.add_liquidity(metapool.address, amounts, 0, {"from": deployer})

    # add only ibbtc liquidity
    amounts = [ibbtc.balanceOf(deployer) / 10, 0, 0, 0]
    ibbtc_zap.add_liquidity(metapool.address, amounts, 0, {"from": deployer})

    for coin, amount in zip(coins, amounts):
        assert coin.balanceOf(ibbtc_zap) == 0

    # check lp token balance
    assert metapool.balanceOf(deployer) > 0

def test_remove_liquidity(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, coins):

    ibbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    renbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    wBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    sBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})

    # initialize pool by depositing all coins
    amounts = [ibbtc.balanceOf(deployer) // 2, renbtc.balanceOf(deployer) // 2, renbtc.balanceOf(deployer) // 2, sBTC.balanceOf(deployer) // 2]
    ibbtc_zap.add_liquidity(metapool, amounts, 0, {"from": deployer})

    balance = metapool.balanceOf(deployer)
    min_amounts = [0] * 4
    ibbtc_zap.remove_liquidity(metapool.address, balance // 10, min_amounts, {"from": deployer})

def test_remove_one_coin(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, coins):

    ibbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    renbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    wBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})

    # add multiple coins
    amounts = [ibbtc.balanceOf(deployer) / 10, renbtc.balanceOf(deployer) / 10, renbtc.balanceOf(deployer) / 10, 0]
    ibbtc_zap.add_liquidity(metapool, amounts, 0, {"from": deployer})

    balance = metapool.balanceOf(deployer)
    
    amount = balance // 10
    before_ibbtc_balance = ibbtc.balanceOf(deployer)
    with brownie.reverts("Integer underflow"): # As we deposit initially there is high slippage
        ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 0, 0, {"from": deployer})
    after_ibbtc_balance = ibbtc.balanceOf(deployer)
    assert after_ibbtc_balance >= before_ibbtc_balance

    amount = balance // 10
    before_renbtc_balance = renbtc.balanceOf(deployer)
    with brownie.reverts("Integer underflow"): # As we deposit initially there is high slippage
        ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 1, 0, {"from": deployer})
    after_renbtc_balance = renbtc.balanceOf(deployer)
    assert after_renbtc_balance >= before_renbtc_balances

    amount = balance // 10
    before_wbtc_balance = wBTC.balanceOf(deployer)
    with brownie.reverts("Integer underflow"): # As we deposit initially there is high slippage
        ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 2, 0, {"from": deployer})
    after_wbtc_balance = wBTC.balanceOf(deployer)
    assert after_wbtc_balance >= before_wbtc_balance

def test_swap(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, coins):
    
    ibbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    renbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    wBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})



@pytest.fixture
def ibbtc_zap(setup):
    return setup.ibbtc_zap

@pytest.fixture
def ibbtc():
    return interface.ERC20("0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F")

@pytest.fixture
def renbtc():
    return interface.ERC20("0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D")

@pytest.fixture
def wBTC():
    return interface.ERC20("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

@pytest.fixture
def wibBTC():
    return Contract.from_explorer("0x8751D4196027d4e6DA63716fA7786B5174F04C15")

@pytest.fixture
def sBTC():
    return Contract.from_explorer("0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6")

@pytest.fixture
def coins(ibbtc, renbtc, wBTC, sBTC):
    return [ibbtc, renbtc, wBTC, sBTC]


@pytest.fixture
def metapool(setup):
    return setup.metapool

@pytest.fixture
def deployer():
    yield accounts[0]

