from rest_framework import serializers

from accounts.models import MasterProfile
from job_requests.models import JobRequest
from offers.models import Offer
from services.models import Service, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = "__all__"


class JobRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequest
        fields = [
            "id",
            "title",
            "description",
            "city",
            "address",
            "budget_min",
            "budget_max",
            "services",
            "status",
            "created_at",
            "deadline",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]

    def validate(self, attrs):
        budget_min = attrs.get("budget_min")
        budget_max = attrs.get("budget_max")

        if (
                budget_min is not None
                and budget_max is not None
                and budget_min > budget_max
        ):
            raise serializers.ValidationError({
                "budget_max": "Максималният бюджет не може да е по-малък от минималния."
            })

        return attrs

    def create(self, validated_data):
        validated_data["client"] = self.context["request"].user
        return super().create(validated_data)


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            "id",
            "job_request",
            "price",
            "message",
            "estimated_days",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]

    def validate_job_request(self, value):
        if value.status != JobRequest.Status.OPEN:
            raise serializers.ValidationError(
                "Можеш да подаваш оферти само за отворени заявки."
            )

        user = self.context["request"].user
        master_profile = MasterProfile.objects.filter(
            user=user
        ).first()

        if master_profile and Offer.objects.filter(
                job_request=value,
                master=master_profile,
        ).exists():
            raise serializers.ValidationError(
                "Вече си подал оферта за тази заявка."
            )

        return value

    def create(self, validated_data):
        user = self.context["request"].user
        master_profile = MasterProfile.objects.filter(user=user).first()

        if master_profile is None:
            raise serializers.ValidationError(
                "Нямаш създаден профил на майстор."
            )

        validated_data["master"] = master_profile

        return super().create(validated_data)
