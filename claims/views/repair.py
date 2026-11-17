from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from claims.enums import ClaimResponse
from claims.models import Claim
from claims.permissions import IsApprover, IsWorkshopAgent
from claims.serializers import ClaimDetailSerializer
from core.services import notify, transition_status


class RepairStartView(APIView):
    """POST /api/claims/{pk}/repair/start/ — workshop agent marks repair started."""

    permission_classes = [IsAuthenticated, IsWorkshopAgent]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Object-level: same workshop
        if not request.user.workshop_id or claim.workshop_id != request.user.workshop_id:
            return Response(
                {"error": ClaimResponse.CLAIM_403_NOT_YOURS},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != Claim.Status.PLR_APPROVED:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transition_status(
            claim=claim,
            to_status=Claim.Status.REPAIR_IN_PROGRESS,
            changed_by=request.user,
            remarks="Repair started at workshop.",
        )

        return Response(
            {
                "details": ClaimResponse.REPAIR_STARTED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )


class RepairCompleteView(APIView):
    """POST /api/claims/{pk}/repair/complete/ — workshop agent marks repair complete."""

    permission_classes = [IsAuthenticated, IsWorkshopAgent]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.workshop_id or claim.workshop_id != request.user.workshop_id:
            return Response(
                {"error": ClaimResponse.CLAIM_403_NOT_YOURS},
                status=status.HTTP_403_FORBIDDEN,
            )

        if claim.status != Claim.Status.REPAIR_IN_PROGRESS:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transition_status(
            claim=claim,
            to_status=Claim.Status.REPAIR_COMPLETED,
            changed_by=request.user,
            remarks="Repair completed at workshop.",
        )

        return Response(
            {
                "details": ClaimResponse.REPAIR_COMPLETED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )


class ClaimCloseView(APIView):
    """POST /api/claims/{pk}/close/ — approver closes the claim after repair."""

    permission_classes = [IsAuthenticated, IsApprover]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if claim.status != Claim.Status.REPAIR_COMPLETED:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remarks = request.data.get("remarks", "").strip()

        transition_status(
            claim=claim,
            to_status=Claim.Status.CLOSED,
            changed_by=request.user,
            remarks=remarks or "Claim closed by approver.",
        )

        # Notify the claimant's creator (FNOL agent) — claim closed
        if claim.created_by and claim.created_by.email:
            notify(
                claim.created_by.email,
                f"Claim {claim.claim_number} closed",
                f"Claim {claim.claim_number} for {claim.claimant_name} has been closed.",
            )

        return Response(
            {
                "details": ClaimResponse.CLAIM_CLOSED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )