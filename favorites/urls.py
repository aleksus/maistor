from django.urls import path

from . import views

urlpatterns = [
    path(
        "toggle/<int:master_id>/",
        views.ToggleFavoriteView.as_view(),
        name="toggle_favorite"
    ),
    path(
        "",
        views.FavoriteListView.as_view(),
        name="favorite_list"
    ),
]
