
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    offer = models.OneToOneField(
        "offers.Offer",
        on_delete=models.CASCADE,
        related_name="review"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.offer.master.user.username} - {self.rating}/5"
