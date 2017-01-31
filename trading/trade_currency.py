class TradeCurrency:
    alt_percent = 0.0
    main_percent = 0.0
    min_buy_profit = 0.0
    min_sell_profit = 0.0
    new_order_threshold = 0.0
    trading_history_in_minutes = 0
    currency_pair = ''
    min_main = 0.0
    min_alt = 0.0
    initial_buy_rate = 0.0
    initial_sell_rate = 0.0
    ann_order_size = 0.0
    ann_threshold = 0.0

    def __init__(self, currency_pair,
                 alt_percent,
                 main_percent,
                 min_buy_profit,
                 min_sell_profit,
                 new_order_threshold,
                 min_main,
                 min_alt,
                 trading_history_in_minutes,
                 initial_buy_rate,
                 initial_sell_rate,
                 ann_order_size,
                 ann_threshold):

        self.alt_percent = alt_percent
        self.main_percent = main_percent
        self.min_buy_profit = min_buy_profit
        self.min_sell_profit = min_sell_profit
        self.new_order_threshold = new_order_threshold
        self.min_main = min_main
        self.min_alt = min_alt
        self.trading_history_in_minutes = trading_history_in_minutes
        self.currency_pair = currency_pair
        self.initial_buy_rate = initial_buy_rate
        self.initial_sell_rate = initial_sell_rate
        self.ann_order_size = ann_order_size
        self.ann_threshold = ann_threshold

    @classmethod
    def from_tc(cls, tc):
        assert isinstance(tc, TradeCurrency)
        ntc = TradeCurrency(currency_pair=tc.currency_pair,
                            alt_percent=tc.alt_percent,
                            main_percent=tc.main_percent,
                            min_buy_profit=tc.min_buy_profit,
                            min_sell_profit=tc.min_sell_profit,
                            new_order_threshold=tc.new_order_threshold,
                            min_main=tc.min_main,
                            min_alt=tc.min_alt,
                            trading_history_in_minutes=tc.trading_history_in_minutes,
                            initial_buy_rate=tc.initial_buy_rate,
                            initial_sell_rate=tc.initial_sell_rate,
                            ann_order_size=tc.ann_order_size,
                            ann_threshold=tc.ann_threshold)
        return ntc

