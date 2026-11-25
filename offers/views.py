from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

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

@login_required
def request_offers(request, request_id):
    if request.user.role != "client":
        messages.error(request, "Само клиенти могат да разглеждат офертите по своите заявки.")
        return redirect("home")

    job = get_object_or_404(
        JobRequest,
        pk=request_id,
        client=request.user
    )

    offers = Offer.objects.filter(
        job_request=job
    ).select_related(
        "master",
        "master__user"
    ).order_by("price", "created_at")

    return render(request, "offers/request_offers.html", {
        "job": job,
        "offers": offers,
    })


@login_required
@require_POST
def accept_offer(request, offer_id):
    if request.user.role != "client":
        messages.error(request, "Само клиенти могат да приемат оферти.")
        return redirect("home")

    # Проверяваме дали офертата съществува
    offer = get_object_or_404(
        Offer.objects.select_related("job_request"),
        pk=offer_id,
        job_request__client=request.user
    )

    job = offer.job_request

    with transaction.atomic():
        # Заключваме заявката, за да не могат да бъдат
        # приети две оферти едновременно.
        job = JobRequest.objects.select_for_update().get(pk=job.pk)

        if job.status != JobRequest.Status.OPEN:
            messages.error(
                request,
                "Тази заявка вече не е отворена."
            )
            return redirect("request_offers", request_id=job.pk)

        # Проверяваме отново офертата
        offer = Offer.objects.select_for_update().get(
            pk=offer_id,
            job_request=job
        )

        if offer.status != Offer.Status.PENDING:
            messages.error(
                request,
                "Тази оферта вече не е в очакване."
            )
            return redirect("request_offers", request_id=job.pk)

        # Приемаме избраната оферта
        offer.status = Offer.Status.ACCEPTED
        offer.save(update_fields=["status"])

        # Отхвърляме останалите чакащи оферти
        Offer.objects.filter(
            job_request=job,
            status=Offer.Status.PENDING
        ).exclude(
            pk=offer.pk
        ).update(
            status=Offer.Status.REJECTED
        )

        # Променяме статуса на заявката
        job.status = JobRequest.Status.IN_PROGRESS
        job.save(update_fields=["status"])

    messages.success(
        request,
        "Офертата беше приета успешно!"
    )

    return redirect("request_offers", request_id=job.pk)


@login_required
def master_orders(request):
    if request.user.role != "master":
        messages.error(request, "Тази страница е достъпна само за майстори.")
        return redirect("home")

    master = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    accepted_offers = Offer.objects.filter(
        master=master,
        status=Offer.Status.ACCEPTED
    ).select_related(
        "job_request",
        "job_request__client"
    ).order_by("-created_at")

    return render(request, "offers/master_orders.html", {
        "offers": accepted_offers,
    })

@login_required
@require_POST
def complete_order(request, request_id):
    if request.user.role != "master":
        messages.error(request, "Само майстори могат да завършват поръчки.")
        return redirect("home")

    master = get_object_or_404(
        MasterProfile,
        user=request.user
    )

    with transaction.atomic():
        job = get_object_or_404(
            JobRequest.objects.select_for_update(),
            pk=request_id
        )

        # Проверяваме дали този майстор има приета оферта
        # точно по тази заявка.
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