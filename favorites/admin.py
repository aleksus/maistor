from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "master",
        "created_at",
    )

    list_filter = ("created_at",)
    search_fields = (
        "client__username",
        "master__user__username",
    )

    readonly_fields = ("created_at",)
