import pytest

from conftest import MAX_UINT256, deployer


@pytest.fixture(autouse=True)
def ibbtc_pool(MetaBTC, wibbtc, deployer):
    yield MetaBTC.deploy(
        "ibBTC", "ibbtc", wibbtc, 1e18, 100, 4_000_000, {"from": deployer}
    )


@pytest.fixture(autouse=True)
def core(Core, deployer):
    yield Core.deploy(1.2e18, {"from": deployer})


@pytest.fixture(autouse=True)
def set_core(wibbtc, deployer, core):
    # Reset wibBTC core
    wibbtc.setCore(core, {"from": wibbtc.governance()})
    wibbtc.updatePricePerShare({"from": deployer})


@pytest.fixture(autouse=True)
def seed_pool(wibbtc, ibbtc_zap, ibbtc_pool, deployer, renbtc, wbtc, sbtc):
    ibbtc_pool.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})

    # Initialize pool to 1: 1 wibbtc/sbtcCrv peg
    amounts = [
        wibbtc.balanceToShares(10 ** wibbtc.decimals()),  # ibbtc
        10 ** renbtc.decimals() // 3,  # renbtc
        10 ** wbtc.decimals() // 3,  # wbtc
        10 ** sbtc.decimals() // 3,  # sbtc
    ]
    print(amounts)
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})


def test_pool_rebalance(ibbtc_pool, wibbtc, sbtc_pool, core, deployer, ibbtc_zap):
    print("-" * 80)
    print(f"ibBTC balance: {wibbtc.balanceToShares(wibbtc.balanceOf(ibbtc_pool))}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print("-" * 80)
    print(f"wibBTC balance: {wibbtc.balanceOf(ibbtc_pool)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print("-" * 80)
    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    # Update pps
    core.setPricePerShare(1.4e18)
    wibbtc.updatePricePerShare({"from": deployer})

    print("-" * 80)
    print(f"ibBTC balance: {wibbtc.balanceToShares(ibbtc_pool.balances(0))}")
    print(
        f"sbtcCrv underlying balance: {sbtc_pool.get_virtual_price() * ibbtc_pool.balances(1) // int(1e18)}"
    )

    print("-" * 80)
    print(f"wibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print("-" * 80)
    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)

    ibbtc_zap.add_liquidity(ibbtc_pool, [0, 0.4e18, 0, 0], 0, {"from": deployer})
    print("-" * 80)
    print(f"wibBTC balance: {ibbtc_pool.balances(0)}")
    print(f"sbtcCrv balance: {ibbtc_pool.balances(1)}")

    print("-" * 80)
    print(f"Virtual price: {ibbtc_pool.get_virtual_price()}")
    print("-" * 80)
