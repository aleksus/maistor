
from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, Service


def category_list(request):
    categories = ServiceCategory.objects.all()

    return render(
        request,
        "services/category_list.html",
        {"categories": categories}
    )


def service_list(request, category_id):
    category = get_object_or_404(
        ServiceCategory,
        id=category_id
    )

    services = category.services.all()

    return render(
        request,
        "services/service_list.html",
        {
            "category": category,
            "services": services
        }
    )
