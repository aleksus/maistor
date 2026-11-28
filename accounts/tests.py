from django.contrib.auth import get_user_model
from django.test import TestCase

from .forms import MasterProfileForm
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
