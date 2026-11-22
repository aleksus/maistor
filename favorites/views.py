from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from accounts.models import MasterProfile
from .models import Favorite


@login_required
@require_POST
def toggle_favorite(request, master_id):
    # Само клиенти могат да добавят майстори в любими.
    if request.user.role != "client":
        messages.error(
            request,
            "Само клиентите могат да добавят майстори в любими."
        )
        return redirect("master_detail", pk=master_id)

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
        messages.success(request, "Майсторът беше премахнат от любими.")
    else:
        Favorite.objects.create(
            client=request.user,
            master=master
        )
        messages.success(request, "Майсторът беше добавен в любими.")

    return redirect("master_detail", pk=master_id)