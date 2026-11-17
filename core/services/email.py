import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify(to_email, subject, body):
    """
    Fire-and-forget email notification.
    Never raises — a claim must still move even when mail is misconfigured.
    """
    if not to_email:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    except Exception:
        logger.exception("Could not send %r to %s", subject, to_email)