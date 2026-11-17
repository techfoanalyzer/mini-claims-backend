from django.urls import path

from .views import (
    ClaimDetailView,
    ClaimListCreateView,
    PLRApproveView,
    PLRReviewView,
    PLRSubmitView,
)

urlpatterns = [
    path("claims/", ClaimListCreateView.as_view(), name="claim-list-create"),
    path("claims/<int:pk>/", ClaimDetailView.as_view(), name="claim-detail"),
    path("claims/<int:pk>/plr/", PLRSubmitView.as_view(), name="plr-submit"),
    path("claims/<int:pk>/plr/review/", PLRReviewView.as_view(), name="plr-review"),
    path("claims/<int:pk>/plr/approve/", PLRApproveView.as_view(), name="plr-approve"),
]