import yfinance as yf
import pandas as pd
import os

from datetime import datetime
import datetime as dat


def check_if_file_exists(ticker):
    return False if not os.path.exists(f'media/stock_dfs/{ticker}.csv') else True
        

def get_stock_data(ticker, start='2010-1-1', end=datetime.today(), user=None):
    tickerData = yf.Ticker(ticker)
    if user:
        print('user check')
        settings = user.settings
        qs = settings.date_ranges.filter(is_primary=True)
        date_range = qs.first() if qs.exists() else None
        if date_range:
            df = tickerData.history(period='1d', start=date_range.start, end=date_range.end)
        else:
           df = tickerData.history(period='1d', start=start, end=end)
    else:
        df = tickerData.history(period='1d', start=start, end=end)
        print('hello')
    print('passed user')
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    if not os.path.exists('media/stock_dfs'):
        os.makedirs('media/stock_dfs')
    df.to_csv('media/stock_dfs/{}.csv'.format(ticker))


def read_data(ticker, start_date='2010-1-1', end_date=datetime.today(), re_download=True):

    if re_download:
        print('download data', ticker)
        get_stock_data(ticker, start=start_date, end=end_date)

    if not os.path.exists(f'media/stock_dfs/{ticker}.csv'):
        try:
            print('didnt find path', ticker)
            get_stock_data(ticker)
        except:
            return pd.DataFrame(columns=[])
    df = pd.read_csv(f'media/stock_dfs/{ticker}.csv', index_col='Date')
    print('df', ticker, df)
    if 'Stock Splits' in df.columns:
        df.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], 1, inplace=True)
    else:
        df.drop(['Open', 'High', 'Low', 'Volume'], 1, inplace=True)
    df.rename(columns={'Close': ticker}, inplace=True)
    return df


def read_data_not_rename(ticker):
    df = pd.read_csv(f'media/stock_dfs/{ticker}.csv', index_col='Date')
    df.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'], 1, inplace=True)

    return df