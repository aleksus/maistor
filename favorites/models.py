
from django.db import models
from django.conf import settings


class Favorite(models.Model):
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    master = models.ForeignKey(
        "accounts.MasterProfile",
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "master"],
                name="unique_favorite_master"
            )
        ]

    def __str__(self):
        return f"{self.client.username} харесва {self.master.user.username}"
