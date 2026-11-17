from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from claims.enums import ClaimResponse
from claims.models import Claim, PreliminaryLossReport
from claims.permissions import IsApprover, IsReviewer, IsSurveyor
from claims.serializers import ( ClaimDetailSerializer, DecisionSerializer, PLRSubmitSerializer,)
from core.services import notify, transition_status


class PLRSubmitView(APIView):
    """
    POST /api/claims/{pk}/plr/  — assigned surveyor submits or resubmits PLR.
    First submission: creates PLR, transitions INTIMATED → PLR_SUBMITTED.
    Resubmission (only when status == PLR_SENT_BACK): bumps revision,
    transitions PLR_SENT_BACK → PLR_SUBMITTED.
    """

    permission_classes = [IsAuthenticated, IsSurveyor]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Object-level: ye claim isi surveyor ka hona chahiye
        if claim.surveyor_id != request.user.id:
            return Response(
                {"error": ClaimResponse.CLAIM_403_NOT_YOURS},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Status check
        allowed_statuses = {Claim.Status.INTIMATED, Claim.Status.PLR_SENT_BACK}
        if claim.status not in allowed_statuses:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PLRSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_resubmission = claim.status == Claim.Status.PLR_SENT_BACK

        if is_resubmission:
            # Existing PLR update karo
            plr = claim.plr
            plr.damage_description = serializer.validated_data["damage_description"]
            plr.estimated_repair_cost = serializer.validated_data["estimated_repair_cost"]
            plr.damage_photo = serializer.validated_data["damage_photo"]
            plr.submitted_by = request.user
            plr.revision += 1
            plr.save()
        else:
            # Naya PLR create karo
            plr = PreliminaryLossReport.objects.create(
                claim=claim,
                damage_description=serializer.validated_data["damage_description"],
                estimated_repair_cost=serializer.validated_data["estimated_repair_cost"],
                damage_photo=serializer.validated_data["damage_photo"],
                submitted_by=request.user,
                revision=1,
            )

        # Transition to PLR_SUBMITTED
        transition_status(
            claim=claim,
            to_status=Claim.Status.PLR_SUBMITTED,
            changed_by=request.user,
            remarks=(
                f"PLR resubmitted (revision {plr.revision})."
                if is_resubmission
                else "PLR submitted."
            ),
        )

        # Notify reviewer (fire-and-forget)
        from users.models import User
        reviewer = User.objects.filter(role=User.Role.REVIEWER).first()
        if reviewer:
            notify(
                reviewer.email,
                f"PLR submitted for {claim.claim_number}",
                f"Surveyor {request.user.username} has submitted PLR for claim "
                f"{claim.claim_number}. Please review.",
            )

        return Response(
            {
                "details": ClaimResponse.PLR_SUBMITTED,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_201_CREATED if not is_resubmission else status.HTTP_200_OK,
        )



class PLRReviewView(APIView):
    """
    POST /api/claims/{pk}/plr/review/  — reviewer forwards or sends back.
    Body: {"decision": "forward"|"send_back", "remarks": "..."}
    """

    permission_classes = [IsAuthenticated, IsReviewer]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if claim.status != Claim.Status.PLR_SUBMITTED:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DecisionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision = serializer.validated_data["decision"]
        remarks = serializer.validated_data["remarks"]

        if decision == "forward":
            new_status = Claim.Status.PLR_REVIEWED
            message = ClaimResponse.PLR_REVIEWED
        elif decision == "send_back":
            new_status = Claim.Status.PLR_SENT_BACK
            message = ClaimResponse.PLR_SENT_BACK
        else:
            return Response(
                {"error": ClaimResponse.CLAIM_400_INVALID_DECISION},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transition_status(
            claim=claim,
            to_status=new_status,
            changed_by=request.user,
            remarks=remarks or f"Reviewer decision: {decision}.",
        )

        # Send back → surveyor ko email
        if decision == "send_back" and claim.surveyor:
            notify(
                claim.surveyor.email,
                f"PLR sent back for {claim.claim_number}",
                f"Reviewer sent back PLR for claim {claim.claim_number}. "
                f"Remarks: {remarks or '(no remarks)'}",
            )

        return Response(
            {
                "details": message,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )


class PLRApproveView(APIView):
    """
    POST /api/claims/{pk}/plr/approve/  — approver approves or sends back.
    Body: {"decision": "approve"|"send_back", "remarks": "..."}
    """

    permission_classes = [IsAuthenticated, IsApprover]

    def post(self, request, pk):
        try:
            claim = Claim.objects.get(pk=pk)
        except Claim.DoesNotExist:
            return Response(
                {"error": ClaimResponse.CLAIM_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if claim.status != Claim.Status.PLR_REVIEWED:
            return Response(
                {"error": ClaimResponse.CLAIM_400_WRONG_STATUS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DecisionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision = serializer.validated_data["decision"]
        remarks = serializer.validated_data["remarks"]

        if decision == "approve":
            new_status = Claim.Status.PLR_APPROVED
            message = ClaimResponse.PLR_APPROVED
        elif decision == "send_back":
            new_status = Claim.Status.PLR_SENT_BACK
            message = ClaimResponse.PLR_SENT_BACK
        else:
            return Response(
                {"error": ClaimResponse.CLAIM_400_INVALID_DECISION},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transition_status(
            claim=claim,
            to_status=new_status,
            changed_by=request.user,
            remarks=remarks or f"Approver decision: {decision}.",
        )

        if decision == "send_back" and claim.surveyor:
            notify(
                claim.surveyor.email,
                f"PLR sent back for {claim.claim_number}",
                f"Approver sent back PLR for claim {claim.claim_number}. "
                f"Remarks: {remarks or '(no remarks)'}",
            )

        return Response(
            {
                "details": message,
                "data": ClaimDetailSerializer(claim).data,
            },
            status=status.HTTP_200_OK,
        )