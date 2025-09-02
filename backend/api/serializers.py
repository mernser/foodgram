from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.constants import (ERROR_ALREADY_FAVORITED,
                                ERROR_ALREADY_IN_SHOPPINGCART,
                                ERROR_ALREADY_SUBSCRIBED,
                                ERROR_DUBLICATE_INGREDIENT,
                                ERROR_DUBLICATE_TAG, ERROR_EMPTY_INGREDIENT,
                                ERROR_EMPTY_TAG, ERROR_NO_IMAGE,
                                ERROR_NO_INGREDIENT, ERROR_NO_TAG,
                                ERROR_SELF_SUBSCRIPTION, MAX_INGREDIENT_AMOUNT,
                                MIN_INGREDIENT_AMOUNT)
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipie,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class ImageField(Base64ImageField):
    def to_internal_value(self, data):
        if data == "":
            raise serializers.ValidationError(ERROR_NO_IMAGE)
        return super().to_internal_value(data)


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class UserProfileSerializer(UserSerializer):
    '''
    Выдача обычного объекта модели юзер.
    '''

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.follower.filter(subscribed_to=obj).exists()
        )


class UserProfileListRecipesSerilizer(UserProfileSerializer):
    '''
    Выдача обычного объекта моедли юзер с ограничением на количестве рецептов.
    '''

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = (
            self.context
            .get('request')
            .query_params.get('recipes_limit')
        )
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (ValueError, TypeError):
                pass
        return FavoriteRecipeSerializer(recipes,
                                        many=True,
                                        context=self.context).data


class AvatarUpdateSerializer(serializers.ModelSerializer):
    avatar = ImageField(required=True)

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
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = ImageField(required=True)
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
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_list.filter(recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.favorite_recipes.filter(recipe=obj).exists()
        )


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
        if len(value) != len(set(value)):
            raise serializers.ValidationError(ERROR_DUBLICATE_TAG)
        return value

    @staticmethod
    def create_recipe_ingredients(recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipie.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        instance.save()
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self.create_recipe_ingredients(instance, ingredients)
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


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('subscribed_to',)

    def to_representation(self, instance):
        subscribed_user = User.objects.filter(
            id=instance.subscribed_to.id
        ).annotate(recipes_count=Count('recipes')).first()

        return UserProfileListRecipesSerilizer(
            subscribed_user,
            context=self.context
        ).data

    def validate(self, data):
        subscribed_to = data['subscribed_to']
        follower = self.context['request'].user
        if Subscription.objects.filter(
            follower=follower,
            subscribed_to=subscribed_to
        ).exists():
            raise serializers.ValidationError(ERROR_ALREADY_SUBSCRIBED)
        if follower == subscribed_to:
            raise serializers.ValidationError(ERROR_SELF_SUBSCRIPTION)
        return data


class BaseCreateRelationSerializer(serializers.ModelSerializer):
    error_message = None

    class Meta:
        fields = ('user', 'recipe')

    def validate(self, data):
        if self.Meta.model.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise serializers.ValidationError(self.error_message)
        return data

    def to_representation(self, instance):
        return FavoriteRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteCreateSerializer(BaseCreateRelationSerializer):
    error_message = ERROR_ALREADY_FAVORITED
    representation_serializer = FavoriteRecipeSerializer

    class Meta(BaseCreateRelationSerializer.Meta):
        model = Favorite


class ShoppingCartCreateSerializer(BaseCreateRelationSerializer):
    error_message = ERROR_ALREADY_IN_SHOPPINGCART
    representation_serializer = FavoriteRecipeSerializer

    class Meta(BaseCreateRelationSerializer.Meta):
        model = ShoppingCart
