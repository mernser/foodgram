from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from .serializers import (AvatarUpdateSerializer, UserProfileSerializer,
                          UserProfileListRecipesSerilizer)
from .models import Subscription
from .pagination import SubscriptionsPageNumberPagination
from foodgram.constants import (ERROR_ALREADY_SUBSCRIBED,
                                ERROR_SELF_SUBSCIRPTION,)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(detail=True,
            methods=('delete',),
            permission_classes=(IsAuthenticated,),
            url_path='avatar')
    def avatar_delete(self, request):
        user_avatar = request.user.avatar
        if user_avatar:
            user_avatar.delete()
            user_avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True,
            methods=('put',),
            permission_classes=(IsAuthenticated,),
            url_path='avatar')
    def avatar_update(self, request):
        serializer = AvatarUpdateSerializer(
            request.user,
            data=request.data,
            partial=False,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomSubscriptionViewSet(UserViewSet):
    pagination_class = SubscriptionsPageNumberPagination

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,),
            url_path='users/subscriptions')
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscribed_to__follower=request.user
        )
        recipes_limit = request.query_params.get('recipes_limit', None)
        page = self.paginate_queryset(subscriptions)
        serializer = UserProfileListRecipesSerilizer(
            page,
            many=True,
            context={'request': request,
                     'recipes_limit': recipes_limit, }
        )
        return self.get_paginated_response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = SubscriptionsPageNumberPagination

    def create(self, request, *args, **kwargs):
        recipes_limit = request.query_params.get('recipes_limit', None)
        user_to_subscribe = get_object_or_404(User, pk=kwargs.get('pk'))
        if Subscription.objects.filter(
                follower=request.user,
                subscribed_to=user_to_subscribe
        ).exists():
            return Response(
                {'detail': ERROR_ALREADY_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_to_subscribe == request.user:
            return Response(
                {'detail': ERROR_SELF_SUBSCIRPTION},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(follower=request.user,
                                    subscribed_to=user_to_subscribe)
        serializer = UserProfileListRecipesSerilizer(
            user_to_subscribe,
            context={'request': request,
                     'recipes_limit': recipes_limit}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_to_unsurbscribe = get_object_or_404(User, pk=kwargs.get('pk'))
        record = get_object_or_404(
            Subscription,
            follower=request.user,
            subscribed_to=user_to_unsurbscribe)
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
