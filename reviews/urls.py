from django.urls import path
from . import views

urlpatterns = [
    path(
        "create/<int:offer_id>/",
        views.create_review,
        name="create_review"
    ),
]