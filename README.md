# Poloniex Trading Bot

Create a file config.cfg and provide it with your api key and secret.  
See config.cfg.example.  

Note that this program is very much in the beta stage still.  
No warranty express or implied is granted for the use of this software.  

The stock market is volatile and profits are not guaranteed.  
Trade at your own risk, and never front more than you can afford to lose.  


***
# Algorithm

This algorithm is based loosely on the algorithm mentioned by "GUNBOT"  

When prices are above both the ema lines the algorithm marks the currency as sellable.
When prices are below both the ema lines, the algorithm marks the currency as buyable.
When prices are in-between the ema lines, nothing is done.

If the profit percentage is at or above the one specified in the config file, the algorithm begins to buy or sell in the percentages mentioned in the cfg file.

The "new_order_threshold" can be considered something of a stop loss. If you purchased a currency and it falls below this threshold, it makes a new purchase at that price. In this manner it can produce greater profits later when the currency goes back up in price.

When buying and selling it never purchases or sells more than what was previously bought or sold respectively plus the profit gained on the trade.
This allows wiggle room for you to make your own manual trades while this bot is running.

***

# Coming soon

XMR and ETH main currency exchanges.