from django.db import models


class Offer(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Очаква одобрение"
        ACCEPTED = "accepted", "Приета"
        REJECTED = "rejected", "Отхвърлена"
        WITHDRAWN = "withdrawn", "Оттеглена"

    job_request = models.ForeignKey(
        "requests.JobRequest",
        on_delete=models.CASCADE,
        related_name="offers"
    )

    master = models.ForeignKey(
        "accounts.MasterProfile",
        on_delete=models.CASCADE,
        related_name="offers"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    message = models.TextField()
    estimated_days = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job_request", "master"],
                name="unique_master_offer_per_job"
            )
        ]

    def __str__(self):
        return f"Оферта от {self.master.user.username}"
