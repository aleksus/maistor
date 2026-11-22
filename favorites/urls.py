from django.urls import path
from . import views

urlpatterns = [
    path(
        "toggle/<int:master_id>/",
        views.toggle_favorite,
        name="toggle_favorite"
    ),
]