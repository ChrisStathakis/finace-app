from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response


class IsPublicOrCreatorPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.is_public and request.method == 'GET':
            return True
        return obj.user == request.user


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET' and obj.portfolio.is_public:
            return True
        return obj.portfolio.user == request.user


class UserTickerReadIfPublicOrCreatePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.portfolio.is_public and request.method == 'GET':
            return True
        return obj.portfolio.user == request.user
