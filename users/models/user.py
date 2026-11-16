from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        FNOL_AGENT = "FNOL_AGENT", "FNOL Agent"
        SURVEYOR = "SURVEYOR", "Surveyor"
        REVIEWER = "REVIEWER", "Reviewer"
        APPROVER = "APPROVER", "Approver"
        WORKSHOP_AGENT = "WORKSHOP_AGENT", "Workshop Agent"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.FNOL_AGENT,
        help_text="User ka role — access control isi se hota hai",
    )
    phone_number = models.CharField(max_length=15, blank=True),
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"