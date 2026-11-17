from django.contrib import admin

from .models import Claim, ClaimStatusHistory, PreliminaryLossReport, Workshop


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "contact_number")
    search_fields = ("name", "city")


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        "claim_number",
        "claimant_name",
        "status",
        "surveyor",
        "workshop",
        "created_at",
    )
    list_filter = ("status", "workshop")
    search_fields = ("claim_number", "policy_number", "claimant_name", "claimant_phone")
    readonly_fields = ("claim_number", "created_at", "updated_at")


@admin.register(PreliminaryLossReport)
class PreliminaryLossReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "claim",
        "estimated_repair_cost",
        "revision",
        "submitted_by",
        "submitted_at",
    )
    search_fields = ("claim__claim_number",)


@admin.register(ClaimStatusHistory)
class ClaimStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "claim",
        "from_status",
        "to_status",
        "changed_by",
        "created_at",
    )
    list_filter = ("to_status",)
    search_fields = ("claim__claim_number",)
    readonly_fields = ("created_at",)