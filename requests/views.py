from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import JobRequestForm
from .models import JobRequest, RequestImage


@login_required
def create_job(request):
    if request.user.role != "client":
        messages.error(
            request,
            "Само клиенти могат да публикуват заявки."
        )
        return redirect("home")

    if request.method == "POST":
        form = JobRequestForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                job = form.save(commit=False)
                job.client = request.user
                job.save()

                form.save_m2m()

                images = request.FILES.getlist("images")

                for image in images:
                    RequestImage.objects.create(
                        job_request=job,
                        image=image
                    )

            messages.success(
                request,
                "Заявката беше публикувана успешно!"
            )

            return redirect("my_jobs")

    else:
        form = JobRequestForm()

    return render(
        request,
        "requests/create_job.html",
        {"form": form}
    )


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
