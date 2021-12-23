from re import T
from rest_framework import serializers

from ..models import Ticker, Portfolio, UserTicker, Group


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['title', 'code', 'id']



class TickerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_tickers:ticker_update')
    analysis = serializers.HyperlinkedIdentityField(view_name='api_tickers:ticker_analysis')

    class Meta:
        model = Ticker
        fields = ['id', 'title', 'ticker', 'group', 'beta', 'coverage', 'market_variance', 'camp', 'price',
                  'simply_return', 'log_return', 'standard_deviation', 'sharp', 'url', 'analysis'
                  ]

    def create(self, validated_data):
        obj = Ticker.objects.create(**validated_data)
        obj.save()
        obj.update_ticker_data()
        
        return obj


class PortfolioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Portfolio
        fields = ['id', 'is_public', 'date_investment', 'is_locked', 'title', 'user', 'annual_returns',
                  'variance', 'starting_investment', 'current_value', 'maximum_cash', 'expected_portfolio_return',
                  'expected_portfolio_volatility', 'expected_portfolio_variance', 'get_difference', 'percent_difference',
                  
                  ]

    def check_user(self, request):
        return True if self.user == request.user else False


class UserTickerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_tickers:user_ticker_detail_view')
    update_url = serializers.HyperlinkedIdentityField(view_name='api_tickers:user_ticker_update_from_yahoo')

    class Meta:
        model = UserTicker
        fields = ['id', 'updated', 'date_buy', 'is_buy', 'is_sell', 'ticker', 'portfolio',
                  'starting_investment', 'current_value', 'qty', 'starting_value_of_ticker', 'current_value_of_ticker',
                  'weight', 'tag_ticker', 'tag_diff_percent', 'tag_diff', 'tag_code', 'url', 'update_url'
                  ]
        read_only_fields = ['tag_ticker', 'tag_diff_percent', 'tag_diff', 'tag_code' ]

    '''
    def create(self, validated_data):
        obj = UserTicker.objects.create(**validated_data)
        obj.save()
        obj.update_ticker_data() if obj else None
        return obj
    '''

    


class UserTickerUpdateFromApiSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_tickers:user_ticker_detail_view')

    class Meta:
        model = UserTicker
        fields = ['id', 'updated', 'date_buy', 'is_buy', 'is_sell', 'ticker', 'portfolio',
                  'starting_investment', 'current_value', 'qty', 'starting_value_of_ticker', 'current_value_of_ticker',
                  'weight', 'tag_ticker', 'tag_diff_percent', 'tag_diff', 'tag_code', 'url',
                  ]
        read_only_fields = ['tag_ticker', 'tag_diff_percent', 'tag_diff', 'tag_code' ]

    def update(self, instance, validated_data):
        instance.update_ticker_data()
        instance.refresh_from_db()
        
        return instance


class TickerAnalysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticker
        fields = ['calculate_averages', 'api_sma', 'create_data_for_chart']
        read_only_fields = ['calculate_averages', 'api_sma']

