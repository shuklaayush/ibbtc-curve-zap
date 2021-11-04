import pytest
from pytest import approx

from conftest import MAX_UINT256


@pytest.fixture(scope="module")
def ibbtc_pool(Contract):
    yield Contract("0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B")


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
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})


# Test to add liquidity to ibbtc pool
def test_add_liquidity(deployer, ibbtc_pool, ibbtc_zap, ibbtc, renbtc, wibbtc, sbtcCrv):
    # add ibbtc liquidity
    amounts = [ibbtc.balanceOf(deployer) // 10, 0, 0, 0]

    wibbtc_shares_before = wibbtc.sharesOf(ibbtc_pool)
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})
    wibbtc_shares_after = wibbtc.sharesOf(ibbtc_pool)

    # depositing ibbtc into curve pool, wibbtc shares of curve pool should increase propotionally to amount of ibbtc shares deposited
    assert float(wibbtc_shares_after - wibbtc_shares_before) == approx(
        amounts[0], rel=1e-2
    )

    # add renbtc liquidity
    # when depositing renbtc/wbtc/sbtc the balance of lp token will increase

    amounts = [0, renbtc.balanceOf(deployer) // 10, 0, 0]

    sbtcCrv_before = sbtcCrv.balanceOf(ibbtc_pool)
    ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})
    sbtcCrv_after = sbtcCrv.balanceOf(ibbtc_pool)

    assert sbtcCrv_after > sbtcCrv_before


# Test to remove liquidity from ibbtc pool in equal proportions
def test_remove_liquidity(
    deployer, ibbtc_pool, ibbtc_zap, ibbtc, renbtc, wbtc, sbtc, wibbtc, sbtcCrv
):
    min_amounts = [0] * 4

    balance_ibbtc_before = ibbtc.balanceOf(deployer)
    balance_renbtc_before = renbtc.balanceOf(deployer)
    balance_wbtc_before = wbtc.balanceOf(deployer)
    balance_sbtc_before = sbtc.balanceOf(deployer)
    balance_wibbtc_before_ibbtc_pool = wibbtc.balanceOf(ibbtc_pool)
    balance_sbtcCrv_before = sbtcCrv.balanceOf(ibbtc_pool)

    ibbtc_zap.remove_liquidity(
        ibbtc_pool,
        ibbtc_pool.balanceOf(deployer) // 10,
        min_amounts,
        {"from": deployer},
    )

    balance_ibbtc_after = ibbtc.balanceOf(deployer)
    balance_renbtc_after = renbtc.balanceOf(deployer)
    balance_wbtc_after = wbtc.balanceOf(deployer)
    balance_sbtc_after = sbtc.balanceOf(deployer)
    balance_wibbtc_after_ibbtc_pool = wibbtc.balanceOf(ibbtc_pool)
    balance_sbtcCrv_after = sbtcCrv.balanceOf(ibbtc_pool)

    # deployer ibbtc, renbtc, wbtc, sbtc balance should increase
    assert balance_ibbtc_after > balance_ibbtc_before
    assert balance_renbtc_after > balance_renbtc_before
    assert balance_wbtc_after > balance_wbtc_before
    assert balance_sbtc_after > balance_sbtc_before

    # ibbtc_pool wibbtc balance should decrease
    assert balance_wibbtc_before_ibbtc_pool > balance_wibbtc_after_ibbtc_pool

    # ibbtc_pool lptoken balance should decrease
    assert balance_sbtcCrv_after < balance_sbtcCrv_before


# Test to remove liquidity from ibbtc pool by removing a single coin
def test_remove_one_coin(deployer, ibbtc_pool, ibbtc_zap, ibbtc, renbtc, wbtc, sbtc):
    balance = ibbtc_pool.balanceOf(deployer)

    # remove ibbtc
    amount = balance // 4
    before_ibbtc_balance = ibbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(ibbtc_pool, amount, 0, 0, {"from": deployer})
    after_ibbtc_balance = ibbtc.balanceOf(deployer)
    assert after_ibbtc_balance > before_ibbtc_balance

    # remove renbtc
    amount = balance // 4
    before_renbtc_balance = renbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(ibbtc_pool, amount, 1, 0, {"from": deployer})
    after_renbtc_balance = renbtc.balanceOf(deployer)
    assert after_renbtc_balance > before_renbtc_balance

    # remove wbtc
    amount = balance // 4
    before_wbtc_balance = wbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(ibbtc_pool, amount, 2, 0, {"from": deployer})
    after_wbtc_balance = wbtc.balanceOf(deployer)
    assert after_wbtc_balance > before_wbtc_balance

    # remove sbtc
    amount = balance // 4
    before_sbtc_balance = sbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(ibbtc_pool, amount, 3, 0, {"from": deployer})
    after_sbtc_balance = sbtc.balanceOf(deployer)
    assert after_sbtc_balance > before_sbtc_balance


