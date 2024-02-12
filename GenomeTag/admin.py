from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, RoleChangeRequest


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


def approve_role_change(modeladmin, request, queryset):
    for request in queryset:
        request.user.role = request.new_role
        request.user.save()
        request.is_approved = True
        request.save()


approve_role_change.short_description = "Approve selected role change requests"


class RoleChangeRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "new_role", "reason", "is_approved"]
    actions = [approve_role_change]


admin.site.register(RoleChangeRequest, RoleChangeRequestAdmin)
