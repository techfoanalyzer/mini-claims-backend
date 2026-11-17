from rest_framework import serializers

from claims.models import ClaimStatusHistory


class ClaimStatusHistorySerializer(serializers.ModelSerializer):
    """Read-only nested serializer for audit trail."""

    changed_by_username = serializers.CharField(
        source="changed_by.username", read_only=True
    )

    class Meta:
        model = ClaimStatusHistory
        fields = [
            "id",
            "from_status",
            "to_status",
            "changed_by_username",
            "remarks",
            "created_at",
        ]
        read_only_fields = fields