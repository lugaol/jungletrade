import time

from trading import Poloniex, OrderHistory


class Trade:
    buy_order = None
    sell_order = None

    def __init__(self, buy=None, sell=None):
        self.buy_order = buy
        self.sell_order = sell

    def buy(self, poloniex, rate, amount, currency_pair='BTC_LTC'):
        assert isinstance(poloniex, Poloniex)

        order = poloniex.buy(currencyPair=currency_pair, rate=rate, amount=amount)
        if 'error' in order:
            raise RuntimeError(order['error'])
        else:
            order_number = order['orderNumber']

            # wait until the trade propagates before returning.
            order = None
            loops = 0
            while order is None and loops < 300:
                time.sleep(1)
                order = OrderHistory(poloniex, minutes=60, currency_pair=currency_pair).get_order(order_number)
                loops += 1

            self.buy_order = order
            return self.buy_order

    def sell(self, poloniex, rate, amount, currency_pair='BTC_LTC'):
        assert isinstance(poloniex, Poloniex)

        order = poloniex.sell(currencyPair=currency_pair, rate=rate, amount=amount)
        if 'error' in order:
            raise RuntimeError(order['error'])
        else:
            order_number = order['orderNumber']

            # wait until the trade propagates before returning.
            order = None
            loops = 0
            while order is None and loops < 300:
                time.sleep(1)
                order = OrderHistory(poloniex, minutes=60, currency_pair=currency_pair).get_order(order_number)
                loops += 1

            self.sell_order = order
            return self.sell_order

    def complete(self):
        return self.buy_order is not None and self.sell_order is not None

    def empty(self):
        return self.buy_order is None and self.sell_order is None

    def is_buy(self):
        return not self.complete() and self.buy_order is not None

    def is_sell(self):
        return not self.complete() and self.sell_order is not None

    def total_amount(self):
        amount = 0.0

        if self.buy_order is not None:
            amount += self.buy_order.amount

        if self.sell_order is not None:
            amount += self.sell_order.amount

        return amount
