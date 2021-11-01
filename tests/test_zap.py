import time

from brownie import *
import brownie

from rich.console import Console

console = Console()

from dotmap import DotMap
import pytest

# Test to add liquidity to metapool
def test_add_liquidity(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, wibBTC, lp_token):
    
    initialize(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC)
    
    # add ibbtc liquidity
    amounts = [ibbtc.balanceOf(deployer) // 10, 0, 0, 0]

    wibBTC_balance_before = wibBTC.sharesOf(metapool)
    ibbtc_zap.add_liquidity(metapool.address, amounts, 0, {"from": deployer})
    wibBTC_balance_after = wibBTC.sharesOf(metapool)

    # depositing ibbtc into curve pool, wibbtc balance of curve pool should increase propotionally to amount of ibbtc deposited
    assert wibBTC_balance_after - wibBTC_balance_before >= amounts[0] * 0.99 # multiplying by 0.99 for slippage considerations

    # add renbtc liquidity
    # when depositing renbtc/wBTC/sBTC the balance of lp token will increase

    amounts = [0, renbtc.balanceOf(deployer) // 10, 0, 0]

    lp_balance_before = lp_token.balanceOf(metapool)
    ibbtc_zap.add_liquidity(metapool.address, amounts, 0, {"from": deployer})
    lp_balance_after = lp_token.balanceOf(metapool)
    
    assert lp_balance_after > lp_balance_before


# Test to remove liquidity from metapool in equal proportions
def test_remove_liquidity(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, wibBTC, lp_token):

    initialize(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC)
    
    balance = metapool.balanceOf(deployer)
    min_amounts = [0] * 4
    
    balance_ibbtc_before = ibbtc.balanceOf(deployer)
    balance_renbtc_before = renbtc.balanceOf(deployer)
    balance_wBTC_before = wBTC.balanceOf(deployer)
    balance_sBTC_before = sBTC.balanceOf(deployer)
    balance_wibbtc_before_metapool = wibBTC.balanceOf(metapool)
    lp_balance_before = lp_token.balanceOf(metapool)

    ibbtc_zap.remove_liquidity(metapool.address, balance // 10, min_amounts, {"from": deployer})
    
    balance_ibbtc_after = ibbtc.balanceOf(deployer)
    balance_renbtc_after = renbtc.balanceOf(deployer)
    balance_wBTC_after = wBTC.balanceOf(deployer)
    balance_sBTC_after = sBTC.balanceOf(deployer)
    balance_wibbtc_after_metapool = wibBTC.balanceOf(metapool)
    lp_balance_after = lp_token.balanceOf(metapool)

    # deployer ibbtc, renbtc, wBTC, sBTC balance should increase
    assert balance_ibbtc_after > balance_ibbtc_before
    assert balance_renbtc_after > balance_renbtc_before
    assert balance_wBTC_after > balance_wBTC_before
    assert balance_sBTC_after > balance_sBTC_before

    # metapool wibbtc balance should decrease
    assert balance_wibbtc_before_metapool > balance_wibbtc_after_metapool

    # metapool lptoken balance should decrease
    assert lp_balance_after < lp_balance_before


# Test to remove liquidity from metapool by removing a single coin
def test_remove_one_coin(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, wibBTC, coins):

    initialize(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC)

    balance = metapool.balanceOf(deployer)
    
    amount = balance // 4
    before_ibbtc_balance = ibbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 0, 0, {"from": deployer})
    after_ibbtc_balance = ibbtc.balanceOf(deployer)
    assert after_ibbtc_balance > before_ibbtc_balance

    amount = balance // 4
    before_renbtc_balance = renbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 1, 0, {"from": deployer})
    after_renbtc_balance = renbtc.balanceOf(deployer)
    assert after_renbtc_balance > before_renbtc_balance

    amount = balance // 4
    before_wbtc_balance = wBTC.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(metapool, amount, 2, 0, {"from": deployer})
    after_wbtc_balance = wBTC.balanceOf(deployer)
    assert after_wbtc_balance > before_wbtc_balance


# Testing swap between different pairs
def test_swap(deployer, metapool, ibbtc_zap, ibbtc, renbtc, wBTC, sBTC, coins):
    
    initialize(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC)

    # swap ibbtc -> wbtc
    ibbtc_amount = ibbtc.balanceOf(deployer) // 10

    balance_wbtc_before_swap = wBTC.balanceOf(deployer)
    ibbtc_zap.swap(metapool, 0, 2, ibbtc_amount, 0)
    balance_wbtc_after_swap = wBTC.balanceOf(deployer)

    assert balance_wbtc_after_swap > balance_wbtc_before_swap

    # swap wbtc -> ibbtc
    wbtc_amount = wBTC.balanceOf(deployer) // 10

    balance_ibbtc_before_swap = ibbtc.balanceOf(deployer)
    ibbtc_zap.swap(metapool, 2, 0, wbtc_amount, 0)
    balance_ibbtc_after_swap = ibbtc.balanceOf(deployer)

    assert balance_ibbtc_after_swap > balance_ibbtc_before_swap

    # swap wbtc -> renbtc
    wbtc_amount = wBTC.balanceOf(deployer) // 10

    balance_renbtc_before_swap = renbtc.balanceOf(deployer)
    ibbtc_zap.swap(metapool, 2, 1, wbtc_amount, 0)
    balance_renbtc_after_swap = renbtc.balanceOf(deployer)

    assert balance_renbtc_after_swap > balance_renbtc_before_swap


#################### Setup ####################

@pytest.fixture
def setup(deployer, ibbtc, renbtc, wBTC):
    metapool = Contract("0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B")
    ibbtc_zap = DepositZapibBTC.deploy({"from": deployer})

    ## Uniswap some tokens here
    router = Contract("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")
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

    
    curve_sbtc_pool = Contract("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")

    balance_wbtc = wBTC.balanceOf(deployer)

    wBTC.approve(curve_sbtc_pool, 999999999999999999999999999999, {"from": deployer})
    curve_sbtc_pool.exchange(1, 2, balance_wbtc / 2, 0, {"from": deployer})

    # now the deployer has ibbtc, renbtc, wBTC
    return DotMap(
        ibbtc_zap=ibbtc_zap,
        metapool=metapool
    )

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
    return Contract("0x8751D4196027d4e6DA63716fA7786B5174F04C15")

@pytest.fixture
def sBTC():
    return Contract("0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6")

@pytest.fixture
def coins(ibbtc, renbtc, wBTC, sBTC):
    return [ibbtc, renbtc, wBTC, sBTC]

@pytest.fixture
def metapool(setup):
    return setup.metapool

# lp token part of the metapool crvRenWSBTC
@pytest.fixture
def lp_token(metapool):
    return Contract(metapool.coins(1))

@pytest.fixture
def deployer():
    yield accounts[0]

def approve(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC):
    
    ibbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    renbtc.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    wBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    sBTC.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})
    metapool.approve(ibbtc_zap, 999999999999999999999999999999, {"from": deployer})

def initialize(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC):
    approve(deployer, ibbtc_zap, metapool, ibbtc, renbtc, wBTC, sBTC)

    # initialize pool by depositing all coins in equal proportions
    amounts = [ibbtc.balanceOf(deployer) // 2, renbtc.balanceOf(deployer) // 2, renbtc.balanceOf(deployer) // 2, sBTC.balanceOf(deployer) // 2]
    ibbtc_zap.add_liquidity(metapool.address, amounts, 0, {"from": deployer})
