from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from .models import ServiceCategory, Service


class CategoryListView(ListView):
    model = ServiceCategory
    template_name = "services/category_list.html"
    context_object_name = "categories"


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_category(self):
        if not hasattr(self, "_category"):
            self._category = get_object_or_404(
                ServiceCategory,
                pk=self.kwargs["category_id"]
            )
        return self._category

    def get_queryset(self):
        return self.get_category().services.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()
        return context
