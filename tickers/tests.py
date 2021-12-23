from django.test import TestCase
import yfinance as yf
import pandas as pd
import os

from datetime import datetime


def check_if_file_exists(ticker):
    return False if not os.path.exists(f'media/stock_dfs/{ticker}.csv') else True
        

def get_stock_data(ticker, start='2010-1-1', end=datetime.today(), user=None):
    tickerData = yf.Ticker(ticker)
    
    df = tickerData.history(period='1d', start=start, end=end)
    print('df', df.head())
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    if not os.path.exists('media/stock_dfs'):
        os.makedirs('media/stock_dfs')
    df.to_csv('media/stock_dfs/{}.csv'.format(ticker))


def read_data(ticker, start_date=None, end_date=None, re_download=True):

    if start_date and end_date and re_download:
        get_stock_data(ticker, start=start_date, end=end_date)

    if not os.path.exists(f'media/stock_dfs/{ticker}.csv'):
        try:
            get_stock_data(ticker)
        except:
            return pd.DataFrame(columns=[])
    df = pd.read_csv(f'media/stock_dfs/{ticker}.csv', index_col='Date')
    print('read layer', df)
    if 'Stock Splits' in df.columns:
        df.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], 1, inplace=True)
    else:
        df.drop(['Open', 'High', 'Low', 'Volume'], 1, inplace=True)
    df.rename(columns={'Close': ticker}, inplace=True)
    return df




data = pd.DataFrame()
tickers = ['^GSPC', 'MSFT']
for ticker in tickers:
    df = read_data(ticker, re_download=True)
    print(ticker, df.head())
    data = df if data.empty else data.join(df, how='outer')

print(data.head())

'''
data = pd.DataFrame()
        instance = self.ticker
        tic = instance.ticker
        group = instance.group.code if instance.group else '^GSPC'
        tickers = [tic]

        for ticker in tickers:
            df = read_data(ticker, re_download=True)
            data = df if data.empty else data.join(df, how='outer')

        sec_returns = np.log(data / data.shift(1))
        cov = sec_returns.cov() * 250
        
        market_var = sec_returns[group].var() * 250
        PG_beta = cov_with_market / market_var
        PG_er = 0.025 + PG_beta * 0.05

        instance.beta = PG_beta
        instance.value = data[tic].iloc[-1]
        instance.current_value_of_ticker = data[tic].iloc[-1]
        instance.coverage = cov_with_market
        instance.camp = PG_er
        instance.market_variance = market_var
        try:
            cov_with_market = cov.iloc[0, 1]
        except:
            print('failed')
            
        instance.save()
'''