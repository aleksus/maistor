from django.urls import path

from .views import (
    ServiceCategoryListAPIView,
    ServiceListAPIView,
)

app_name = "api"

urlpatterns = [
    path(
        "categories/",
        ServiceCategoryListAPIView.as_view(),
        name="category-list",
    ),
    path(
        "services/",
        ServiceListAPIView.as_view(),
        name="service-list",
    ),
]