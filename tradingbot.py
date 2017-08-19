import threading
from threading import Timer
import random
import time

from datetime import datetime, timedelta

from configparser import ConfigParser

from trading.esssencial.logger import log
from trading.esssencial.api import Poloniex
from trading.model.order import Order
from trading.model.trade_currency import TradeCurrency
from trading.model.data_source import BacktestDataSource,LiveDataSource
from trading import ITradeAlgorithm, ANN, SniperBacktest, MACD, MyTradeAlgorithm, SimpleStrategy

api_key = ''
api_secret = ''

update_interval = 0

trade_currencies = []

lock = threading.Lock()

main_percent = 'main_percent'
alt_percent = 'alt_percent'
min_buy_profit = 'min_buy_profit'
min_sell_profit = 'min_sell_profit'
new_order_threshold = 'new_order_threshold'
min_main = 'min_main'
min_alt = 'min_alt'
trading_history = 'trading_history'
initial_buy_rate = 'initial_buy_rate'
initial_sell_rate = 'initial_sell_rate'
ann_order_size = 'ann_order_size'
ann_threshold = 'ann_threshold'


def load_defaults(cfg, currency):
    dft_tc = TradeCurrency(currency_pair='',
                           main_percent=float(cfg[currency][main_percent]) / 100.0,
                           alt_percent=float(cfg[currency][alt_percent]) / 100.0,
                           min_buy_profit=float(cfg[currency][min_buy_profit]) / 100.0,
                           min_sell_profit=float(cfg[currency][min_sell_profit]) / 100.0,
                           new_order_threshold=float(cfg[currency][new_order_threshold]) / 100.0,
                           min_main=float(cfg[currency][min_main]),
                           min_alt=float(cfg[currency][min_alt]),
                           trading_history_in_minutes=float(cfg[currency][trading_history]),
                           initial_buy_rate=float(cfg[currency][initial_buy_rate]),
                           initial_sell_rate=float(cfg[currency][initial_sell_rate]),
                           ann_order_size=float(cfg[currency][ann_order_size]),
                           ann_threshold=float(cfg[currency][ann_threshold]))
    return dft_tc


def load_custom(cfg, dft_tc, pair):
    # initialize with defaults
    tc = TradeCurrency.from_tc(dft_tc)
    tc.currency_pair = pair

    # custom values
    if pair in cfg:
        tc.main_percent = float(cfg[pair][main_percent]) / 100 if main_percent in cfg[pair] else tc.main_percent
        tc.alt_percent = float(cfg[pair][alt_percent]) / 100.0 if alt_percent in cfg[pair] else tc.alt_percent
        tc.min_buy_profit = float(cfg[pair][min_buy_profit]) / 100.0 if min_buy_profit in cfg[pair] else tc.min_buy_profit
        tc.min_sell_profit = float(cfg[pair][min_sell_profit]) / 100.0 if min_sell_profit in cfg[pair] else tc.min_sell_profit
        tc.new_order_threshold = float(cfg[pair][new_order_threshold]) / 100.0 if new_order_threshold in cfg[pair] else tc.new_order_threshold
        tc.min_main = float(cfg[pair][min_main] if min_main in cfg[pair] else tc.min_main)
        tc.min_alt = float(cfg[pair][min_alt] if min_alt in cfg[pair] else tc.min_alt)
        tc.trading_history_in_minutes = float(cfg[pair][trading_history] if trading_history in cfg[pair] else tc.trading_history_in_minutes)
        tc.initial_buy_rate = float(cfg[pair][initial_buy_rate] if initial_buy_rate in cfg[pair] else tc.initial_buy_rate)
        tc.initial_sell_rate = float(cfg[pair][initial_sell_rate] if initial_sell_rate in cfg[pair] else tc.initial_sell_rate)
        tc.ann_order_size = float(cfg[pair][ann_order_size] if ann_order_size in cfg[pair] else tc.ann_order_size)
        tc.ann_threshold = float(cfg[pair][ann_threshold] if ann_threshold in cfg[pair] else tc.ann_threshold)

    return tc


