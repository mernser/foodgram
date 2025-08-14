from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (Tag, Ingredient,
                        Recipie, Favorite,
                        ShoppingCart)
from users.serializers import UserProfileSerializer, Base64ImageField
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
    author = UserProfileSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipie
        fields = (
            'id', 'tags', 'author',
            'name', 'image', 'text', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited',
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists():
            return True
        return False

    def get_is_favorited(self, obj):
        if Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists():
            return True
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipie
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
