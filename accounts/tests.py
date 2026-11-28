from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import MasterProfileForm
from .models import ClientProfile
from .models import MasterProfile

User = get_user_model()


class MasterProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_master",
            email="master@example.com",
            password="TestPassword123!",
            role=User.Role.MASTER,
        )

        self.profile = MasterProfile.objects.create(
            user=self.user,
            description="Опитен майстор",
            experience_years=5,
            city="София",
        )

    def test_username_and_email_are_initially_populated(self):
        form = MasterProfileForm(instance=self.profile)

        self.assertEqual(
            form["username"].value(),
            "test_master",
        )
        self.assertEqual(
            form["email"].value(),
            "master@example.com",
        )

    def test_username_and_email_fields_are_disabled(self):
        form = MasterProfileForm(instance=self.profile)

        self.assertTrue(form.fields["username"].disabled)
        self.assertTrue(form.fields["email"].disabled)

    def test_submitted_username_and_email_cannot_be_changed(self):
        form = MasterProfileForm(
            data={
                "username": "changed_username",
                "email": "changed@example.com",
                "description": "Ново описание",
                "experience_years": 6,
                "city": "Пловдив",
                "address": "",
                "price_from": "",
                "services": [],
            },
            instance=self.profile,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.user.refresh_from_db()

        self.assertEqual(self.user.username, "test_master")
        self.assertEqual(self.user.email, "master@example.com")
        self.assertEqual(
            self.profile.description,
            "Ново описание",
        )


class ClientProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="test_client",
            email="client@example.com",
            password="TestPassword123!",
            role=User.Role.CLIENT,
        )

        self.profile = ClientProfile.objects.create(
            user=self.client_user,
            city="София",
            address="бул. България 10",
        )

        self.url = reverse("client_profile_setup")

    def test_client_can_access_own_profile(self):
        self.client.force_login(self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "accounts/client_profile_setup.html",
        )

    def test_client_can_update_own_profile(self):
        self.client.force_login(self.client_user)

        response = self.client.post(
            self.url,
            {
                "city": "Пловдив",
                "address": "ул. Главна 15",
            },
        )

        self.profile.refresh_from_db()

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.profile.city, "Пловдив")
        self.assertEqual(
            self.profile.address,
            "ул. Главна 15",
        )

    def test_master_cannot_access_client_profile(self):
        master = User.objects.create_user(
            username="test_master",
            email="master@example.com",
            password="TestPassword123!",
            role=User.Role.MASTER,
        )

        self.client.force_login(master)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("home"))

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)
