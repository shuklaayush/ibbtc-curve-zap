import pytest

from conftest import MAX_UINT256


@pytest.fixture(autouse=True)
def ibbtc_pool(MetaIbBTC, ibbtc, deployer):
    pool = MetaIbBTC.deploy({"from": deployer})
    pool.initialize("ibBTC", "ibBTC", ibbtc, 100, 4_000_000, {"from": deployer})
    yield pool


@pytest.fixture(autouse=True)
def ibbtc_zap(DepositZapBTC, deployer):
    yield DepositZapBTC.deploy({"from": deployer})


@pytest.fixture(autouse=True)
def core(Core, deployer):
    yield Core.deploy(1e18, {"from": deployer})


@pytest.fixture(autouse=True)
def set_core(ibbtc, core):
    # Reset ibBTC core
    ibbtc.switchCore(core, {"from": ibbtc.core()})


@pytest.fixture(autouse=True)
def seed_pool(ibbtc_zap, ibbtc_pool, deployer, ibbtc, renbtc, wbtc, sbtc):
    ibbtc_pool.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})

    # Initialize pool to 1: 1 wibbtc/sbtcCrv peg
    amounts = [
        10 ** ibbtc.decimals(),  # ibbtc
        10 ** renbtc.decimals() // 3,  # renbtc
        10 ** wbtc.decimals() // 3,  # wbtc
        10 ** sbtc.decimals() // 3,  # sbtc
    ]
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})


def test_pool_rebalance(ibbtc, ibbtc_pool, sbtc_pool, core, deployer, ibbtc_zap):
    print("-" * 80)
    print(f"PPS: {ibbtc.pricePerShare()}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"ibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    # Update pps
    core.setPricePerShare(1.2e18)
    ibbtc_pool.update_rate_multiplier({'from': deployer})

    print("-" * 80)
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"PPS: {ibbtc.pricePerShare()}")
    print(f"ibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    ibbtc_zap.add_liquidity(ibbtc_pool, [0, 0.4e8, 0, 0], 0, {"from": deployer})
    print("-" * 80)
    print(f"PPS: {ibbtc.pricePerShare()}")

    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print(f"ibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)
