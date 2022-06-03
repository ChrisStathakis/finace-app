from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages

from decimal import Decimal
import numpy as np
import pandas as pd

from scipy.stats import norm
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from .get_stock_data import read_data, get_stock_data


from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

from io import StringIO
import time

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class Ticker(models.Model):
    updated = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=200, null=True)
    ticker = models.CharField(max_length=200, null=True)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL)
    beta = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True)
    coverage = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    market_variance = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    camp = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)

    simply_return = models.DecimalField(max_digits=30, decimal_places=8, default=0, help_text='Simply Rate of Return')
    log_return = models.DecimalField(max_digits=30, decimal_places=8, default=0, help_text='Log Return')
    standard_deviation = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    sharp = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.update_ticker_data()
        super(Ticker, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:ticker_update', kwargs={'pk': self.id})

    def calculate_averages(self):
        # returns rolling averages 3, 7 and 30 days
        df = read_data(self.ticker, re_download=False)
        df['three_days_avg'] = df[self.ticker].rolling(3).mean()
        df['seven_days_avg'] = df[self.ticker].rolling(7).mean()
        df['thirty_days_avg'] = df[self.ticker].rolling(30).mean()
        return [df.iloc[-1]['three_days_avg'], df.iloc[-1]['seven_days_avg'], df.iloc[-1]['thirty_days_avg']]

    def create_data_for_chart(self):
        # returns rolling averages 3, 7 and 30 days
        df = read_data(self.ticker, re_download=False)
        df['MA3'] = df[self.ticker].rolling(3).mean()
        df['MA10'] = df[self.ticker].rolling(10).mean()
        df['MA50'] = df[self.ticker].rolling(50).mean()

        df.dropna(inplace=True)

        # df['Close1'] = df[self.ticker].shift(-1)
        # df['Profit'] = [df.loc[ei, 'Close1'] - df.loc[ei, {self.ticker}] for ei in df.index]

        # df['wealth'] = df['Profit'].cumsum()
        df = df.tail(50)
        return df

    def get_delete_url(self):
        return reverse('portfolio:ticker_delete_view', kwargs={'id': self.id})

    def download_and_read_ticker_data(self, df,  download_data=True, start='2000-01-01', end=datetime.now().date()):
        if download_data:
            get_stock_data(self.ticker, start=start, end=end)
        data = read_data(self.ticker)
        df = data if df.empty else df.join(data, how='outer')
        return df

    @staticmethod
    def filter_data(request):
        q = request.GET.get('q', None)
        qs = Ticker.objects.filter(title__icontains=q) if q else Ticker.objects.all()
        return qs

    def sma(self, periods=12):
        # returns simply moving average (dataframe)
        df = read_data(self.ticker, re_download=False)
        sma = df.rolling(window=periods).mean()
        df['sma'] = df.rolling(window=periods).mean()
        df.dropna()
        return df

    def api_sma(self):
        df_sma = self.bb()
        df_sma.dropna(inplace=True)
        return [df_sma.columns.tolist()] + df_sma.reset_index().values.tolist()

    def moving_average_trading_strategy(self, window=20, start_date='2020-01-01', end_date=datetime.now().date()):
        # returns pandas dataframe enchanced with shorting roll and ema (exponetial moving average)
        df = read_data(self.ticker, start_date, end_date, re_download=False)
        shorting_roll = f'shorting_roll_{self.ticker}'
        ema_short = f'ema_short_{self.ticker}'
        df[shorting_roll] = df[self.ticker].rolling(window=window).mean()
        df[ema_short] = df[self.ticker].ewm(span=window, adjust=False).mean()
        df.dropna(inplace=True)
        return df

    def bb(self, sma_periods=12, periods=2):
        df = read_data(self.ticker, re_download=False)
        df['sma'] = df[self.ticker].rolling(sma_periods).mean()
        df['sma2'] = df[self.ticker].rolling(periods).mean()

        df['std'] = df['sma2'].std()
        df.dropna()
        df['upper_bb'] = df['sma'] + (df['std'] * 2)
        df['lower_bb'] = df['sma'] - (df['std'] * 2)

        return df

    def calculate_macd(self):
        df = read_data(self.ticker, re_download=False)
        ticker = df[self.ticker]
        exp1 = ticker.ewm(span=12, adjust=False).mean()
        exp2 = ticker.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        exp3 = macd.ewm(span=9, adjust=False).mean()
        ticker = [df.columns.tolist()] + df.reset_index().values.tolist()

        return [macd, exp3, ticker]

    def implement_bb_strategy(self):
        data = read_data(self.ticker)

    def calculate_probability_of_drop(self, percent=0.05):
        # you choose the percent a ticker will drop, and calculates the probabillity
        ms = read_data(ticker=self.ticker, re_download=False)
        ms['LogReturn'] = np.log(ms[self.ticker]).shift(-1) - np.log(ms[self.ticker])
        mu = ms['LogReturn'].mean()
        sigma = ms['LogReturn'].std(ddof=1)
        prob_return1 = norm.cdf(-percent, mu, sigma)
        return prob_return1

    @staticmethod
    def show_graph(df, size=(9, 3)):
        fig = plt.figure(figsize=size)
        plt.plot(df)
        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()
        return data

    def monte_carlo_simulation(self):
        rev_m = 170
        rev_stdev = 20
        iterations = 1000
        rev = np.random.normal(rev_m, rev_stdev, iterations)
        fig = plt.figure(figsize=(9, 3))
        plt.plot(rev)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        data = imgdata.getvalue()

        COGS = - (rev * np.random.normal(0.6, 0.1))
        COGS.mean()
        COGS.std()
        Gross_profit = rev + COGS

        return data

    def get_ticker_data(self):
        try:
            data = read_data(self.ticker)
        except:
            data = pd.DataFrame()
        return data

    def forecast(self, days=7):
        try:
            df = read_data(self.ticker)
            df['prediction'] = df[self.ticker].shift(-1)
            df.dropna(inplace=True)
            forecast_time = int(days)
            X = np.array(df.drop(['prediction'], 1))
            Y = np.array(df['prediction'])
            X = preprocessing.scale(X)
            X_prediction = X[-forecast_time:]
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.5)
            clf = LinearRegression()
            clf.fit(X_train, Y_train)
            prediction = (clf.predict(X_prediction))
            predict_days = []
            for ele in range(days):
                predict_days.append([(datetime.today() + timedelta(days=ele+1)).date(), prediction[ele]])
        except:
            predict_days = []

        return predict_days

    def forecasting_stock_prices(self, update_data=False):

        if update_data:
            get_stock_data(self.ticker)
        df = read_data(self.ticker)
        data = df
        log_returns = np.log(1+data.pct_change())
        u = log_returns.mean()
        var = log_returns.var()
        drift = u - (0.5*var)

        stdev = log_returns.std()

        x = np.random.rand(10, 2)
        norm.ppf(x)
        Z = norm.ppf(np.random.rand(10, 2))
        t_intervals = 1000
        iterations = 10
        daily_returns = np.exp(drift.values + stdev.values * norm.ppf(np.random.rand(t_intervals, iterations)))
        S0 = data.iloc[-1]
        price_list = np.zeros_like(daily_returns)
        price_list[0] = S0
        for t in range(1, t_intervals):
            price_list[t] = price_list[t-1]*daily_returns[t]

    def update_ticker_data(self, request=None, re_download=True):
        group = self.group.code if self.group else '^GSPC'
        tic = self.ticker
        tickers = [self.ticker, group]
        data = pd.DataFrame()
        for ticker in tickers:
            df = read_data(ticker, re_download=re_download)
            data = df if data.empty else data.join(df, how='outer')

        try:
            data['log_return'] = np.log(data[tic] / data[tic].shift(1))
        except:
            messages.warning(request, f'No data for ticker {ticker}')
            return None
        log_return = (data['log_return'].mean() * 250) * 100
        self.log_return = log_return
        data['simply_return'] = (data[tic] / data[tic].shift(1)) - 1
        simply_return = (data['simply_return'].mean() * 250) * 100

        sec_returns = np.log(data / data.shift(1))
        standard_deviation = sec_returns[tic].std() * 250 ** 0.5
        cov = sec_returns.cov() * 250
        cov_with_market = cov.iloc[0, 1]
        market_var = sec_returns[group].var() * 250
        PG_beta = cov_with_market / market_var
        PG_er = 0.025 + PG_beta * 0.05
        Sharpe = (PG_er - 0.025) / (sec_returns[tic].std() * 250 ** 0.5)

        self.beta = round(float(PG_beta), 4) if isinstance(PG_beta, float) else 0
        self.simply_return = round(float(simply_return), 4) if isinstance(simply_return, float) else 0
        price = round(float(data[tic].iloc[-1]), 8) if isinstance(data[tic].iloc[-1], float) else 0
        if np.isnan(price):
            self.price = 0
            price = 0
        else:
            self.price = 0 if isinstance(price, str) else price
        
        self.coverage = round(float(cov_with_market), 4) if isinstance(cov_with_market, float) else 0
        self.camp = round(float(PG_er), 4) if isinstance(PG_er, float) else 0
        self.market_variance = round(float(market_var), 4) if isinstance(market_var, float) else 0
        self.standard_deviation = round(standard_deviation, 4) if isinstance(standard_deviation, float) else 0
        self.sharp = round(standard_deviation, 4) if isinstance(Sharpe, float) else 0
        self.updated = datetime.now()
        time.sleep(2)


