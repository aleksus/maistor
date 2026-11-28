from rest_framework import serializers

from job_requests.models import JobRequest
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