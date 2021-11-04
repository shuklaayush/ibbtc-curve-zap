# Curve ibbtc zap for wibbtc/crvRenWSBTC metapool
With this zap users can now directly interact with curve wrapped ibbtc metapool using ibbtc to deposit/withdraw/swap of ibbtc into the curve wrapped ibbtc metapool thereby hiding wibbtc from the end users

## Changes
The [DepositZapBTC.vy](https://github.com/curvefi/curve-factory/blob/master/contracts/zaps/DepositZapBTC.vy) has been modified to work with wrapping and unwrapping of ibbtc with the following changes:
- function `add_liquidity`: if the user is depositing ibbtc then (__deposit_amounts[0]!=0) we wrap the ibbtc to wibbtc and deposit it into the curve wibbtc metapool
- function `remove_liquidity`: as remove_liquidity removes all tokens according to `_burn_amount`, the withdrawn wibbtc from curve metapool is unwrapped to ibbtc and transferred to user.
- function `remove_liquidity_one_coin`: if i=0 ie. we are removing liquidity in terms of ibbtc then, the withdrawn wibbtc from curve metapool is unwrapped to ibbtc and transferred to user.
- function `swap`: Swap function added which wraps/unwrap if we are swapping from/to ibbtc
- function `calc_withdraw_one_coin`: if withdrawn coin is ibbtc (ie. i=0) it calculates the amount of ibbtc shares received
- function `calc_token_amount`: changes ibbtc shares to wibbtc balance and then calculates addition or reduction in token supply from a deposit or withdrawal
- function `remove_liquidity_imbalance`: if there is an imbalance, the amount of wibbtc received would be converted to ibbtc before transferring to the `msg.sender`
