from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from .helpers import calculate_sum, calculate_avg

from .serializers import (TickerSerializer, PortfolioSerializer,
                          UserTickerSerializer, TickerAnalysisSerializer,
                          GroupSerializer, UserTickerUpdateFromApiSerializer
                          )
from ..models import Ticker, Portfolio, UserTicker, Group
from .permisions import IsPublicOrCreatorPermission, IsOwnerOrReadOnly, UserTickerReadIfPublicOrCreatePermission


@api_view(['GET'])
def ticker_homepage_api_view(request, format=None):
    return Response({
        'tickers': reverse('api_tickers:ticker_list', request=request, format=format),
        'portfolios': reverse('api_tickers:portfolio_list', request=request, format=format),
        'user_tickers': reverse('api_tickers:user_ticker_list_view', request=request, format=format),
        'group': reverse('api_tickers:group_list', request=request, format=format),
        'total_data_by_user': reverse('api_tickers:portfolio_total_data_by_user', request=request, format=format)
    })


class GroupListApiView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AllowAny, ]


class TickerListApiView(generics.ListCreateAPIView):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    permission_classes = [AllowAny, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['group']
    search_fields = ['title', 'ticker']



class TickerUpdateApiView(generics.RetrieveUpdateAPIView):
    queryset = Ticker.objects.all()
    serializer_class = TickerSerializer
    permission_classes = [AllowAny, ]


class TickerAnalysisApiView(generics.RetrieveAPIView):
    queryset = Ticker.objects.all()
    serializer_class = TickerAnalysisSerializer


class PortfolioListApiView(generics.ListCreateAPIView):
    # queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsPublicOrCreatorPermission, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'is_public']
    search_filters = ['title', ]

    def get_queryset(self):
        user = self.request.user
        user_qs = Portfolio.objects.filter(user=user) if user.is_authenticated else Portfolio.objects.none()
        public_qs = Portfolio.objects.filter(is_public=True)
        qs = user_qs|public_qs
        qs = Portfolio.filter_data(self.request, qs)

        return qs

    def filter_queryset(self, queryset):
        filter_backends = self.filter_backends

        # for backend in list(filter_backends):
        #  queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset


class PortfolioRetrieveUpdateDeleteApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsPublicOrCreatorPermission, ]


class UserTickerUpdateFromYahooApiView(generics.RetrieveUpdateAPIView):
    queryset = UserTicker.objects.all()
    serializer_class = UserTickerUpdateFromApiSerializer
    


class UserTickerListApiView(generics.ListCreateAPIView):
    queryset = UserTicker.objects.all()
    serializer_class = UserTickerSerializer
    permission_classes = [IsOwnerOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['portfolio', 'is_buy']
    search_filters = ['ticker', 'portfolio']


class UserTickerDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserTicker.objects.all()
    serializer_class = UserTickerSerializer
    permission_classes = [UserTickerReadIfPublicOrCreatePermission, ]


@api_view(['GET'])
def portfolio_total_data_view(request, format=None):
    user = request.user
    print('user', user)
    qs = Portfolio.objects.filter(user=user)
    active_qs = qs.filter(is_locked=False)
    total_money_investment = calculate_sum('starting_investment', qs)
    current_value = calculate_sum('current_value', qs)
    expected_portofolio_return = calculate_avg('expected_portfolio_return', qs)
    volatility = calculate_avg('expected_portfolio_volatility', qs)
    return Response({
        'starting_investment': total_money_investment,
        'current_value': current_value,
        'volatility': volatility,
        'return': expected_portofolio_return
    })


@api_view(['GET', ])
def portfolio_refresh_data_view(request, pk,format=None):
    instance = get_object_or_404(Portfolio, id=pk)
    if not request.user == instance.user:
        return Response({
            'message': 'You dont own this portfolio!'
        })
    for tick in instance.tickers.all():
        tick.update_basic_data()
    instance.save()
    instance.refresh_from_db()
    return Response({
        'message': 'Update with Success'
    })
