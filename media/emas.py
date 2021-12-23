import pandas as pd
from matplotlib import pyplot
import os


class MovingAverage():

    def __init__(self, closing_price):
        self.data = pd.DataFrame()

    def EMA(self, average_length=50):
        ret = self.data.ewm(
            span=average_length,
            adjust=False
        ).mean()
        return ret.rename(columns={'Close': 'EMA'})