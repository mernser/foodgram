from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (Favorite, Ingredient, RecipeIngredient,
                        Recipie, ShoppingCart, Tag)
from foodgram.constants import (ERROR_DUBLICATE_INGREDIENT,
                                ERROR_DUBLICATE_TAG, ERROR_EMPTY_INGREDIENT,
                                ERROR_EMPTY_TAG, ERROR_NO_INGREDIENT,
                                ERROR_NO_TAG)
from users.serializers import Base64ImageField, UserProfileSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    author = UserProfileSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients'
    )

    class Meta:
        model = Recipie
        fields = (
            'id', 'tags', 'author',
            'name', 'image', 'text', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited',
            'ingredients',
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if self.context['request'].user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if self.context['request'].user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    ingredients = CreateRecipeIngredientSerializer(many=True, required=True)

    class Meta(RecipeSerializer.Meta):
        fields = (
            'tags', 'ingredients',
            'name', 'text', 'image', 'cooking_time',
        )

    def validate(self, data):
        if self.context['request'].method == 'PATCH':
            if 'tags' not in data:
                raise serializers.ValidationError(ERROR_NO_TAG)
            if 'ingredients' not in data:
                raise serializers.ValidationError(ERROR_NO_INGREDIENT)
        return data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(ERROR_EMPTY_INGREDIENT)
        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(ERROR_DUBLICATE_INGREDIENT)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(ERROR_EMPTY_TAG)
        tags_ids = [item.id for item in value]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(ERROR_DUBLICATE_TAG)
        return value

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipie.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipie
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class ShortLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipie
        fields = ('short_link',)

    def get_short_link(self, obj):
        if obj.short_link:
            return self.context['request'].build_absolute_uri(obj.short_link)
        return None
