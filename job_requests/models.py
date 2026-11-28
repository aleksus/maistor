from django.conf import settings
from django.db import models


class JobRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Отворена"
        IN_PROGRESS = "in_progress", "В процес"
        COMPLETED = "completed", "Завършена"
        CANCELLED = "cancelled", "Отказана"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_requests"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)

    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    services = models.ManyToManyField(
        "services.Service",
        related_name="job_requests"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class RequestImage(models.Model):
    job_request = models.ForeignKey(
        JobRequest,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="job_requests/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Снимка към {self.job_request.title}"
