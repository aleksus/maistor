from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Клиент"
        MASTER = "master", "Майстор"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role,
        default=Role.CLIENT
    )
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username


class MasterProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="master_profile"
    )
    description = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    price_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_verified = models.BooleanField(default=False)

    services = models.ManyToManyField(
        "services.Service",
        related_name="masters",
        blank=True
    )

    def __str__(self):
        return f"Профил на {self.user.username}"


class ClientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Клиент: {self.user.username}"
