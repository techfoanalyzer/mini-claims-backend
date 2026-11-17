from datetime import date

from rest_framework import serializers

from claims.models import Claim, PreliminaryLossReport, Workshop
from users.models import User

from .preliminary_loss_report import PLRDetailSerializer
from .claim_status_history import ClaimStatusHistorySerializer


class _MiniUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role"]


class _MiniWorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = ["id", "name", "city"]


class ClaimCreateSerializer(serializers.ModelSerializer):
    """FNOL agent se claim create karwane ke liye."""

    class Meta:
        model = Claim
        fields = [
            "policy_number",
            "claimant_name",
            "claimant_phone",
            "loss_date",
            "loss_description",
            "surveyor",
            "workshop",
        ]

    def validate_loss_date(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Loss date cannot be in the future."
            )
        return value

    def validate_surveyor(self, value):
        if value.role != User.Role.SURVEYOR:
            raise serializers.ValidationError(
                "Assigned user must have the SURVEYOR role."
            )
        return value

    def validate_workshop(self, value):
        if value is None:
            raise serializers.ValidationError(
                "A workshop must be assigned at creation."
            )
        return value


class ClaimListSerializer(serializers.ModelSerializer):
    """List view — chhota, sirf zaroori fields."""

    surveyor_username = serializers.CharField(
        source="surveyor.username", read_only=True, default=None
    )
    workshop_name = serializers.CharField(
        source="workshop.name", read_only=True, default=None
    )

    class Meta:
        model = Claim
        fields = [
            "id",
            "claim_number",
            "claimant_name",
            "status",
            "loss_date",
            "surveyor_username",
            "workshop_name",
            "created_at",
        ]
        read_only_fields = fields


class ClaimDetailSerializer(serializers.ModelSerializer):
    """Full claim + nested PLR + full history."""

    created_by = _MiniUserSerializer(read_only=True)
    surveyor = _MiniUserSerializer(read_only=True)
    workshop = _MiniWorkshopSerializer(read_only=True)
    plr = serializers.SerializerMethodField()
    history = ClaimStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Claim
        fields = [
            "id",
            "claim_number",
            "policy_number",
            "claimant_name",
            "claimant_phone",
            "loss_date",
            "loss_description",
            "status",
            "created_by",
            "surveyor",
            "workshop",
            "plr",
            "history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_plr(self, obj):
        try:
            return PLRDetailSerializer(obj.plr, context=self.context).data
        except PreliminaryLossReport.DoesNotExist:
            return None