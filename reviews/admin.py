from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "offer",
        "rating",
        "created_at",
    )

    list_filter = ("rating", "created_at")
    search_fields = (
        "offer__master__user__username",
        "offer__job_request__title",
        "comment",
    )

    readonly_fields = ("created_at",)
