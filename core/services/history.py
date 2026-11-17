from django.db import transaction


@transaction.atomic
def transition_status(
    *, claim, to_status, changed_by, remarks="", from_status=None
):
    """
    Status transition ka single source of truth.
    from_status=None → claim ka current status use hoga.
    from_status="" (explicit) → creation ke liye.
    """
    from claims.models import ClaimStatusHistory

    effective_from = from_status if from_status is not None else claim.status
    claim.status = to_status
    claim.save(update_fields=["status", "updated_at"])

    return ClaimStatusHistory.objects.create(
        claim=claim,
        from_status=effective_from,
        to_status=to_status,
        changed_by=changed_by,
        remarks=remarks,
    )