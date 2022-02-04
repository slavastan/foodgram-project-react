from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username',)
    empty_value_display = ('-empty-')
    search_fields = ('username',)
    list_filter = ('email', 'username')
