class Order:
    number = ''
    rate = 0.0
    total = 0.0     # BTC
    amount = 0.0    # LTC
    currency_pair = 'BTC_LTC'
    fee = 0.0

    def __init__(self, order, currency_pair):
        assert isinstance(order, dict)
        self.number = order['orderNumber']
        self.rate = float(order['rate'])
        self.total = float(order['total'])
        self.amount = float(order['amount'])
        self.fee = float(order['fee'])
        self.currency_pair = currency_pair

        if order['type'] == 'buy':
            self.total *= -1
        else:
            self.amount *= -1

    @classmethod
    def from_currency_pair(cls, type, currency_pair):
        order = {'type': type, 'orderNumber': '', 'rate': 0.0, 'total': 0.0, 'amount': 0.0, 'fee': 0.0}
        return cls(order, currency_pair)

    def combine(self, order):
        assert isinstance(order, Order)

        self.number = ''
        self.total += order.total
        self.amount += order.amount
        self.rate = order.rate if self.rate == 0.0 else (self.rate + order.rate) / 2.0
        self.fee += order.fee

        return self

    def type(self):
        if self.total > 0:
            return 'sell'
        return 'buy'

    def is_buy(self):
        return self.total < 0

    def is_sell(self):
        return self.total > 0
