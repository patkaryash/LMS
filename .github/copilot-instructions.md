# Lab Management System (LMS) — Copilot Instructions

## Project Overview

A **Lab Management System** for college computer labs. Django REST API backend, React + TypeScript frontend. Manages labs, PCs, equipment, software, maintenance logs, tickets, and notifications.

## Quick Commands

```bash
# Backend (from backend/LMS/)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
python manage.py test
python manage.py createsuperuser
python manage.py check_escalations       # daily cron: escalate stale maintenance logs

# Frontend (from frontend/)
npm install
npm run dev          # Vite dev server on :5173
npm run build
npm run lint
```

## Architecture

```
backend/LMS/
├── LMS/               # Django project config (settings, root urls, wsgi)
├── labs/              # Core app — owns User model + Lab, PC, Equipment, Software, MaintenanceLog, Inventory
├── notifications/     # Notification model, escalation service, management command
├── tickets/           # Student support tickets
├── users/             # Auth endpoints (register, login) — re-exports labs.User, does NOT define its own
└── manage.py

frontend/src/
├── pages/             # Route-level components (Login, Dashboard, Labs, Maintenance, etc.)
├── components/        # Reusable UI (AppLayout, Sidebar, HeaderBar, ProtectedRoute)
├── contexts/          # AuthContext (JWT state), ThemeContext (dark/light)
├── services/          # api.ts — axios wrapper with token interceptors
├── types/             # Shared TypeScript interfaces
└── assets/
```

### Critical: User Model Ownership

`AUTH_USER_MODEL = 'labs.User'` — the **labs** app owns the canonical User model. The **users** app re-exports it (`from labs.models import User`). **Never define a second User model** — it will break authentication across the entire project.

### User Roles

Only two roles exist: `admin` and `student`. There is no `lab_assistant` or `technician` role. The `IsTechnicianOrAdmin` permission class in `labs/permissions.py` is unused/dead code.

## Backend Conventions

### Models
- CamelCase class names, snake_case fields
- `auto_now_add=True` for creation timestamps, `auto_now=True` for update timestamps
- Choice fields as tuple-of-tuples: `STATUS_CHOICES = (('pending', 'Pending'), ('fixed', 'Fixed'))`
- Always define `__str__()` and `related_name` on ForeignKeys
- Use `settings.AUTH_USER_MODEL` (not direct import) in ForeignKey declarations

### Views
- Use DRF class-based generics: `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`
- Use `@api_view` + `@permission_classes` decorators for one-off action endpoints
- Override `perform_create()` to auto-populate user/FK fields from request context
- Override `get_queryset()` for role-based filtering

### Serializers
- `ModelSerializer` with explicit `Meta.fields` tuple or `'__all__'`
- Mark auto-populated fields as `read_only_fields`
- Use `serializers.Serializer` for non-model/dynamic data (e.g., InventorySerializer)

### Permissions (labs/permissions.py)
| Class | Behavior |
|---|---|
| `IsAdminOrReadOnly` | Authenticated read; admin-only write |
| `IsAdminUser` | Admin-only for all methods |
| `AllowAuthenticatedReadAndCreateElseAdmin` | Any auth user can read/create; admin-only update/delete |

### URL Patterns
- All API routes prefixed with `/api/`
- Apps mounted in `LMS/urls.py`: `path('api/', include('labs.urls'))`, `path('api/notifications/', include('notifications.urls'))`, etc.
- Hyphenated paths, trailing slashes: `/api/maintenance/`, `/api/read-all/`
- Nested resources: `/api/labs/<int:lab_id>/pcs/`

### Admin Registration
- Use `@admin.register(Model)` decorator with custom `ModelAdmin`
- Always set `list_display`, `list_filter`, `search_fields`

### Authentication
- JWT via `djangorestframework-simplejwt` — access token 60 min, refresh 1 day, rotation enabled
- Login returns `{access, refresh, role, username}` at `POST /api/users/login/`
- Frontend sends `Authorization: Bearer <token>` header

### Database
- SQLite by default; MySQL via env vars (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- Config uses `python-decouple` — set env vars in `.env` file

### Notifications Module
- `Notification` model links to `User` and `MaintenanceLog`
- Service layer in `notifications/services.py` — use these functions, don't query the model directly from views
- `python manage.py check_escalations` — cron job that creates escalation notifications for pending maintenance logs older than 7 days; targets admin users; prevents duplicates by checking (user, maintenance_log, type='escalation')

## Frontend Conventions

### Stack
- React 19 + TypeScript (strict mode, `noUncheckedIndexedAccess`)
- Vite, Tailwind CSS 4, Material UI (`@mui/material`, `@mui/x-data-grid`), Lucide icons
- react-router-dom for routing, React Context for state (no Redux)

### Patterns
- Pages in `pages/`, reusable components in `components/`
- `AuthContext` manages JWT tokens in localStorage + user state
- `api.ts` organizes endpoints into grouped objects: `labsAPI.getAll()`, `maintenanceAPI.create()`, etc.
- Axios interceptors handle token refresh on 401 automatically
- `ProtectedRoute` wraps authenticated pages; `AdminRoute` restricts admin-only views
- `VITE_API_BASE_URL` env var for API base (defaults to `http://127.0.0.1:8001/api`)

## Known Pitfalls

1. **Two login endpoints exist**: `/api/users/login/` (returns role) and `/api/login/` (Simple JWT default, no role). Frontend uses the first one.
2. **PC vs Equipment overlap**: `PC` and `Equipment` are separate models. PCs can have Software; Equipment covers all device types including PCs.
3. **Inventory model is vestigial**: `InventoryList` view calculates inventory dynamically from Equipment — the `Inventory` DB table is not used by the list endpoint.
4. **MaintenanceLog.save()** auto-assigns `lab` from `equipment.lab` — hidden side effect.
5. **No rate limiting** configured on any endpoint.
