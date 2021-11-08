import pytest

MAX_UINT256 = 2 ** 256 - 1


@pytest.fixture(scope="session")
def weth(interface):
    yield interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="session")
def wbtc(interface):
    yield interface.ERC20("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")


@pytest.fixture(scope="session")
def renbtc(interface):
    yield interface.ERC20("0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D")


@pytest.fixture(scope="session")
def sbtc(interface):
    yield interface.ERC20("0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6")


@pytest.fixture(scope="session")
def ibbtc(Contract):
    yield Contract("0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F")


@pytest.fixture(scope="session")
def wibbtc(Contract):
    yield Contract("0x8751D4196027d4e6DA63716fA7786B5174F04C15")


@pytest.fixture(scope="session")
def sbtc_pool(Contract):
    yield Contract("0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714")


@pytest.fixture(scope="session")
def sbtcCrv(Contract):
    yield Contract("0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3")


@pytest.fixture(scope="session")
def router(Contract):
    yield Contract("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")


@pytest.fixture(scope="session")
def deployer(accounts):
    yield accounts[0]


@pytest.fixture(autouse=True)
def get_tokens(deployer, router, weth, ibbtc, wbtc, sbtc_pool):
    # Get ibbtc
    router.swapETHForExactTokens(
        2 * 10 ** ibbtc.decimals(),
        [weth, wbtc, ibbtc],
        deployer,
        MAX_UINT256,
        {"from": deployer, "value": deployer.balance()},
    )

    # Get wbtc
    router.swapETHForExactTokens(
        3 * 10 ** wbtc.decimals(),
        [weth, wbtc],
        deployer,
        MAX_UINT256,
        {"from": deployer, "value": deployer.balance()},
    )
    # Get renbtc, sbtc from curve sbtc pool
    wbtc.approve(sbtc_pool, MAX_UINT256, {"from": deployer})
    # renbtc
    sbtc_pool.exchange(1, 0, 10 ** wbtc.decimals(), 0, {"from": deployer})
    # sbtc
    sbtc_pool.exchange(1, 2, 10 ** wbtc.decimals(), 0, {"from": deployer})


@pytest.fixture(autouse=True)
def set_approvals(deployer, ibbtc, wbtc, renbtc, sbtc, ibbtc_zap):
    # Approvals
    ibbtc.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})
    renbtc.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})
    wbtc.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})
    sbtc.approve(ibbtc_zap, MAX_UINT256, {"from": deployer})


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