class Portfolio(models.Model):
    is_public = models.BooleanField(default=False)
    date_investment = models.DateField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    annual_returns = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    variance = models.DecimalField(max_digits=200, decimal_places=150, default=0)
    starting_investment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    maximum_cash = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    expected_portfolio_return = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    expected_portfolio_volatility = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    expected_portfolio_variance = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        qs = self.tickers.all()

        inve = qs.aggregate(Sum('starting_investment'))['starting_investment__sum'] if qs.exists() else 0
        self.starting_investment = inve

        self.current_value = qs.aggregate(Sum('current_value'))[
            'current_value__sum'] if qs.exists() else 0

        
        self.expected_portfolio_return, self.expected_portfolio_variance, self.expected_portfolio_volatility = \
            self.calculate_returns_and_volatility()
      

        super(Portfolio, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('portfolio:portofolio_detail', kwargs={'id':self.id})

    def remaining_capital(self):
        return self.maximum_cash - self.starting_investment

    def remaining_percent(self):
        return self.remaining_capital()/self.maximum_cash * 100 if self.maximum_cash !=0 else 0

    def get_difference(self):
        return [self.current_value - self.starting_investment,
                True if self.current_value - self.starting_investment >=0 else False
                ]

    def earnings(self):
        return self.current_value - self.starting_investment

    def percent_difference(self):
        if self.starting_investment != 0:
            p = (self.current_value - self.starting_investment)/self.starting_investment
            return round(p, 2)
        return 0

    def calculate_coveriance(self):
        pass

    def effecient_frontier(self):
        assets = []
        tickers = [ticker.ticker for ticker in self.tickers.filter(is_buy=False, is_sell=False)]
        for tic in tickers:
            assets.append(tic.ticker)

        df_data = pd.DataFrame()
        for a in assets:
            # get_stock_data(a)
            df = read_data(a)
            df_data = df if df_data.empty else df_data.join(df, how='outer')

        log_returns = np.log(df_data/df_data.shift(1))
        mean = log_returns.mean() * 250
        cov = log_returns.cov()
        corr = log_returns.corr()

        num_assets = len(assets)
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        expected_portofolio_return = np.sum(weights*log_returns.mean()) * 250
        expected_portfolio_variance = np.dot(weights.T, np.dot(log_returns.cov()*250, weights))
        expected_portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov()* 250, weights)))

        pfolio_returns = []
        pfolio_volatilies = []
        total_weights = []
        total_money = []
        for x in range(1, 1000):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            pfolio_returns.append(np.sum(weights*log_returns.mean()) * 250)
            pfolio_volatilies.append(np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 250, weights))))
            total_weights.append(weights)

            current_money = []
            for weight in weights:
                current_money.append(round(float(self.starting_investment) * float(round(weight, 4)), 2))
            total_money.append(current_money)

        pfolio_returns = np.array(pfolio_returns)
        pfolio_volatilies = np.array(pfolio_volatilies)
        return [total_weights, pfolio_volatilies, pfolio_returns, total_money]

    def capm(self):
        pass

    def add_tickers_to_portfolio(self, request):
        money = request.GET.get('money')
        money_list = money.split(',')
        for ele in money_list:
            ele = ele.replace(' ', '')
            ele = ele.replace('[', '')
            ele = ele.replace(']', '')

    def calculate_returns_and_volatility(self):
        try:
            assets, weights = [], []
            tickers = [ticker.ticker for ticker in self.tickers.all()]
            for tic in self.tickers.all():
                new_weight = tic.starting_investment/self.starting_investment if self.starting_investment != 0 else 1/self.tickers.count()
                weights.append(float(new_weight))
            weights = np.array(weights)

            for tic in tickers:
                assets.append(tic.ticker)

            df_data = pd.DataFrame()
            for a in assets:
                # get_stock_data(a)
                df = read_data(a)
                df_data = df if df_data.empty else df_data.join(df, how='outer')

            log_returns = np.log(df_data / df_data.shift(1))
            mean = log_returns.mean()# *250
            # cov = log_returns.cov()
            # corr = log_returns.corr()
        except:
            print('worng')

        '''
        num_assets = len(assets)
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        '''
        try:
            expected_portofolio_return = Decimal(np.sum(weights * mean)) * 250
            expected_portofolio_return = expected_portofolio_return if expected_portofolio_return else 0
            expected_portfolio_variance = np.dot(weights.T, np.dot(log_returns.cov() * 250, weights))
            expected_portfolio_variance = expected_portfolio_variance if expected_portfolio_variance else 0
            expected_portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 250, weights)))
            expected_portfolio_volatility = expected_portfolio_volatility if expected_portfolio_volatility else 0
            print('expected', expected_portofolio_return, expected_portfolio_variance, expected_portfolio_volatility)
        except Exception as e:

            return [0, 0, 0]

        return [expected_portofolio_return, expected_portfolio_variance, expected_portfolio_volatility]

    @staticmethod
    def filter_data(request, qs):
        user = request.GET.get('user', None)
        is_public = request.GET.get('is_public', None)
        qs = qs.filter(user__id=user) if user else qs
        qs = qs.filter(is_public=is_public) if is_public else qs

        return qs


