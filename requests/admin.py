from django.contrib import admin

from .models import JobRequest, RequestImage


class RequestImageInline(admin.TabularInline):
    model = RequestImage
    extra = 0


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "city",
        "status",
        "budget_min",
        "budget_max",
        "created_at",
    )

    list_filter = ("status", "city", "created_at")
    search_fields = (
        "title",
        "description",
        "client__username",
        "city",
    )

    filter_horizontal = ("services",)
    readonly_fields = ("created_at",)

    inlines = [RequestImageInline]


@admin.register(RequestImage)
class RequestImageAdmin(admin.ModelAdmin):
    list_display = ("job_request", "uploaded_at")
    list_filter = ("uploaded_at",)
