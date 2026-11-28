from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from requests.models import JobRequest
from services.models import Service, ServiceCategory
from .permissions import IsClient
from .serializers import JobRequestSerializer
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


class JobRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = JobRequestSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        return JobRequest.objects.filter(
            client=self.request.user
        ).prefetch_related("services")

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
