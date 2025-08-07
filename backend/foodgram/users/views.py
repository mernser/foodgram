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
