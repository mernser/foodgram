from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (Tag, Ingredient,
                        Recipie,)
from users.serializers import UserProfileSerilizer, Base64ImageField
User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserProfileSerilizer(read_only=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipie
        fields = (
            'id', 'author', 'tags',
            'name', 'image', 'text', 'cooking_time',
        )
