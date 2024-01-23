from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)


activate_users.short_description = "Activate selected users"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "role",
        "is_active",
    ]
    actions = [activate_users]


admin.site.register(CustomUser, CustomUserAdmin)
