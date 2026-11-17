from rest_framework import serializers

from claims.models import PreliminaryLossReport


class PLRDetailSerializer(serializers.ModelSerializer):
    """Read-only nested serializer for the claim detail view."""

    submitted_by_username = serializers.CharField(
        source="submitted_by.username", read_only=True
    )

    class Meta:
        model = PreliminaryLossReport
        fields = [
            "id",
            "damage_description",
            "estimated_repair_cost",
            "damage_photo",
            "submitted_by_username",
            "submitted_at",
            "revision",
        ]
        read_only_fields = fields


class PLRSubmitSerializer(serializers.ModelSerializer):
    """Surveyor PLR submit/resubmit karne ke liye. Photo validate karta hai."""

    MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

    class Meta:
        model = PreliminaryLossReport
        fields = ["damage_description", "estimated_repair_cost", "damage_photo"]

    def validate_damage_photo(self, value):
        ext = value.name.rsplit(".", 1)[-1].lower() if "." in value.name else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Only jpg, jpeg, or png files are allowed."
            )
        if value.size > self.MAX_PHOTO_SIZE:
            raise serializers.ValidationError("Photo size must not exceed 5MB.")
        return value