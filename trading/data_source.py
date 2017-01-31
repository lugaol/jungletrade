from trading import Order
from trading.trade_currency import TradeCurrency
from trading.api import Poloniex
from trading import OrderHistory
from datetime import datetime, timedelta
from time import time

class IDataSource:
    currency = None
    symbol_main = ''
    symbol_alt = ''
    main_balance = 0
    alt_balance = 0
    main_balance_init = 0
    alt_balance_init = 0
    highest_bid = 0.0
    lowest_ask = 0.0
    orders = []

    def __init__(self, currency):
        assert isinstance(currency, TradeCurrency)
        self.currency = currency
        self.symbol_main = self.currency.currency_pair.split('_')[0]
        self.symbol_alt = self.currency.currency_pair.split('_')[1]

    def update(self):
        return False

    def security(self, period, value, num_periods=2):
        raise NotImplementedError()

    def buy(self, alt):
        raise NotImplementedError()

    def sell(self, alt):
        raise NotImplementedError()

    @staticmethod
    def sma(data,window):
        if len(data) < window:
            return None
        return sum(data[-window:]) / float(window)

    @staticmethod
    def wma(series, amounts):
        avg = 0
        for i in range(len(series)):
            avg += series[i] * amounts[i]

        return avg / sum(amounts)

    def ema(self, data, window=-1):
        if len(data) == 0:
            return 0
        elif len(data) == 1:
            return data[0]

        if window < 0:
            window = int(len(data) / 2)

        c = 2.0 / (window + 1)
        current_ema = self.sma(data[-window * 2:-window], window)
        for value in data[-window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema

    @staticmethod
    def crossover(series1, series2):
        return series1[1] < series2[1] and series1[0] > series2[0]

    @staticmethod
    def crossunder(series1, series2):
        return series1[1] > series2[1] and series1[0] < series2[0]


class BacktestDataSource(IDataSource):
    all_data = []
    data = []
    data_offset = 0
    update_interval = 5

    def __init__(self, currency, poloniex, start, data_offset, update_interval):
        super().__init__(currency)
        assert isinstance(poloniex, Poloniex)

        self.update_interval = update_interval
        balances = poloniex.returnBalances()
        self.all_data = poloniex.returnChartData(currencyPair=self.currency.currency_pair, period=self.update_interval * 60, start=start)

        self.data_offset = int(data_offset / update_interval)
        self.data = self.all_data[:self.data_offset]
        self.highest_bid = self.lowest_ask = self.data[-1]['close']

        self.main_balance_init = float(balances[self.symbol_main])
        self.alt_balance_init = float(balances[self.symbol_alt])
        self.main_balance = float(balances[self.symbol_main])
        self.alt_balance = float(balances[self.symbol_alt])

    def update(self):
        if len(self.all_data) <= self.data_offset:
            return False

        self.all_data = self.all_data[1:]
        self.data = self.all_data[:self.data_offset]
        self.highest_bid = self.lowest_ask = self.data[-1]['close']

        return True

    def buy(self, alt):
        main = alt * self.lowest_ask
        if (self.main_balance - main) >= self.currency.min_main:
            order = Order({'type': 'buy', 'orderNumber': '', 'rate': self.lowest_ask, 'total': main, 'amount': alt, 'fee': main * 0.0025}, self.currency.currency_pair)
            self.main_balance += order.total - order.fee
            self.alt_balance += order.amount
            self.orders.insert(0, order)
            return order

        return None

    def sell(self, alt):
        if (self.alt_balance - alt) >= self.currency.min_main:
            main = alt * self.highest_bid
            order = Order({'type': 'sell', 'orderNumber': '', 'rate': self.highest_bid, 'total': main, 'amount': alt, 'fee': main * 0.0025}, self.currency.currency_pair)
            self.main_balance += order.total
            self.alt_balance += order.amount
            self.orders.insert(0, order)
            return order

        return None

    def trade_history(self):
        return self.orders


class LiveDataSource(IDataSource):
    all_data = []
    data = []
    data_offset = 0
    update_interval = 5
    buy_order = None
    sell_order = None
    orderHistory = None
    exchange = None

    def __init__(self, currency, exchange, start, data_offset, update_interval):
        super().__init__(currency)
        assert isinstance(exchange, Poloniex)
        self.exchange = exchange
        self.update_interval = update_interval

    def update(self):
        balances = self.exchange.returnBalances()
        if 'error' in balances:
            raise RuntimeError(balances['error'])
        else:
            self.main_balance = float(balances[self.symbol_main])
            self.alt_balance = float(balances[self.symbol_alt])

        ticker = self.exchange.returnTicker()
        if 'error' in ticker:
            raise RuntimeError(ticker['error'])
        else:
            self.highest_bid = float(ticker[self.currency.currency_pair]['highestBid'])
            self.lowest_ask = float(ticker[self.currency.currency_pair]['lowestAsk'])

        start = datetime.now() - timedelta(hours=24)

        self.data = self.exchange.returnChartData(currencyPair=self.currency.currency_pair, period=self.update_interval * 60, start=start)

        minutes = self.currency.trading_history_in_minutes
        history = OrderHistory(self.exchange, minutes, self.currency.currency_pair)
        self.orders = history.orders
        return True

    def buy(self, amount):
        order = self.exchange.buy(currencyPair=self.currency_pair, rate=self.lowest_ask, amount=amount)
        if 'error' in order:
            raise RuntimeError(order['error'])
        else:
            order_number = order['orderNumber']  # wait until the trade propagates before returning.
            order = None
            loops = 0
            while order is None and loops < 300:
                time.sleep(1)
                order = OrderHistory(self.exchange, minutes=60, currency_pair=self.currency_pair).get_order(order_number)
                loops += 1

            self.buy_order = order
            return self.buy_order

    def sell(self, amount):
        order = self.exchange.sell(currencyPair=self.currency_pair, rate=self.highest_bid, amount=amount)
        if 'error' in order:
            raise RuntimeError(order['error'])
        else:
            order_number = order['orderNumber']

            # wait until the trade propagates before returning.
            order = None
            loops = 0
            while order is None and loops < 300:
                time.sleep(1)
                order = OrderHistory(self.exchange, minutes=60, currency_pair=self.currency_pair).get_order(order_number)
                loops += 1

            self.sell_order = order
            return self.sell_order

    def trade_history(self):
        return self.orders