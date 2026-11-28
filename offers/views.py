from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, ListView

from accounts.models import MasterProfile
from job_requests.models import JobRequest
from .forms import OfferForm
from .models import Offer


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    required_role = None
    permission_message = "Нямате достъп до тази страница."

    def test_func(self):
        return self.request.user.role == self.required_role

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                self.permission_message
            )
            return redirect("home")

        return super().handle_no_permission()


class CreateOfferView(RoleRequiredMixin, CreateView):
    model = Offer
    form_class = OfferForm
    template_name = "offers/create_offer.html"

    required_role = "master"
    permission_message = "Само майстори могат да изпращат оферти."

    def get_master(self):
        if not hasattr(self, "_master"):
            self._master = get_object_or_404(
                MasterProfile,
                user=self.request.user
            )
        return self._master

    def get_job(self):
        if not hasattr(self, "_job"):
            self._job = get_object_or_404(
                JobRequest,
                pk=self.kwargs["request_id"],
                status=JobRequest.Status.OPEN
            )
        return self._job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = self.get_job()
        return context

    def form_valid(self, form):
        job = self.get_job()
        master = self.get_master()

        existing_offer = Offer.objects.filter(
            job_request=job,
            master=master
        ).exists()

        if existing_offer:
            messages.warning(
                self.request,
                "Вече си изпратил оферта по тази заявка."
            )
            return redirect("request_detail", pk=job.pk)

        self.object = form.save(commit=False)
        self.object.job_request = job
        self.object.master = master
        self.object.save()

        messages.success(
            self.request,
            "Офертата беше изпратена успешно!"
        )

        return redirect("request_detail", pk=job.pk)


class RequestOffersView(RoleRequiredMixin, ListView):
    model = Offer
    template_name = "offers/request_offers.html"
    context_object_name = "offers"

    required_role = "client"
    permission_message = (
        "Само клиенти могат да разглеждат офертите по своите заявки."
    )

    def get_job(self):
        if not hasattr(self, "_job"):
            self._job = get_object_or_404(
                JobRequest,
                pk=self.kwargs["request_id"],
                client=self.request.user
            )
        return self._job

    def get_queryset(self):
        return Offer.objects.filter(
            job_request=self.get_job()
        ).select_related(
            "master",
            "master__user"
        ).order_by(
            "price",
            "created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = self.get_job()
        return context


class AcceptOfferView(RoleRequiredMixin, View):
    required_role = "client"
    permission_message = "Само клиенти могат да приемат оферти."
    http_method_names = ["post"]

    def post(self, request, offer_id):
        offer = get_object_or_404(
            Offer.objects.select_related("job_request"),
            pk=offer_id,
            job_request__client=request.user
        )

        job = offer.job_request

        with transaction.atomic():
            job = JobRequest.objects.select_for_update().get(
                pk=job.pk
            )

            if job.status != JobRequest.Status.OPEN:
                messages.error(
                    request,
                    "Тази заявка вече не е отворена."
                )
                return redirect(
                    "request_offers",
                    request_id=job.pk
                )

            offer = Offer.objects.select_for_update().get(
                pk=offer_id,
                job_request=job
            )

            if offer.status != Offer.Status.PENDING:
                messages.error(
                    request,
                    "Тази оферта вече не е в очакване."
                )
                return redirect(
                    "request_offers",
                    request_id=job.pk
                )

            offer.status = Offer.Status.ACCEPTED
            offer.save(update_fields=["status"])

            Offer.objects.filter(
                job_request=job,
                status=Offer.Status.PENDING
            ).exclude(
                pk=offer.pk
            ).update(
                status=Offer.Status.REJECTED
            )

            job.status = JobRequest.Status.IN_PROGRESS
            job.save(update_fields=["status"])

        messages.success(
            request,
            "Офертата беше приета успешно!"
        )

        return redirect(
            "request_offers",
            request_id=job.pk
        )


class MasterOrdersView(RoleRequiredMixin, ListView):
    model = Offer
    template_name = "offers/master_orders.html"
    context_object_name = "offers"

    required_role = "master"
    permission_message = (
        "Тази страница е достъпна само за майстори."
    )

    def get_queryset(self):
        master = get_object_or_404(
            MasterProfile,
            user=self.request.user
        )

        return Offer.objects.filter(
            master=master,
            status=Offer.Status.ACCEPTED
        ).select_related(
            "job_request",
            "job_request__client"
        ).order_by("-created_at")


class CompleteOrderView(RoleRequiredMixin, View):
    required_role = "master"
    permission_message = (
        "Само майстори могат да завършват поръчки."
    )
    http_method_names = ["post"]

    def post(self, request, request_id):
        master = get_object_or_404(
            MasterProfile,
            user=request.user
        )

        with transaction.atomic():
            job = get_object_or_404(
                JobRequest.objects.select_for_update(),
                pk=request_id
            )

            accepted_offer = Offer.objects.filter(
                job_request=job,
                master=master,
                status=Offer.Status.ACCEPTED
            ).exists()

            if not accepted_offer:
                messages.error(
                    request,
                    "Нямаш приета оферта по тази заявка."
                )
                return redirect("master_orders")

            if job.status != JobRequest.Status.IN_PROGRESS:
                messages.error(
                    request,
                    "Тази поръчка не е в процес на изпълнение."
                )
                return redirect("master_orders")

            job.status = JobRequest.Status.COMPLETED
            job.save(update_fields=["status"])

        messages.success(
            request,
            "Поръчката беше маркирана като завършена."
        )

        return redirect("master_orders")
