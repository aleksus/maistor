from rest_framework import generics

from services.models import Service, ServiceCategory

from .serializers import (
    ServiceCategorySerializer,
    ServiceSerializer,
)


class ServiceCategoryListAPIView(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


class ServiceListAPIView(generics.ListAPIView):
    queryset = Service.objects.select_related("category").all()
    serializer_class = ServiceSerializer