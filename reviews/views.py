from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView

from offers.models import Offer
from requests.models import JobRequest
from .forms import ReviewForm
from .models import Review


class CreateReviewView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/create_review.html"

    def test_func(self):
        return self.request.user.role == "client"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Само клиенти могат да оставят отзиви."
            )
            return redirect("home")

        return super().handle_no_permission()

    def get_offer(self):
        if not hasattr(self, "_offer"):
            self._offer = get_object_or_404(
                Offer.objects.select_related(
                    "job_request",
                    "master__user"
                ),
                pk=self.kwargs["offer_id"],
                job_request__client=self.request.user,
                status=Offer.Status.ACCEPTED,
                job_request__status=JobRequest.Status.COMPLETED
            )

        return self._offer

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if (
                request.user.is_authenticated
                and request.user.role == "client"
                and Review.objects.filter(
            offer_id=kwargs["offer_id"]
        ).exists()
        ):
            offer = get_object_or_404(
                Offer,
                pk=kwargs["offer_id"],
                job_request__client=request.user
            )
            messages.warning(
                request,
                "Вече си оставил отзив за тази поръчка."
            )
            return redirect("master_detail", pk=offer.master.pk)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = self.get_offer()
        return context

    def form_valid(self, form):
        offer = self.get_offer()

        form.instance.offer = offer
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Благодарим ти за оставения отзив!"
        )

        return response

    def get_success_url(self):
        return redirect(
            "master_detail",
            pk=self.get_offer().master.pk
        ).url
