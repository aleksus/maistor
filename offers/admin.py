from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "job_request",
        "master",
        "price",
        "estimated_days",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = (
        "job_request__title",
        "master__user__username",
        "message",
    )

    readonly_fields = ("created_at",)