def load_config():
    global api_key, api_secret, update_interval, trade_currencies

    cfg = ConfigParser()
    cfg.read('config.cfg')

    api_key = cfg['API']['key']
    api_secret = cfg['API']['secret']

    update_interval = float(cfg['PROCESS']['update_interval']) * 60

    btc_pairs = cfg['CURRENCY']['btc_pairs'].split(',') if 'btc_pairs' in cfg['CURRENCY'] else []
    usdt_pairs = cfg['CURRENCY']['usdt_pairs'].split(',') if 'usdt_pairs' in cfg['CURRENCY'] else []

    dft_tc_btc = load_defaults(cfg, 'BTC')
    dft_tc_usdt = load_defaults(cfg, 'USDT')

    for pair in btc_pairs:
        trade_currencies.append(load_custom(cfg, dft_tc_btc, pair))

    for pair in usdt_pairs:
        trade_currencies.append(load_custom(cfg, dft_tc_usdt, pair))


def update_loop(algorithm):
    with lock:
        assert isinstance(algorithm, ITradeAlgorithm)
        try:
            algorithm.update()
            try_again = False
        except Exception as e:
            log('An error occurred: ' + str(e.args), True)
            try_again = True

        if try_again:
            loop = Timer(random.randint(1, 10), update_loop, [algorithm])
            loop.start()
        else:
            loop = Timer(update_interval + random.randint(1, 10), update_loop, [algorithm])
            loop.start()


def main():
    try:
        load_config()

        template = "{0:20}{1:>15}\t\t\t{2:33}"
        print('initializing')
        poloniex = Poloniex(api_key, api_secret)

        offset = 60 * 24 * 2 #2 Days Offset
        start = datetime.now() - timedelta(days=31)

        #MODE: 'BACKTEST' 'LIVE'
        mode = 'BACKTEST'

        for currency in trade_currencies:
            total_profit = 0

            if mode == 'LIVE':
                for currency in trade_currencies:
                    source = LiveDataSource(currency, poloniex, start, offset, update_interval / 60)
                    algorithm = SimpleStrategy(source, offset)
                    update_loop(algorithm)
                    time.sleep(10)
            if mode == 'BACKTEST':
                print('\n\nBackTest Mode - Gathering Data for ' + currency.currency_pair)
                source = BacktestDataSource(currency, poloniex, start, offset, update_interval / 60)
                algorithm = SimpleStrategy(source, offset)

                #source.plot_result()

                print('Updating... ' + currency.currency_pair)
                print(template.format('Initial Balances:', '$' + "{0:.2f}".format(source.main_balance), str(source.alt_balance)))
                while algorithm.update():
                    continue
                total_main = 0
                total_alt = 0
                total_fee = 0
                total_trades = algorithm.winning_trades + algorithm.losing_trades
                accuracy = (abs(algorithm.winning_trades - algorithm.losing_trades) / total_trades) * 100 if total_trades > 0 else 0
                for order in algorithm.data_source.orders:
                    assert isinstance(order, Order)
                    total_main += abs(order.total)
                    total_alt += abs(order.amount)
                    total_fee += order.fee

                main_profit = algorithm.data_source.main_balance - algorithm.data_source.main_balance_init
                alt_profit = algorithm.data_source.alt_balance - algorithm.data_source.alt_balance_init
                highest_bid = float(poloniex.returnTicker()[currency.currency_pair]['highestBid'])
                profit = (alt_profit * highest_bid) + main_profit
                total_profit += profit

                print(template.format('Final Balances:', '$' + "{0:.2f}".format(algorithm.data_source.main_balance), str(algorithm.data_source.alt_balance)))
                print(template.format('Difference:', '$' + "{0:.2f}".format(main_profit), str(alt_profit)))
                print(template.format('Total Moved:', '$' + "{0:.2f}".format(total_main), str(total_alt)))
                print(template.format('Accuracy: ' , '%' + "{0:.2f}".format(accuracy), str(total_alt)))
                print(template.format('Fees:' , '$' + "{0:.2f}".format(total_fee), str(total_alt)))
                print(template.format('Winning Trades:' , str(algorithm.winning_trades), str(total_alt)))
                print(template.format('Losing  Trades:' , str(algorithm.losing_trades), str(total_alt)))
                print(template.format('Profit:' , '$' + "{0:.2f}".format(profit), str(total_alt)))
                print(template.format('Total Profit:', '$' + "{0:.2f}".format(profit), str(total_profit)))

    except KeyboardInterrupt:
        quit()


if __name__ == '__main__':
    main()
