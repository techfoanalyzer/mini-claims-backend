from django.conf import settings
from django.db import models

from .claim import Claim


class ClaimStatusHistory(models.Model):

    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="history",
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="status_changes",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name_plural = "Claim status histories"

    def __str__(self):
        return f"{self.claim.claim_number}: {self.from_status or '—'} → {self.to_status}"