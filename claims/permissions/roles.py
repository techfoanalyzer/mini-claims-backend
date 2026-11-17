from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """Base — checks if user's role matches required_role."""

    required_role = None

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == self.required_role
        )


class IsFNOLAgent(HasRole):
    required_role = "FNOL_AGENT"


class IsSurveyor(HasRole):
    required_role = "SURVEYOR"


class IsReviewer(HasRole):
    required_role = "REVIEWER"


class IsApprover(HasRole):
    required_role = "APPROVER"


class IsWorkshopAgent(HasRole):
    required_role = "WORKSHOP_AGENT"