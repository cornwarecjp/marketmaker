# Market Maker

Market Maker is a very simple trading bot.

## Market support

Currently, Market Maker only supports BTC/EUR trading on the BL3P exchange
( https://bl3p.eu ).

## Trading algorithm

Market Maker tries to keep the ratio between the value of BTC funds and EUR
funds within a certain margin around a configured target ratio.
If the BTC/EUR exchange rate rises, the value of the BTC funds rises with
respect to the value of the EUR funds; once a certain threshold is reached,
some of the BTC funds are sold to move back to the target ratio.
Similarly, if the BTC/EUR exchange rate drops, the value of the EUR funds drops
with respect to the value of the BTC funds; once a certain threshold is reached,
some of the EUR funds are sold to move back to the target ratio.

Because of the margin between the buy and the sell action, in a market that
continuously moves up and down, buys tend to happen at a slightly lower price
and sells tend to happen at a slightly higher price.
The difference, after subtraction of transaction fees, is profit.

Market Maker performs this strategy by placing bid and ask limit orders in the
market, based on the current BTC and EUR balance in the account.
It periodically checks whether the balance has changed (for instance, because
an order has been (partially) executed); in that case, it replaces the existing
order book with a new one, based on the new balance.

So, if you manually deposit/withdraw while Market Maker is active, it will
automatically adjust its order book; for instance, if you deposit BTC, it will
probably sell some of that BTC to rebalance the EUR / BTC value.
If you manually perform a buy/sell while Market maker is active, it will
probably immediately undo your trade, to bring the EUR / BTC balance back to its
target.
When a change of orders is triggered, Market Maker will remove any open orders
it doesn't want for its own strategy.

The step size between orders is incrementing further away from the center:
normally, these far-away orders are only reached if there is a sudden 'whale'
buy/sell that happens before Market Maker notices the change.
By having further-away steps, the hope is to increase the margin, and therefore
the profit, in these cases.
In a calm market, only the innermost offers are ever touched; when that happens,
the order book is replaced before the outer offers can be executed.

## Failure modes

I expect every possible trading algorithm to have failure modes.
This algorithm is no exception.
I guess that, if one of the two asset values actually drops to zero,
Market Maker will continue to buy it all the way down, to such a large degree
that its other asset amount will also become zero.
This will make you lose all funds in the account managed by Market Maker.
Market Maker probably performs best in a horizontal market with a large amount
of volatility.

Even then, I offer no guarantee or warranty of any kind: see also the warranty
disclaimer in the LICENSE file. Deploying Market Maker is your own choice;
you are responsible for the consequences, and you should do your own analysis
on what failure modes exist in your situation.

## Impact on the market

Market Maker is a contrarian trader: when everyone else sells, the price drops,
and Market Maker starts buying; when everyone else buys, the price rises,
and Market Maker starts selling.
When deployed with large funds (possibly the collective result of many traders
simultaneously running Market Maker), this should have a dampening effect on
price fluctuations, reducing volatility.

Running Market Maker continuously can be seen as providing a service to other
traders who want the ability to immediately buy or sell at certain moments.
People running Market Maker add liquidity to the market that makes this
possible.

## Installation

For trading on BL3P, A verified BL3P account is needed.

In BL3P, you need to create an API key that gives rights to read data and to
perform trades. For better security, if you intend to run Market Maker from a
fixed IP address, you should set this as a fixed IP address for the API key in
BL3P. When BL3P gives you the private key of the API key, make sure to store it
somewhere (in a secure location).

Market Maker requires Python3 and pycurl. In Debian, you can get pycurl by
installing the package python3-pycurl.

For the rest, installation simply consists of copying this directory to where
you want to run Market Maker, create a marketmaker.cfg file
(see marketmaker.cfg.example), and run marketmaker.py from this directory.
Market Maker does not locally store any data, so for security you can make
everything read-only.

The most important thing, before starting Market Maker, is to fill in the BL3P
API public and private keys in marketmaker.cfg. Slightly less important,
you can check whether the default settings from marketmaker.cfg.example are
acceptable to you, and change them to fit your needs.

Market Maker does not come with operating system integration; it is your own
job to make something like a start-up script that automatically starts Market
Maker when your server boots. It is recommended to redirect Market Maker's
stdout to a software logging service like syslog.

