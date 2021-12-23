from tickers.get_stock_data import get_stock_data, read_data

fb_ticker = 'FB'
# get_stock_data(fb_ticker)

fb = read_data(fb_ticker)


df = fb.loc['2020-01-01': '2020-12-31']
df['price1'] = df['FB'].shift(-1)
df['priceDiff'] = df['price1'] - df['FB']
df['Return'] = df['priceDiff']/df['FB']
df['Direction'] = [1 if df.loc[ei, 'priceDiff'] > 0 else -1 for ei in df.index]
df['Average3'] = (df[fb_ticker] + df[fb_ticker].shift(1) + df[fb_ticker].shift(2))/3
df['MA40'] = df[fb_ticker].rolling(40).mean()

df.dropna(inplace=True)
print(df)