from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_job, name="create_job"),
    path("my-jobs/", views.my_jobs, name="my_jobs"),
]