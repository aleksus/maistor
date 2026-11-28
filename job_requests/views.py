from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from services.models import Service
from .forms import JobRequestForm
from .models import JobRequest, RequestImage


class CreateJobView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):
    model = JobRequest
    form_class = JobRequestForm
    template_name = "requests/create_job.html"
    success_url = reverse_lazy("my_jobs")

    def test_func(self):
        return self.request.user.role == "client"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Само клиенти могат да публикуват заявки."
            )
            return redirect("home")

        return super().handle_no_permission()

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.client = self.request.user
            self.object.save()

            form.save_m2m()

            images = self.request.FILES.getlist("images")

            for image in images:
                RequestImage.objects.create(
                    job_request=self.object,
                    image=image
                )

        messages.success(
            self.request,
            "Заявката беше публикувана успешно!"
        )

        return super().form_valid(form)


class MyJobsView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):
    model = JobRequest
    template_name = "requests/my_jobs.html"
    context_object_name = "jobs"

    def test_func(self):
        return self.request.user.role == "client"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Тази страница е достъпна само за клиенти."
            )
            return redirect("home")

        return super().handle_no_permission()

    def get_queryset(self):
        return JobRequest.objects.filter(
            client=self.request.user
        ).prefetch_related(
            "services",
            "images"
        ).order_by("-created_at")


class AvailableRequestsView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):
    model = JobRequest
    template_name = "requests/available_requests.html"
    context_object_name = "requests"

    def test_func(self):
        return self.request.user.role == "master"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Само майстори могат да разглеждат свободните заявки."
            )
            return redirect("home")

        return super().handle_no_permission()

    def get_queryset(self):
        requests_list = JobRequest.objects.filter(
            status=JobRequest.Status.OPEN
        ).select_related(
            "client"
        ).prefetch_related(
            "services",
            "images"
        ).order_by("-created_at")

        city = self.request.GET.get("city", "").strip()
        search = self.request.GET.get("search", "").strip()
        service_id = self.request.GET.get("service", "").strip()

        if city:
            requests_list = requests_list.filter(
                city__icontains=city
            )

        if search:
            requests_list = requests_list.filter(
                title__icontains=search
            )

        if service_id.isdigit():
            requests_list = requests_list.filter(
                services__id=int(service_id)
            )

        return requests_list.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "services": Service.objects.all(),
            "selected_city": self.request.GET.get("city", "").strip(),
            "selected_search": self.request.GET.get("search", "").strip(),
            "selected_service": self.request.GET.get("service", "").strip(),
        })

        return context


class RequestDetailView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DetailView
):
    model = JobRequest
    template_name = "requests/request_detail.html"
    context_object_name = "job"

    def test_func(self):
        return self.request.user.role == "master"

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Само майстори могат да разглеждат подробностите на заявките."
            )
            return redirect("home")

        return super().handle_no_permission()

    def get_queryset(self):
        return JobRequest.objects.filter(
            status=JobRequest.Status.OPEN
        ).select_related(
            "client"
        ).prefetch_related(
            "services",
            "images"
        )
