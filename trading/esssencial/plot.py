# THIS VERSION IS FOR PYTHON 3 #

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pylab
from matplotlib.dates import HourLocator, DateFormatter

from trading.esssencial.mpl_finance import candlestick2_ohlc


class Plot:
    data = []
    orders = []
    pair = 'BTC_USD'
    ma1 = 10
    ma2 = 50

    def __init__(self, data, orders, pair):
        matplotlib.rcParams.update({'font.size': 9})
        self.data = data
        self.orders = orders
        self.pair = pair

    def rsiFunc(self,prices, n=14):
        deltas = np.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi

    def movingaverage(self,values, window):
        weigths = np.repeat(1.0, window) / window
        smas = np.convolve(values, weigths, 'valid')
        return smas  # as a numpy array

    def exp_moving_average(self,values, window):
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        a = np.convolve(values, weights, mode='full')[:len(values)]
        a[:window] = a[window]
        return a

    def computeMACD(self,x, slow=26, fast=12):
        """
         compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
         return value is emaslow, emafast, macd which are len(x) arrays
         """
        emaslow = self.exp_moving_average(x, slow)
        emafast = self.exp_moving_average(x, fast)
        return emaslow, emafast, emafast - emaslow

    def bytespdate2num(self,fmt, encoding='utf-8'):
        strconverter = mdates.strpdate2num(fmt)

        def bytesconverter(b):
            s = b.decode(encoding)
            return strconverter(s)

        return bytesconverter

    def graph_data(self):
        try:
            openp = []
            highp = []
            lowp = []
            closep = []
            date = []
            volume = []
            x = 0
            newAr = []

            while x < 600:
                # self.data[x]['date'] = datetime.datetime.fromtimestamp(int(self.data[x]['date'])).strftime('%Y-%m-%d %H:%M:%S')
                append_line = self.data[x]['date'], self.data[x]['open'], self.data[x]['high'], self.data[x]['low'], \
                              self.data[x]['close'], self.data[x]['volume']
                newAr.append(append_line)
                openp.append(self.data[x]['open'])
                highp.append(self.data[x]['high'])
                lowp.append(self.data[x]['low'])
                closep.append(self.data[x]['close'])
                date.append(self.data[x]['date'])
                volume.append(self.data[x]['volume'])
                x += 1

            Av1 = self.movingaverage(closep, self.ma1)
            Av2 = self.movingaverage(closep, self.ma2)

            SP = len(date[self.ma1 - 1:])
            SP2 = len(date[self.ma2 - 1:])

            fig = plt.figure(facecolor='#07000d')

            ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, axisbg='#07000d')
            candlestick2_ohlc(ax1, openp[-SP:], highp[-SP:], lowp[-SP:], closep[-SP:], width=.6, colorup='#53c156', colordown='#ff1717')



            Label1 = str(self.ma1) + ' SMA'
            Label2 = str(self.ma2) + ' SMA'

            ax1.plot(date[-SP:], Av1[-SP:], '#e1edf9', label=Label1, linewidth=1.5)
            ax1.plot(date[-SP2:], Av2[-SP2:], '#4ee6fd', label=Label2, linewidth=1.5)

            hour = HourLocator(interval=1)
            hourformatter = DateFormatter('%H:%M')
            ax1.grid(True, color='w')
            ax1.xaxis.set_major_locator(hour)
            ax1.xaxis.set_major_formatter(hourformatter)
            ax1.yaxis.label.set_color("w")
            ax1.spines['bottom'].set_color("#5998ff")
            ax1.spines['top'].set_color("#5998ff")
            ax1.spines['left'].set_color("#5998ff")
            ax1.spines['right'].set_color("#5998ff")
            ax1.tick_params(axis='y', colors='w')
            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
            ax1.tick_params(axis='x', colors='w')
            plt.ylabel('Stock price and Volume')

            maLeg = plt.legend(loc=9, ncol=2, prop={'size': 7},
                               fancybox=True, borderaxespad=0.)
            maLeg.get_frame().set_alpha(0.4)
            textEd = pylab.gca().get_legend().get_texts()
            pylab.setp(textEd[0:5], color='w')

            volumeMin = 0

            ax0 = plt.subplot2grid((6, 4), (0, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
            rsi = self.rsiFunc(closep)
            rsiCol = '#c1f9f7'
            posCol = '#386d13'
            negCol = '#8f2020'

            ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
            ax0.axhline(70, color=negCol)
            ax0.axhline(30, color=posCol)
            ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:] >= 70), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:] <= 30), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.set_yticks([30, 70])
            ax0.yaxis.label.set_color("w")
            ax0.spines['bottom'].set_color("#5998ff")
            ax0.spines['top'].set_color("#5998ff")
            ax0.spines['left'].set_color("#5998ff")
            ax0.spines['right'].set_color("#5998ff")
            ax0.tick_params(axis='y', colors='w')
            ax0.tick_params(axis='x', colors='w')
            plt.ylabel('RSI')

            ax1v = ax1.twinx()
            ax1v.fill_between(date[-SP:], volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.4)
            ax1v.axes.yaxis.set_ticklabels([])
            ax1v.grid(False)
            ###Edit this to 3, so it's a bit larger
            ax1v.set_ylim(0, 3 * max(volume))
            ax1v.spines['bottom'].set_color("#5998ff")
            ax1v.spines['top'].set_color("#5998ff")
            ax1v.spines['left'].set_color("#5998ff")
            ax1v.spines['right'].set_color("#5998ff")
            ax1v.tick_params(axis='x', colors='w')
            ax1v.tick_params(axis='y', colors='w')
            ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
            fillcolor = '#00ffe8'
            nslow = 26
            nfast = 12
            nema = 9
            emaslow, emafast, macd = self.computeMACD(closep)
            ema9 = self.exp_moving_average(macd, nema)
            ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
            ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
            ax2.fill_between(date[-SP:], macd[-SP:] - ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)

            plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
            ax2.spines['bottom'].set_color("#5998ff")
            ax2.spines['top'].set_color("#5998ff")
            ax2.spines['left'].set_color("#5998ff")
            ax2.spines['right'].set_color("#5998ff")
            ax2.tick_params(axis='x', colors='w')
            ax2.tick_params(axis='y', colors='w')
            plt.ylabel('MACD', color='w')
            ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
            for label in ax2.xaxis.get_ticklabels():
                label.set_rotation(45)

            plt.suptitle(self.pair.upper(), color='w')
            plt.setp(ax0.get_xticklabels(), visible=False)
            plt.setp(ax1.get_xticklabels(), visible=False)

            ax1.annotate('Big news!', (date[510], Av1[510]),
                         xytext=(0.8, 0.9), textcoords='axes fraction',
                         arrowprops=dict(facecolor='white', shrink=0.05),
                         fontsize=14, color='w',
                         horizontalalignment='right', verticalalignment='bottom')

            for order in self.orders:
                if order.is_buy():
                    ax1.annotate('buy',
                                 (date[210], Av1[210]), xycoords='data',
                                 xytext=(-15, 25), textcoords='offset points',
                                 arrowprops=dict(facecolor='green', shrink=0.05),
                                 horizontalalignment='right', verticalalignment='bottom')
                elif order.is_sell():
                    ax1.annotate('sell',
                                 (date[210], Av1[210]), xycoords='data',
                                 xytext=(-15, 25), textcoords='offset points',
                                 arrowprops=dict(facecolor='red', shrink=0.05),
                                 horizontalalignment='right', verticalalignment='bottom')

            plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
            plt.show()
            fig.savefig('example.png', facecolor=fig.get_facecolor())

        except Exception as e:
            print('main loop', str(e))