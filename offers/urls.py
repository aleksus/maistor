from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/<int:request_id>/",
        views.create_offer,
        name="create_offer"
    ),
]
