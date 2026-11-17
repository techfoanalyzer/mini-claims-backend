from django.urls import path

from .views import ClaimDetailView, ClaimListCreateView, PLRSubmitView

urlpatterns = [
    path("claims/", ClaimListCreateView.as_view(), name="claim-list-create"),
    path("claims/<int:pk>/", ClaimDetailView.as_view(), name="claim-detail"),
    path("claims/<int:pk>/plr/", PLRSubmitView.as_view(), name="plr-submit"),
]