from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

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


@login_required
def my_jobs(request):
    if request.user.role != "client":
        messages.error(
            request,
            "Тази страница е достъпна само за клиенти."
        )
        return redirect("home")

    jobs = JobRequest.objects.filter(
        client=request.user
    ).prefetch_related(
        "services",
        "images"
    ).order_by("-created_at")

    return render(
        request,
        "requests/my_jobs.html",
        {"jobs": jobs}
    )


@login_required
def available_requests(request):
    if request.user.role != "master":
        messages.error(
            request,
            "Само майстори могат да разглеждат свободните заявки."
        )
        return redirect("home")

    requests_list = JobRequest.objects.filter(
        status=JobRequest.Status.OPEN
    ).select_related(
        "client"
    ).prefetch_related(
        "services",
        "images"
    ).order_by("-created_at")

    city = request.GET.get("city", "").strip()
    search = request.GET.get("search", "").strip()
    service_id = request.GET.get("service", "").strip()

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

    requests_list = requests_list.distinct()

    from services.models import Service

    context = {
        "requests": requests_list,
        "services": Service.objects.all(),
        "selected_city": city,
        "selected_search": search,
        "selected_service": service_id,
    }

    return render(
        request,
        "requests/available_requests.html",
        context
    )


@login_required
def request_detail(request, pk):
    if request.user.role != "master":
        messages.error(
            request,
            "Само майстори могат да разглеждат подробностите на заявките."
        )
        return redirect("home")

    job = get_object_or_404(
        JobRequest.objects.select_related(
            "client"
        ).prefetch_related(
            "services",
            "images"
        ),
        pk=pk,
        status=JobRequest.Status.OPEN
    )

    return render(
        request,
        "requests/request_detail.html",
        {"job": job}
    )
