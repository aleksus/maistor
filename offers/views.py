from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import MasterProfile
from requests.models import JobRequest
from .forms import OfferForm
from .models import Offer


@login_required
def create_offer(request, request_id):
    if request.user.role != "master":
        messages.error(request, "Само майстори могат да изпращат оферти.")
        return redirect("home")

    master = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    job = get_object_or_404(
        JobRequest,
        pk=request_id,
        status=JobRequest.Status.OPEN
    )

    # Проверяваме дали майсторът вече е изпратил оферта
    existing_offer = Offer.objects.filter(
        job_request=job,
        master=master
    ).exists()

    if existing_offer:
        messages.warning(request, "Вече си изпратил оферта по тази заявка.")
        return redirect("request_detail", pk=job.pk)

    if request.method == "POST":
        form = OfferForm(request.POST)

        if form.is_valid():
            offer = form.save(commit=False)
            offer.job_request = job
            offer.master = master
            offer.save()

            messages.success(request, "Офертата беше изпратена успешно!")
            return redirect("request_detail", pk=job.pk)
    else:
        form = OfferForm()

    return render(request, "offers/create_offer.html", {
        "form": form,
        "job": job,
    })
