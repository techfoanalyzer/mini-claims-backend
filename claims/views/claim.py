from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from claims.enums import ClaimResponse
from claims.models import Claim
from claims.permissions import IsFNOLAgent
from claims.serializers import (
    ClaimCreateSerializer,
    ClaimDetailSerializer,
    ClaimListSerializer,
)
from core.services import transition_status
from users.models import User


def _can_view_claim(user, claim):
    """Object-level check: kaun claim dekh sakta hai."""
    if user.is_superuser:
        return True
    if user.role in (User.Role.REVIEWER, User.Role.APPROVER):
        return True
    if user.role == User.Role.FNOL_AGENT and claim.created_by_id == user.id:
        return True
    if user.role == User.Role.SURVEYOR and claim.surveyor_id == user.id:
        return True
    if (
        user.role == User.Role.WORKSHOP_AGENT
        and user.workshop_id
        and claim.workshop_id == user.workshop_id
    ):
        return True
    return False


class ClaimListCreateView(APIView):
    """
    GET  /api/claims/  — role-scoped list, newest first
    POST /api/claims/  — FNOL agent creates claim
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsFNOLAgent()]
        return [IsAuthenticated()]

    def get(self, request):
        user = request.user
        qs = Claim.objects.select_related("surveyor", "workshop").all()

        if user.role == User.Role.SURVEYOR:
            qs = qs.filter(surveyor=user)
        elif user.role == User.Role.FNOL_AGENT:
            qs = qs.filter(created_by=user)
        elif user.role == User.Role.WORKSHOP_AGENT:
            if user.workshop_id:
                qs = qs.filter(workshop_id=user.workshop_id)
            else:
                qs = qs.none()

        serializer = ClaimListSerializer(qs, many=True)
        return Response(
            {
                "details": ClaimResponse.CLAIM_LIST_FETCHED,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ClaimCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        claim = serializer.save(created_by=request.user)

        transition_status(
            claim=claim,
            to_status=Claim.Status.INTIMATED,
            changed_by=request.user,
            remarks="Claim created by FNOL agent.",
            from_status="",
        )

        return Response(
            {
                "details": ClaimResponse.CLAIM_201_CREATED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ClaimDetailView(APIView):
    """GET /api/claims/{id}/ — full claim + PLR + history."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            claim = (
                Claim.objects.select_related("created_by", "surveyor", "workshop")
                .prefetch_related("history")
                .get(pk=pk)
            )
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_view_claim(request.user, claim):
            return Response(
                {"error": ClaimResponse.CLAIM_403_NOT_YOURS},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "details": ClaimResponse.CLAIM_DETAIL_FETCHED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )