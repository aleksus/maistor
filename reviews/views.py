from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from offers.models import Offer
from requests.models import JobRequest
from .forms import ReviewForm
from .models import Review


@login_required
@require_http_methods(["GET", "POST"])
def create_review(request, offer_id):
    if request.user.role != "client":
        messages.error(request, "Само клиенти могат да оставят отзиви.")
        return redirect("home")

    offer = get_object_or_404(
        Offer.objects.select_related("job_request", "master__user"),
        pk=offer_id,
        job_request__client=request.user,
        status=Offer.Status.ACCEPTED,
        job_request__status=JobRequest.Status.COMPLETED
    )

    # Проверяваме дали вече има отзив
    if Review.objects.filter(offer=offer).exists():
        messages.warning(request, "Вече си оставил отзив за тази поръчка.")
        return redirect("master_detail", pk=offer.master.pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.offer = offer
            review.save()

            messages.success(request, "Благодарим ти за оставения отзив!")
            return redirect("master_detail", pk=offer.master.pk)
    else:
        form = ReviewForm()

    return render(request, "reviews/create_review.html", {
        "form": form,
        "offer": offer,
    })
