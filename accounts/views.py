from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from services.models import ServiceCategory, Service
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


def master_list(request):
    masters = MasterProfile.objects.filter(
        user__is_active=True
    ).select_related(
        "user"
    ).prefetch_related(
        "services",
        "services__category"
    ).annotate(
        avg_rating=Avg("offers__review__rating"),
        review_count=Count("offers__review", distinct=True)
    )

    # Филтри от GET параметрите
    city = request.GET.get("city", "").strip()
    category_id = request.GET.get("category", "").strip()
    service_id = request.GET.get("service", "").strip()
    min_experience = request.GET.get("min_experience", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    search = request.GET.get("search", "").strip()

    if city:
        masters = masters.filter(city__icontains=city)

    if category_id.isdigit():
        masters = masters.filter(
            services__category_id=int(category_id)
        )

    if service_id.isdigit():
        masters = masters.filter(
            services__id=int(service_id)
        )

    if min_experience.isdigit():
        masters = masters.filter(
            experience_years__gte=int(min_experience)
        )

    if max_price:
        try:
            masters = masters.filter(
                price_from__lte=float(max_price)
            )
        except ValueError:
            pass

    if search:
        masters = masters.filter(
            user__username__icontains=search
        )

    masters = masters.distinct()

    # Сортиране
    sort = request.GET.get("sort", "rating")

    if sort == "experience":
        masters = masters.order_by("-experience_years")
    elif sort == "price":
        masters = masters.order_by("price_from")
    elif sort == "rating":
        masters = masters.order_by("-avg_rating", "-review_count")
    else:
        masters = masters.order_by("-id")

    context = {
        "masters": masters,
        "categories": ServiceCategory.objects.all(),
        "services": Service.objects.select_related("category").all(),
        "selected_city": city,
        "selected_category": category_id,
        "selected_service": service_id,
        "selected_min_experience": min_experience,
        "selected_max_price": max_price,
        "selected_search": search,
        "selected_sort": sort,
    }

    return render(request, "accounts/master_list.html", context)


def master_detail(request, pk):
    master = get_object_or_404(
        MasterProfile.objects.select_related("user").prefetch_related(
            "services",
            "services__category",
            "offers__review"
        ).annotate(
            avg_rating=Avg("offers__review__rating"),
            review_count=Count("offers__review", distinct=True)
        ),
        pk=pk,
        user__is_active=True
    )

    reviews = master.offers.filter(
        status="accepted",
        review__isnull=False
    ).select_related(
        "review",
        "job_request",
        "job_request__client"
    ).order_by("-review__created_at")

    context = {
        "master": master,
        "reviews": reviews,
    }

    return render(request, "accounts/master_detail.html", context)
