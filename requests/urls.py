from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_job, name="create_job"),
    path("my-jobs/", views.my_jobs, name="my_jobs"),

    path(
        "available/",
        views.available_requests,
        name="available_requests"
    ),

    path(
        "available/<int:pk>/",
        views.request_detail,
        name="request_detail"
    ),
]