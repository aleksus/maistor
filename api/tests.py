from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from job_requests.models import JobRequest
from services.models import Service, ServiceCategory


User = get_user_model()


class JobRequestAPITests(APITestCase):

    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name="Ремонт"
        )

        self.service = Service.objects.create(
            category=self.category,
            name="ВиК услуги"
        )

        self.client_user = User.objects.create_user(
            username="client_test",
            email="client@example.com",
            password="TestPassword123!",
            role="client",
        )

        self.other_client = User.objects.create_user(
            username="other_client",
            email="other@example.com",
            password="TestPassword123!",
            role="client",
        )

        self.master = User.objects.create_user(
            username="master_test",
            email="master@example.com",
            password="TestPassword123!",
            role="master",
        )

        self.url = reverse("api:request-list-create")

    def test_client_can_create_job_request(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            self.url,
            {
                "title": "Ремонт на баня",
                "description": "Трябва ми ремонт на баня.",
                "city": "София",
                "budget_min": "500.00",
                "budget_max": "1500.00",
                "services": [self.service.id],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        job_request = JobRequest.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(job_request.client, self.client_user)
        self.assertEqual(
            job_request.status,
            JobRequest.Status.OPEN
        )
        self.assertTrue(
            job_request.services.filter(
                id=self.service.id
            ).exists()
        )

    def test_client_sees_only_own_requests(self):
        own_request = JobRequest.objects.create(
            client=self.client_user,
            title="Моята заявка",
            description="Описание",
            city="София",
        )
        own_request.services.add(self.service)

        other_request = JobRequest.objects.create(
            client=self.other_client,
            title="Чужда заявка",
            description="Описание",
            city="Пловдив",
        )
        other_request.services.add(self.service)

        self.client.force_authenticate(user=self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["id"],
            own_request.id
        )

    def test_master_cannot_access_requests_api(self):
        self.client.force_authenticate(user=self.master)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_unauthenticated_user_cannot_access_requests_api(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    def test_invalid_budget_is_rejected(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            self.url,
            {
                "title": "Ремонт",
                "description": "Описание",
                "city": "София",
                "budget_min": "2000.00",
                "budget_max": "1000.00",
                "services": [self.service.id],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )