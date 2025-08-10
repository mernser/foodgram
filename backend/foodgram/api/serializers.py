from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (Tag, Ingredient,
                        Recipie, Favorite)
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
    image = Base64ImageField(required=False)
    author = UserProfileSerilizer(read_only=True)

    class Meta:
        model = Recipie
        fields = (
            'id', 'tags', 'author',
            'name', 'image', 'text', 'cooking_time',
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipie
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
