from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("register/",
         views.RegisterView.as_view(),
         name="register"),

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
        views.MasterProfileSetupView.as_view(),
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

    path(
        "client-profile/setup/",
        views.ClientProfileUpdateView.as_view(),
        name="client_profile_setup",
    ),
]
