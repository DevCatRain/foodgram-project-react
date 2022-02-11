from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'first_name',
                    'last_name')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