class UserTicker(models.Model):
    updated = models.DateTimeField(blank=True, null=True)
    date_buy = models.DateTimeField(blank=True, null=True)
    is_buy = models.BooleanField(default=False)
    is_sell = models.BooleanField(default=False)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, null=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, related_name='tickers')

    starting_investment = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    current_value = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    qty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    starting_value_of_ticker = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    current_value_of_ticker = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    weight = models.DecimalField(max_digits=30, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.qty = Decimal(self.starting_investment)/Decimal(self.starting_value_of_ticker) if self.starting_value_of_ticker != 0 else 0

        if self.starting_investment != 0:
            starting_value = Decimal(self.starting_investment)
            ticker_current_value = Decimal(self.current_value_of_ticker)
            ticker_starting_value = Decimal(self.starting_value_of_ticker)
            self.current_value = ((ticker_current_value/ticker_starting_value)*starting_value) if ticker_starting_value !=0 else 0
        if self.starting_investment > 0:
            self.is_buy = True

        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticker.title if self.ticker else 'delete'

    def update_data_on_buy(self):
        self.update_ticker_data()
        if self.historic_ticker:
            self.historic_ticker.delete()
        self.date_buy = datetime.now()
        self.starting_value_of_ticker = self.current_value_of_ticker
        self.save()

    def get_delete_url(self):
        return reverse('portfolio:delete_ticker_from_portfolio', kwargs={'pk': self.id})

    def get_edit_url(self):
        return reverse('portfolio:update_user_ticker', kwargs={'pk': self.id})

    def diff(self):
        return self.current_value - self.starting_investment

    def diff_percent_ticker_price(self):
        if self.starting_value_of_ticker !=0:
            p = (self.current_value_of_ticker-self.starting_value_of_ticker)/self.starting_value_of_ticker
            return round(p, 8) * 100
        return 0

    def update_ticker_data(self):

        data = pd.DataFrame()
        instance = self.ticker
        tic = instance.ticker
        group = instance.group.code if instance.group else '^GSPC'
        tickers = [tic, group]

        for ticker in tickers:
            df = read_data(ticker, re_download=True)
            data = df if data.empty else data.join(df, how='outer')

        sec_returns = np.log(data / data.shift(1))
        cov = sec_returns.cov() * 250
        cov_with_market = cov.iloc[0, 1]
        market_var = sec_returns[group].var() * 250
        PG_beta = cov_with_market / market_var
        PG_er = 0.025 + PG_beta * 0.05

        instance.beta = PG_beta
        instance.value = data[tic].iloc[-1]
        instance.current_value_of_ticker = data[tic].iloc[-1]
        instance.coverage = cov_with_market
        instance.camp = PG_er
        instance.market_variance = market_var
        instance.save()

        self.current_value_of_ticker = data[tic].iloc[-1]
        if self.starting_value_of_ticker <= 0.1:
            self.starting_value_of_ticker = data[tic].iloc[-1]
        self.updated = datetime.now()
        self.save()

    def update_basic_data(self):
        # this fuction is only for the api, so the response don't get too long
       
        instance = self.ticker
        tic = instance.ticker
        data = read_data(tic, re_download=True)

        instance.value = data[tic].iloc[-1]
        instance.save()
        self.current_value_of_ticker = data[tic].iloc[-1]

        self.current_value_of_ticker = data[tic].iloc[-1]
        if self.starting_value_of_ticker <= 0.1:
            self.starting_value_of_ticker = data[tic].iloc[-1]
        self.updated = datetime.now()
        self.save()

    def tag_ticker(self):
        return self.ticker.title if self.ticker else 'Something is wrong'
    
    def tag_code(self):
        return self.ticker.ticker if self.ticker else 'Something is wrong'

    def tag_diff_percent(self):
        return round((self.current_value_of_ticker - self.starting_value_of_ticker)/ self.starting_value_of_ticker if self.starting_value_of_ticker != 0 else 0, 3)

    def tag_diff(self):
        return round(Decimal(self.starting_investment) * Decimal(self.tag_diff_percent()), 2)

    def update_ticker_and_update_user_ticker(self):
        ticker = self.ticker
        ticker.update_ticker_data()
        

class HistoricTicker(models.Model):
    ticker = models.OneToOneField(UserTicker, on_delete=models.CASCADE, related_name='historic_ticker')
    timestamp = models.DateField(auto_now_add=True)
    beta = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True)
    coverage = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    market_variance = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    camp = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=30, decimal_places=8, blank=True, null=True, default=0)

    simply_return = models.DecimalField(max_digits=30, decimal_places=8, default=0, help_text='Simply Rate of Return')
    log_return = models.DecimalField(max_digits=30, decimal_places=8, default=0, help_text='Log Return')
    standard_deviation = models.DecimalField(max_digits=30, decimal_places=8, default=0)

    def __str__(self):
        return f'Historic data of {self.ticker}'

