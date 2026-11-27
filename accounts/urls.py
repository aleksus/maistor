from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),

    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),

    path(
        "master-profile/setup/",
        views.master_profile_setup,
        name="master_profile_setup"
    ),

    path(
        "masters/",
        views.MasterListView.as_view(),
        name="master_list"
    ),

    path(
        "masters/<int:pk>/",
        views.MasterDetailView.as_view(),
        name="master_detail"
    ),
]
