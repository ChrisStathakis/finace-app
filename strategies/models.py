from django.db import models
from django.contrib.auth import get_user_model

from tickers.models import Ticker
import datetime
from datetime import timedelta
import pandas as pd

from tickers.get_stock_data import read_data, get_stock_data


User = get_user_model()


class Strategy(models.Model):
    CHOICES = (
        ('a', 'Moving Average Trading Strategy'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=1, choices=CHOICES)

    class Meta:
        unique_together = ['user', 'category']


class StrategyTicker(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='my_tickers')
    # created_database = models.BooleanField(default=True)

    def __str__(self):
        return self.ticker.title

    def get_dataframe(self):
        twelve_months_ago = datetime.datetime.now() - timedelta(days=360)
        return read_data(ticker=self.ticker.ticker,
                         start_date=twelve_months_ago,
                         end_date=datetime.datetime.now().date(),
                         re_download=False
                        )

    def EMA(self, average_length=50):
        data = self.get_dataframe()
        ret = data.ewm(span=average_length, adjust=False).mean()
        return ret

    def MACD(self, a=12, b=26, c=9):
        MACD_line = self.EMA(a) - self.EMA(b)
        signal_line = MACD_line.ewm(span=c, adjust=False).mean()
        histogram = MACD_line - signal_line
       # MACD_line = [MACD_line.columns.tolist() + MACD_line.reset_index().values.tolist()]
        # signal_line = [signal_line.columns.tolist() + signal_line.reset_index().values.tolist()]
        return MACD_line, signal_line, histogram

    def generate_signal(self, closing_prices):
        ticker = self.ticker.ticker
        buy = pd.DataFrame(index=closing_prices.index, columns=['Buy'])  # an empty data-frame to store buy signals
        sell = pd.DataFrame(index=closing_prices.index, columns=['Sell'])  # an empty data-frame to store sell signals
        MACD_line, signal_line, histogram = self.MACD()
        cooldown = 0
        COOLDOWN_PERIOD = 30
        high = ''
        for i in range(1, len(closing_prices)):
            try:
                cooldown -= 1
                if i == 1:
                    if MACD_line[ticker].iloc[i] > signal_line[ticker].iloc[i]:
                        high = 'MACD'
                    else:
                        high = 'SIGNAL'
                elif MACD_line[ticker].iloc[i] > signal_line[ticker].iloc[i]:
                    if high == 'SIGNAL':  # MACD crossed signal - bottom to top BUY
                        if MACD_line[ticker].iloc[i] < 0 and cooldown <= 0:
                            buy.iloc[i] = closing_prices[i]  # BUY
                            cooldown = COOLDOWN_PERIOD
                        high = 'MACD'
                elif MACD_line[ticker].iloc[i] < signal_line[ticker].iloc[i]:
                    if high == 'MACD':  # MACD crossed signal - top to bottom SELL
                        if MACD_line[ticker].iloc[i] > 0:
                            sell.iloc[i] = closing_prices[i]  # SELL
                        high = 'SIGNAL'
            except:
                continue

    @staticmethod
    def calculate_historic_rsi(tickers):
        Compare_Tickers = pd.DataFrame(columns=["Company", "Days Observed", "Crosses", "True_Positive",
                                                "False_Negative", "Sensitivity", "Specificity", "Accuracy",
                                                "TPR", "FPR"
                                                ]
                                       )

        for stock in tickers:
            print('loop starting')
            df = read_data(stock, start_date='2000-01-01', end_date=datetime.datetime.now(), re_download=False)
            df[stock] = df.loc[(df[stock] > 2)]
            upPrices, downPrices, i = [], [], 0
            print('database ready', df.count())
            while i < len(df.count()):
                print('start counting', i)
                if i == 0:
                    upPrices.append(0)
                    downPrices.append(0)
                else:
                    diff = df[stock][i]-df[stock][i-1]
                    print('diff', diff)
                    if diff > 0:
                        upPrices.append(diff)
                        downPrices.append(0)
                    else:
                        downPrices.append(diff)
                        upPrices.append(0)
                i+=1

            x, avg_gain, avg_loss = 0, [], []

            print('first step')
            while x < len(df.count()):
                if x < 15:
                    avg_gain.append(0)
                    avg_loss.append(0)
                else:
                    sumGain, sumLoss = 0, 0
                    y = x-14
                    while y <= x:
                        sumGain += upPrices[y]
                        sumLoss += downPrices[y]
                        y += 1
                    avg_gain.append(sumGain/14)
                    avg_loss.append(sumLoss/14)
                x += 1
            print('second step')
            p, RS, RSI = 0, [], []
            while p < len(df.count()):
                if p < 15:
                    RS.append(0)
                    RSI.append(0)
                else:
                    RsValue = (avg_gain[p]/avg_loss[p])
                    RS.append(RsValue)
                    RSI.append(100-(100/(1+RsValue)))
                p += 1
            print('third step')
            df_dict = {
                'Prices': df[stock],
                'upPrices': upPrices,
                'downPrices': downPrices,
                'AvgGain': avg_gain,
                'AvgLoss': avg_loss,
                'RS': RS,
                'RSI': RSI
            }

            Days_Observed = 15
            Crosses = 0
            nothing = 0
            True_Positive = 0
            False_Positive = 0
            True_Negative = 0
            False_Negative = 0
            Sensitivity = 0
            Specificity = 0
            Accurancy = 0
            while Days_Observed < len(df.count())-5:
                if RSI[Days_Observed] <= 30:
                    if ((df[stock][Days_Observed+1] + df[stock][Days_Observed+2] + df[stock][Days_Observed+3] + df[stock][Days_Observed+4] + df[stock][Days_Observed+5])/5 >df[stock][Days_Observed]):
                        True_Negative +=1
                    else:
                        False_Positive +=1
                    Crosses +=1
                else:
                    nothing +=1
                Days_Observed +=1

            try:
                Sensitivity = (True_Positive/(True_Positive + False_Negative))
            except ZeroDivisionError:
                Sensitivity = 0

            try:
                Specificity = (True_Negative/(True_Negative + False_Negative))
            except ZeroDivisionError:
                Specificity = 0

            try:
                Accuracy = (True_Negative + True_Positive) / (True_Negative + True_Positive + False_Positive)
            except ZeroDivisionError:
                Accuracy = 0

            TPR = Sensitivity
            FPR = 1- Specificity

            add_row = {'Company': stock, 'Days_Observed': Days_Observed, 'Crosses': Crosses, 'True_Positive' : True_Positive, 'False_Positive' : False_Positive,
                       'True_Negative': True_Negative, 'False_Negative' : False_Negative, 'Sensitivity' : Sensitivity, 'Specificity' : Specificity, 'Accuracy' : Accuracy, 'TPR' : TPR, 'FPR' : FPR}











