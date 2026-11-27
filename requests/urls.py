from django.urls import path

from . import views

urlpatterns = [
    path("create/",
         views.CreateJobView.as_view(),
         name="create_job"),

    path("my-jobs/",
         views.MyJobsView.as_view(),
         name="my_jobs"),

    path(
        "available/",
        views.AvailableRequestsView.as_view(),
        name="available_requests"
    ),

    path(
        "available/<int:pk>/",
        views.request_detail,
        name="request_detail"
    ),
]
