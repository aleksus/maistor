from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    CreateView,
)

from favorites.models import Favorite
from services.models import ServiceCategory, Service
from .forms import (
    UserRegisterForm,
    MasterProfileForm,
    ClientProfileForm,
)
from .models import MasterProfile, ClientProfile


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()

            group_name = (
                "Майстори"
                if user.role == "master"
                else "Клиенти"
            )

            group, created = Group.objects.get_or_create(
                name=group_name
            )

            user.groups.add(group)

            if user.role == "master":
                MasterProfile.objects.create(
                    user=user,
                    description="",
                    city=""
                )
            else:
                ClientProfile.objects.create(user=user)

        login(self.request, user)

        if user.role == "master":
            return redirect("master_profile_setup")

        return redirect("client_profile_setup")


class MasterProfileSetupView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = MasterProfile
    form_class = MasterProfileForm
    template_name = "accounts/master_profile_setup.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.request.user.role == "master"

    def get_object(self, queryset=None):
        return self.request.user.master_profile

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class ClientProfileUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = ClientProfile
    form_class = ClientProfileForm
    template_name = "accounts/client_profile_setup.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.request.user.role == "client"

    def get_object(self, queryset=None):
        return self.request.user.client_profile

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("home")

        return super().handle_no_permission()


class MasterListView(ListView):
    model = MasterProfile
    template_name = "accounts/master_list.html"
    context_object_name = "masters"

    def get_queryset(self):
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

        params = self.request.GET

        city = params.get("city", "").strip()
        category_id = params.get("category", "").strip()
        service_id = params.get("service", "").strip()
        min_experience = params.get("min_experience", "").strip()
        max_price = params.get("max_price", "").strip()
        search = params.get("search", "").strip()

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

        sort = params.get("sort", "rating")

        if sort == "experience":
            masters = masters.order_by("-experience_years")
        elif sort == "price":
            masters = masters.order_by("price_from")
        elif sort == "rating":
            masters = masters.order_by(
                "-avg_rating",
                "-review_count"
            )
        else:
            masters = masters.order_by("-id")

        return masters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        params = self.request.GET

        context.update({
            "categories": ServiceCategory.objects.all(),
            "services": Service.objects.select_related(
                "category"
            ).all(),
            "selected_city": params.get("city", "").strip(),
            "selected_category": params.get("category", "").strip(),
            "selected_service": params.get("service", "").strip(),
            "selected_min_experience": params.get(
                "min_experience", ""
            ).strip(),
            "selected_max_price": params.get(
                "max_price", ""
            ).strip(),
            "selected_search": params.get("search", "").strip(),
            "selected_sort": params.get("sort", "rating"),
        })

        return context


class MasterDetailView(DetailView):
    model = MasterProfile
    template_name = "accounts/master_detail.html"
    context_object_name = "master"

    def get_queryset(self):
        return MasterProfile.objects.select_related(
            "user"
        ).prefetch_related(
            "services",
            "services__category",
            "offers__review"
        ).annotate(
            avg_rating=Avg("offers__review__rating"),
            review_count=Count("offers__review", distinct=True)
        ).filter(
            user__is_active=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        master = self.object
        user = self.request.user

        is_favorite = False

        if user.is_authenticated and user.role == "client":
            is_favorite = Favorite.objects.filter(
                client=user,
                master=master
            ).exists()

        reviews = master.offers.filter(
            status="accepted",
            review__isnull=False
        ).select_related(
            "review",
            "job_request",
            "job_request__client"
        ).order_by("-review__created_at")

        context.update({
            "master": master,
            "reviews": reviews,
            "is_favorite": is_favorite,
        })

        return context
