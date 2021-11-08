import pytest

from brownie import MetaBTC, MetaBTCBalances
from conftest import MAX_UINT256, weth


@pytest.fixture(autouse=True, params=[MetaBTC, MetaBTCBalances])
def ibbtc_pool(request, wibbtc, deployer):
    pool = request.param.deploy({"from": deployer})
    pool.initialize("wibBTC", "wibBTC", wibbtc, 1e18, 100, 4_000_000, {"from": deployer})
    yield pool


@pytest.fixture(autouse=True)
def ibbtc_zap(DepositZapibBTC, deployer):
    yield DepositZapibBTC.deploy({"from": deployer})


@pytest.fixture(autouse=True)
def core(Core, deployer):
    yield Core.deploy(1e18, {"from": deployer})


@pytest.fixture(autouse=True)
def set_core(wibbtc, deployer, core):
    # Reset wibBTC core
    wibbtc.setCore(core, {"from": wibbtc.governance()})
    wibbtc.updatePricePerShare({"from": deployer})


@pytest.fixture(autouse=True)
def seed_pool(ibbtc_zap, ibbtc_pool, deployer, wibbtc, renbtc, wbtc, sbtc):
    ibbtc_pool.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})

    # Initialize pool to 1: 1 wibbtc/sbtcCrv peg
    amounts = [
        wibbtc.balanceToShares(10 ** wibbtc.decimals()),  # ibbtc
        10 ** renbtc.decimals() // 3,  # renbtc
        10 ** wbtc.decimals() // 3,  # wbtc
        10 ** sbtc.decimals() // 3,  # sbtc
    ]
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})


def test_pool_rebalance(wibbtc, ibbtc_pool, sbtc_pool, core, deployer, ibbtc_zap):
    print("-" * 80)
    print(f"PPS: {wibbtc.pricePerShare()}")
    print(f"ibBTC balance: {wibbtc.balanceToShares(wibbtc.balanceOf(ibbtc_pool))}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"wibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    # Update pps
    core.setPricePerShare(1.2e18)
    wibbtc.updatePricePerShare({"from": deployer})

    print("-" * 80)
    print(f"PPS: {wibbtc.pricePerShare()}")
    print(f"ibBTC balance: {wibbtc.balanceToShares(ibbtc_pool.balances(0))}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"wibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    # Add some renbtc
    ibbtc_zap.add_liquidity(ibbtc_pool, [0, 0.4e8, 0, 0], 0, {"from": deployer})
    print("-" * 80)
    print(f"PPS: {wibbtc.pricePerShare()}")

    print(f"ibBTC balance: {wibbtc.balanceToShares(ibbtc_pool.balances(0))}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"wibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)
