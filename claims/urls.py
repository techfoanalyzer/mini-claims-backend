from django.urls import path

from .views import (
    ClaimCloseView,
    ClaimDetailView,
    ClaimListCreateView,
    PLRApproveView,
    PLRReviewView,
    PLRSubmitView,
    RepairCompleteView,
    RepairStartView,
)

urlpatterns = [
    path("claims/", ClaimListCreateView.as_view(), name="claim-list-create"),
    path("claims/<int:pk>/", ClaimDetailView.as_view(), name="claim-detail"),
    path("claims/<int:pk>/plr/", PLRSubmitView.as_view(), name="plr-submit"),
    path("claims/<int:pk>/plr/review/", PLRReviewView.as_view(), name="plr-review"),
    path("claims/<int:pk>/plr/approve/", PLRApproveView.as_view(), name="plr-approve"),
    path("claims/<int:pk>/repair/start/", RepairStartView.as_view(), name="repair-start"),
    path("claims/<int:pk>/repair/complete/", RepairCompleteView.as_view(), name="repair-complete"),
    path("claims/<int:pk>/close/", ClaimCloseView.as_view(), name="claim-close"),
]