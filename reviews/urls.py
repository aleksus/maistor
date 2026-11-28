from django.urls import path
from . import views

urlpatterns = [
    path(
        "create/<int:offer_id>/",
        views.CreateReviewView.as_view(),
        name="create_review"
    ),
]