from django.conf import settings
from django.db import models

from .claim import Claim


def plr_photo_path(instance, filename):
    """Upload path: media/plr/<claim_number>/<filename>"""
    return f"plr/{instance.claim.claim_number}/{filename}"


class PreliminaryLossReport(models.Model):

    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        related_name="plr",
    )
    damage_description = models.TextField()
    estimated_repair_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    damage_photo = models.ImageField(upload_to=plr_photo_path)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_plrs",
    )
    submitted_at = models.DateTimeField(auto_now=True)
    revision = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"PLR for {self.claim.claim_number} (rev {self.revision})"