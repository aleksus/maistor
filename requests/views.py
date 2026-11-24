from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import JobRequest, RequestImage
from .forms import JobRequestForm

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

