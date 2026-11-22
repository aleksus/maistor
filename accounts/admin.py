from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, MasterProfile, ClientProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "phone",
        "is_staff",
        "is_active",
    )

    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "phone")

    fieldsets = UserAdmin.fieldsets + (
        ("Допълнителна информация", {
            "fields": ("role", "phone", "profile_picture")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Допълнителна информация", {
            "fields": ("email", "role", "phone", "profile_picture")
        }),
    )


@admin.register(MasterProfile)
class MasterProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "city",
        "experience_years",
        "price_from",
        "is_verified",
    )

    list_filter = ("city", "is_verified")
    search_fields = ("user__username", "city")
    filter_horizontal = ("services",)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city")
    list_filter = ("city",)
    search_fields = ("user__username", "city")