# Testing calc_withdraw_one_coin
def test_calc_withdraw_one_coin(deployer, ibbtc_pool, ibbtc_zap, ibbtc):
    amount = ibbtc_pool.balanceOf(deployer) // 10
    withdraw_amount_ibbtc = ibbtc_zap.calc_withdraw_one_coin(
        ibbtc_pool, amount, 0, {"from": deployer}
    )

    before_ibbtc_shares = ibbtc.balanceOf(deployer)
    ibbtc_zap.remove_liquidity_one_coin(ibbtc_pool, amount, 0, 0, {"from": deployer})
    after_ibbtc_shares = ibbtc.balanceOf(deployer)

    assert float(after_ibbtc_shares - before_ibbtc_shares) == approx(
        withdraw_amount_ibbtc, rel=1e-2
    )


# Testing swap between different pairs
def test_swap(deployer, ibbtc_pool, ibbtc_zap, ibbtc, renbtc, wbtc):
    # swap ibbtc -> wbtc
    ibbtc_amount = ibbtc.balanceOf(deployer) // 10

    balance_wbtc_before_swap = wbtc.balanceOf(deployer)
    ibbtc_zap.exchange_underlying(ibbtc_pool, 0, 2, ibbtc_amount, 0)
    balance_wbtc_after_swap = wbtc.balanceOf(deployer)

    assert balance_wbtc_after_swap > balance_wbtc_before_swap

    # swap wbtc -> ibbtc
    wbtc_amount = wbtc.balanceOf(deployer) // 10

    balance_ibbtc_before_swap = ibbtc.balanceOf(deployer)
    ibbtc_zap.exchange_underlying(ibbtc_pool, 2, 0, wbtc_amount, 0)
    balance_ibbtc_after_swap = ibbtc.balanceOf(deployer)

    assert balance_ibbtc_after_swap > balance_ibbtc_before_swap

    # swap wbtc -> renbtc
    wbtc_amount = wbtc.balanceOf(deployer) // 10

    balance_renbtc_before_swap = renbtc.balanceOf(deployer)
    ibbtc_zap.exchange_underlying(ibbtc_pool, 2, 1, wbtc_amount, 0)
    balance_renbtc_after_swap = renbtc.balanceOf(deployer)

    assert balance_renbtc_after_swap > balance_renbtc_before_swap

    # swap ibbtc -> wbtc -> ibbtc
    balance_ibbtc_before_swap = ibbtc.balanceOf(deployer)

    balance_wbtc_before_swap = wbtc.balanceOf(deployer)
    ibbtc_zap.exchange_underlying(ibbtc_pool, 0, 2, ibbtc_amount, 0)
    balance_wbtc_after_swap = wbtc.balanceOf(deployer)

    ibbtc_zap.exchange_underlying(
        ibbtc_pool, 2, 0, balance_wbtc_after_swap - balance_wbtc_before_swap, 0
    )
    balance_ibbtc_after_swap = ibbtc.balanceOf(deployer)

    assert float(balance_ibbtc_after_swap) == approx(
        balance_ibbtc_before_swap, rel=1e-2
    )


def test_zap_flow(deployer, ibbtc_pool, ibbtc_zap, ibbtc):
    balance_ibbtc_before = ibbtc.balanceOf(deployer)

    # deposit ibbtc
    amounts = [ibbtc.balanceOf(deployer) // 2, 0, 0, 0]
    tx = ibbtc_zap.add_liquidity(ibbtc_pool, amounts, 0, {"from": deployer})

    # remove liquidity in terms of ibbtc
    ibbtc_zap.remove_liquidity_one_coin(
        ibbtc_pool, tx.return_value, 0, 0, {"from": deployer}
    )

    balance_ibbtc_after = ibbtc.balanceOf(deployer)

    assert float(balance_ibbtc_after) == approx(balance_ibbtc_before, rel=1e-2)
