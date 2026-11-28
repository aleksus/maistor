from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import MasterProfile
from api.serializers import OfferSerializer
from job_requests.models import JobRequest
from offers.models import Offer
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


class OfferSerializerTests(APITestCase):

    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name="Ремонт"
        )

        self.service = Service.objects.create(
            category=self.category,
            name="ВиК услуги"
        )

        self.client_user = User.objects.create_user(
            username="offer_client",
            email="offer_client@example.com",
            password="TestPassword123!",
            role="client",
        )

        self.master = User.objects.create_user(
            username="offer_master",
            email="offer_master@example.com",
            password="TestPassword123!",
            role="master",
        )

        self.master_profile = MasterProfile.objects.create(
            user=self.master,
            description="Опитен майстор",
            city="София",
        )

        self.url = reverse("api:offer-list-create")

        self.job_request = JobRequest.objects.create(
            client=self.client_user,
            title="Ремонт на баня",
            description="Описание",
            city="София",
        )
        self.job_request.services.add(self.service)

    def test_offer_uses_current_master_profile(self):
        serializer = OfferSerializer(
            data={
                "job_request": self.job_request.id,
                "price": "850.00",
                "message": "Мога да извърша ремонта.",
                "estimated_days": 5,
            },
            context={
                "request": type(
                    "Request",
                    (),
                    {"user": self.master}
                )()
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        offer = serializer.save()

        self.assertEqual(offer.master, self.master_profile)
        self.assertEqual(offer.status, Offer.Status.PENDING)

    def test_offer_for_closed_request_is_rejected(self):
        self.job_request.status = JobRequest.Status.COMPLETED
        self.job_request.save()

        serializer = OfferSerializer(
            data={
                "job_request": self.job_request.id,
                "price": "850.00",
                "message": "Оферта",
                "estimated_days": 5,
            },
            context={
                "request": type(
                    "Request",
                    (),
                    {"user": self.master}
                )()
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("job_request", serializer.errors)

    def test_offer_status_is_read_only(self):
        serializer = OfferSerializer(
            data={
                "job_request": self.job_request.id,
                "price": "850.00",
                "message": "Оферта",
                "estimated_days": 5,
                "status": Offer.Status.ACCEPTED,
            },
            context={
                "request": type(
                    "Request",
                    (),
                    {"user": self.master}
                )()
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        offer = serializer.save()

        self.assertEqual(offer.status, Offer.Status.PENDING)

    def test_master_can_create_offer_through_api(self):
        self.client.force_authenticate(user=self.master)

        response = self.client.post(
            self.url,
            {
                "job_request": self.job_request.id,
                "price": "850.00",
                "message": "Мога да извърша ремонта.",
                "estimated_days": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        offer = Offer.objects.get(id=response.data["id"])
        self.assertEqual(offer.master, self.master_profile)

    def test_master_sees_only_own_offers(self):
        other_master = User.objects.create_user(
            username="other_master",
            email="other_master@example.com",
            password="TestPassword123!",
            role="master",
        )

        other_profile = MasterProfile.objects.create(
            user=other_master,
            description="Друг майстор",
            city="Пловдив",
        )

        own_offer = Offer.objects.create(
            job_request=self.job_request,
            master=self.master_profile,
            price="850.00",
            message="Моята оферта",
            estimated_days=5,
        )

        Offer.objects.create(
            job_request=self.job_request,
            master=other_profile,
            price="900.00",
            message="Чужда оферта",
            estimated_days=6,
        )

        self.client.force_authenticate(user=self.master)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_offer.id)

    def test_client_cannot_access_offers_api(self):
        self.client.force_authenticate(user=self.client_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_master_cannot_submit_duplicate_offer(self):
        self.client.force_authenticate(user=self.master)

        payload = {
            "job_request": self.job_request.id,
            "price": "850.00",
            "message": "Оферта",
            "estimated_days": 5,
        }

        first_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        second_response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            Offer.objects.filter(
                job_request=self.job_request,
                master=self.master_profile,
            ).count(),
            1,
        )
