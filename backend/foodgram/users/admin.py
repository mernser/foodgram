from django.contrib import admin
from .models import MyUser, Subscription


@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    list_editable = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'follower', 'subscribed_to')
    search_fields = ('follower', 'subscribed_to')
    list_filter = ('follower', 'subscribed_to')
    empty_value_display = '-'
