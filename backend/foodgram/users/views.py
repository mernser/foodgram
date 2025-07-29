from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from .serializers import AvatarUpdateSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(detail=True,
            methods=('put',),
            permission_classes=(IsAuthenticated,),
            url_path='avatar')
    def avatar(self, request):
        serializer = AvatarUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
