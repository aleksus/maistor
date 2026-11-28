
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from accounts.models import MasterProfile

from .models import Favorite


class FavoriteRoleMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == "client"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Тази функционалност е достъпна само за клиенти."
            )
            return redirect("home")

        return super().handle_no_permission()


class ToggleFavoriteView(FavoriteRoleMixin, View):
    http_method_names = ["post"]

    def post(self, request, master_id):
        master = get_object_or_404(
            MasterProfile,
            pk=master_id,
            user__is_active=True
        )

        favorite = Favorite.objects.filter(
            client=request.user,
            master=master
        )

        if favorite.exists():
            favorite.delete()
            messages.success(
                request,
                "Майсторът беше премахнат от любими."
            )
        else:
            Favorite.objects.get_or_create(
                client=request.user,
                master=master
            )
            messages.success(
                request,
                "Майсторът беше добавен в любими."
            )

        return redirect("master_detail", pk=master_id)


class FavoriteListView(FavoriteRoleMixin, ListView):
    model = Favorite
    template_name = "favorites/favorite_list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        return Favorite.objects.filter(
            client=self.request.user
        ).select_related(
            "master",
            "master__user"
        ).prefetch_related(
            "master__services"
        ).order_by("-created_at")
