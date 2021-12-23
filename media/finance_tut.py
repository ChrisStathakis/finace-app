import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


tickers = ['AAPL', 'MSFT', '^GSPC']
start_date = '2010-01-01'
end_date = '2016-12-31'

tickerData = yf.Ticker('MSFT')
panel_data = tickerData.history(period='1d', start=start_date, end=end_date)
panel_data.dropna(inplace=True)

close = panel_data['Close']
all_weekends = pd.date_range(start=start_date, end=end_date, freq='B')
close = close.reindex(all_weekends)
close = close.fillna(method='ffill')


