from trading import Poloniex, Order
from datetime import datetime, timedelta


class OrderHistory:
    poloniex = None
    orders = []
    currency_pair = ''
    minutes = 0

    def __init__(self, poloniex, minutes, currency_pair='BTC_LTC'):
        assert isinstance(poloniex, Poloniex)
        self.poloniex = poloniex
        self.minutes = max(minutes, 5)
        self.currency_pair = currency_pair
        self.update()

    def update(self):
        self.orders.clear()
        start = datetime.now() - timedelta(minutes=self.minutes)
        history = self.poloniex.returnAccountTradeHistory(self.currency_pair, start)
        if 'error' in history:
            raise RuntimeError(history['error'])
        else:
            for order in history:
                self.orders.insert(0, Order(order, self.currency_pair))

    def get_order(self, order_number):
        assert isinstance(order_number, str)
        for order in self.orders:
            assert isinstance(order, Order)
            if order.number == order_number:
                return order

        return None
        # raise IndexError('The order with the specified number does not exist')
