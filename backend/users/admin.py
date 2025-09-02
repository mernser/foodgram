from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name',
        'last_name', 'recipes_count', 'subscribers_count'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('last_name', 'first_name')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count('recipes', distinct=True),
            subscribers_count=Count('authors', distinct=True)
        )

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes_count

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, obj):
        return obj.subscribers_count


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
