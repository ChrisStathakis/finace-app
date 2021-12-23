from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import ProfileSerializer, UserSerializer
from ..models import Profile



class CurrentUser(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)