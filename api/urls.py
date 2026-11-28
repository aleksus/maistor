from django.urls import path

from .views import (
    ServiceCategoryListAPIView,
    ServiceListAPIView,
    JobRequestListCreateAPIView,
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
    path(
        "requests/",
        JobRequestListCreateAPIView.as_view(),
        name="request-list-create",
    ),
]
