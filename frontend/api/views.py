from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def homepage_api_view(request, format=None):
    return Response({
        'tickers': reverse('api_tickers:home', request=request, format=format),
        'login':  reverse('token_obtain_pair', request=request, format=format),
        'refreshToken': reverse('token_refresh', request=request, format=format),
        
    }) 