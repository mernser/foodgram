import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Subscription


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class UserProfileSerializer(UserSerializer):
    '''
    Выдача обычного объекта модели юзер
    '''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        return Subscription.objects.filter(
            follower=self.context.get('request').user,
            subscribed_to=obj
        ).exists()


class UserProfileListRecipesSerilizer(UserProfileSerializer):
    '''
    Выдача обычного объекта моедли юзер с ограничением на количестве рецептов
    Сделать наследование
    '''
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserProfileSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',
                  'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        from api.serializers import FavoriteRecipeSerializer
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (ValueError, TypeError):
                pass
        return FavoriteRecipeSerializer(recipes,
                                        many=True,
                                        context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            avatar_url = instance.avatar.url
            representation['avatar'] = (self
                                        .context['request']
                                        .build_absolute_uri(avatar_url))
        return representation
