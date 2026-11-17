from django.conf import settings
from django.db import models
from django.utils import timezone

from .workshop import Workshop


class Claim(models.Model):
    

    class Status(models.TextChoices):
        INTIMATED = "INTIMATED", "Intimated"
        PLR_SUBMITTED = "PLR_SUBMITTED", "PLR Submitted"
        PLR_REVIEWED = "PLR_REVIEWED", "PLR Reviewed"
        PLR_SENT_BACK = "PLR_SENT_BACK", "PLR Sent Back"
        PLR_APPROVED = "PLR_APPROVED", "PLR Approved"
        REPAIR_IN_PROGRESS = "REPAIR_IN_PROGRESS", "Repair In Progress"
        REPAIR_COMPLETED = "REPAIR_COMPLETED", "Repair Completed"
        CLOSED = "CLOSED", "Closed"

    claim_number = models.CharField(max_length=20, unique=True, blank=True)
    policy_number = models.CharField(max_length=50)
    claimant_name = models.CharField(max_length=150)
    claimant_phone = models.CharField(max_length=15)
    loss_date = models.DateField()
    loss_description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INTIMATED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_claims",
    )
    surveyor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_claims",
        null=True,
        blank=True,
    )
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.PROTECT,
        related_name="claims",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.claim_number} - {self.claimant_name}"

    def save(self, *args, **kwargs):
        if not self.claim_number:
            year = timezone.now().year
            prefix = f"CLM-{year}-"
            last = (
                Claim.objects.filter(claim_number__startswith=prefix)
                .order_by("-claim_number")
                .first()
            )
            if last:
                last_num = int(last.claim_number.split("-")[-1])
                next_num = last_num + 1
            else:
                next_num = 1
            self.claim_number = f"{prefix}{next_num:05d}"
        super().save(*args, **kwargs)