from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import (
    UserRegisterForm,
    MasterProfileForm,
)
from .models import MasterProfile, ClientProfile


def register(request):

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                if user.role == "master":
                    MasterProfile.objects.create(
                        user=user,
                        description="",
                        city=""
                    )
                else:
                    ClientProfile.objects.create(user=user)

            login(request, user)

            if user.role == "master":
                return redirect("master_profile_setup")

            return redirect("home")

    else:
        form = UserRegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )



def master_profile_setup(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role != "master":
        return redirect("home")

    profile = request.user.master_profile

    if request.method == "POST":
        form = MasterProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("home")

    else:
        form = MasterProfileForm(instance=profile)

    return render(
        request,
        "accounts/master_profile_setup.html",
        {"form": form}
    )


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    else:
        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form}
    )


@login_required
def user_logout(request):
    if request.method == "POST":
        from django.contrib.auth import logout
        logout(request)
        return redirect("login")

    return redirect("home")
