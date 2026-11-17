from django.core.management.base import BaseCommand
from decouple import config

from claims.models import Workshop
from users.models import User


class Command(BaseCommand):
    help = "Seed test users (one per role) and two workshops. Idempotent."

    def handle(self, *args, **options):
        password = config("SEED_PASSWORD")

        # --- Workshops ---
        workshops = [
            {"name": "Karachi Motors", "city": "Karachi", "contact_number": "021111222333"},
            {"name": "Lahore Auto Works", "city": "Lahore", "contact_number": "042111444555"},
        ]
        for w in workshops:
            obj, created = Workshop.objects.get_or_create(
                name=w["name"],
                defaults={"city": w["city"], "contact_number": w["contact_number"]},
            )
            status = "Created" if created else "Exists"
            self.stdout.write(f"  Workshop: {obj.name} — {status}")

        # --- Users (one per role) ---
        users = [
            ("fnol_agent", User.Role.FNOL_AGENT, "03000000001"),
            ("surveyor", User.Role.SURVEYOR, "03000000002"),
            ("reviewer", User.Role.REVIEWER, "03000000003"),
            ("approver", User.Role.APPROVER, "03000000004"),
            ("workshop_agent", User.Role.WORKSHOP_AGENT, "03000000005"),
        ]
        for username, role, phone in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"role": role, "phone_number": phone},
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"  User: {username} ({role}) — Created")
            else:
                self.stdout.write(f"  User: {username} ({role}) — Exists")

        # --- Link workshop_agent to first workshop ---
        first_workshop = Workshop.objects.first()
        if first_workshop:
            wa = User.objects.get(username="workshop_agent")
            wa.workshop = first_workshop
            wa.save()
            self.stdout.write(f"  Linked workshop_agent → {first_workshop.name}")

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))