import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from tickers.get_stock_data import read_data

tickers = ['AAPL', 'MSFT', '^GSPC']

data = pd.DataFrame()
my_year_month_fmt = mdates.DateFormatter('%m%y')
start_date = '2015-01-01'
end_date = '2016-12-31'

for ticker in tickers:
    df = read_data(ticker)
    data = df if data.empty else data.join(df, how='outer')

data['short_rolling'] = data['AAPL'].rolling(window=20).mean()
data['ema_short'] = data['AAPL'].ewm(span=20, adjust=False).mean()

print(data.tail())