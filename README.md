# Mini Claims Backend

A small motor-insurance claims service. A claim is reported by an FNOL agent, assessed by a surveyor (PLR), reviewed by a reviewer, approved by an approver, repaired by a workshop, and finally closed by the approver. Every transition has a named actor and writes a row to the audit trail.

## Stack

- Python 3.12+
- Django 6.x
- Django REST Framework
- PostgreSQL 16 (via Docker)
- JWT auth (djangorestframework-simplejwt)

## Setup

**Prerequisites:** Python 3.12+, Docker Desktop, Git.

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd mini_claims
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate    # Windows (Git Bash)
   # source venv/bin/activate       # macOS / Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in real values:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` — at minimum, set a strong `SECRET_KEY`.

5. Start PostgreSQL via Docker:
   ```bash
   docker compose up -d
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Seed test users and workshops:
   ```bash
   python manage.py seed_data
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

The API is now available at `http://127.0.0.1:8000/`.

## Seeded Logins

The `seed_data` command creates one user per role. All passwords come from `SEED_PASSWORD` in your `.env` file.

| Username | Role | Password |
| --- | --- | --- |
| `fnol_agent` | FNOL_AGENT | `SEED_PASSWORD` |
| `surveyor` | SURVEYOR | `SEED_PASSWORD` |
| `reviewer` | REVIEWER | `SEED_PASSWORD` |
| `approver` | APPROVER | `SEED_PASSWORD` |
| `workshop_agent` | WORKSHOP_AGENT | `SEED_PASSWORD` |

The `admin` superuser is created separately with `python manage.py createsuperuser`.

## The Flow

| Status | Set when | Whose turn next |
| --- | --- | --- |
| INTIMATED | Claim created | Surveyor |
| PLR_SUBMITTED | Surveyor submits the PLR | Reviewer |
| PLR_REVIEWED | Reviewer forwards it | Approver |
| PLR_SENT_BACK | Reviewer or approver sends it back | Surveyor |
| PLR_APPROVED | Approver approves | Workshop |
| REPAIR_IN_PROGRESS | Workshop starts work | Workshop |
| REPAIR_COMPLETED | Workshop finishes | Approver |
| CLOSED | Approver closes the claim | — (terminal) |

## API

See `MiniClaims.postman_collection.json` in the repo root. Import it into Postman, set the `base_url` and `token` collection variables, and run the requests in folder order.

| # | Method & Path | Who | Purpose |
| - | --- | --- | --- |
| 1 | `POST /api/users/login/` | Anyone | Obtain JWT access token |
| 2 | `GET /api/users/me/` | Any logged-in | Caller's own profile + role |
| 3 | `GET /api/claims/` | Any logged-in | Role-scoped list, newest first |
| 4 | `POST /api/claims/` | FNOL agent | Intimate a claim |
| 5 | `GET /api/claims/{id}/` | Anyone on claim | Claim + PLR + full history |
| 6 | `POST /api/claims/{id}/plr/` | Assigned surveyor | Submit / resubmit PLR (multipart) |
| 7 | `POST /api/claims/{id}/plr/review/` | Reviewer | Forward or send back |
| 8 | `POST /api/claims/{id}/plr/approve/` | Approver | Approve or send back |
| 9 | `POST /api/claims/{id}/repair/start/` | Workshop agent | Repair has begun |
| 10 | `POST /api/claims/{id}/repair/complete/` | Workshop agent | Repair is finished |
| 11 | `POST /api/claims/{id}/close/` | Approver | Close the claim |

## Project Structure

```
mini_claims/
├── config/         # Django settings, root URLs, WSGI/ASGI
├── core/           # Shared helpers: email notify, status transition
├── users/          # Custom User model (role, phone, workshop FK), auth
├── claims/         # Claim, Workshop, PLR, ClaimStatusHistory, the whole flow
├── media/          # Uploaded damage photos (git-ignored)
├── manage.py
├── docker-compose.yml
├── requirements.txt
├── MiniClaims.postman_collection.json
└── README.md
```

- `config` — the Django project package (settings, url router).
- `core` — dependency-free shared utilities (email, transition helper).
- `users` — custom `User` (role, phone, workshop), JWT login, `/me` endpoint.
- `claims` — all four domain models, serializers, role permissions, views, URLs.