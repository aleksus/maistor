from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    path(
        "master-profile/setup/",
        views.master_profile_setup,
        name="master_profile_setup"
    ),
    path("masters/", views.master_list, name="master_list"),
]
