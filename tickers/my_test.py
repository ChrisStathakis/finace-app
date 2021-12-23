import yfinance as yf
import pandas as pd

data = yf.download(['AMZN', ], start="2015-01-01", end="2020-02-21")

print('data', data)