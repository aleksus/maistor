from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.CategoryListView.as_view(),
        name="category_list"
    ),
    path(
        "<int:category_id>/",
        views.ServiceListView.as_view(),
        name="service_list"
    ),
]
