# LMS – Lab Management System

A Django-based Lab Management System to manage labs, PCs, and lab equipment in educational environments. This repository contains a Django project located at `backend/LMS` with apps such as `labs`, `users`, `tickets`, and more. A `frontend/` directory is present for optional UI work.

## Badges
- [Python 3.9+](https://www.python.org/) Fresh install recommended
- [Django](https://www.djangoproject.com/) web framework
- MIT license (adjust if needed)

---

## Overview
- Manage labs, PCs, and LabEquipment (with detailed subtables for equipment metadata)
- REST API powered by Django REST Framework
- Admin panel for quick data management
- Importer for bulk CSV/XLSX uploads
- Local development friendly with a virtual environment

---

## Project Layout (current repo)
- Root contains:
  - backend/LMS/  Django project (manage.py at backend/LMS/manage.py; settings at backend/LMS/LMS/settings.py)
  - labs/        Django app module (models for Lab, PC, LabEquipment, etc.)
  - frontend/     Optional frontend UI
  - requirements.txt  Dependencies for the project (run in a venv)

Notes:
- You can verify structure by inspecting: `backend/LMS/` (manage.py, apps) and `backend/LMS/LMS/` (settings, urls).

---

## Prerequisites
- Python 3.9+
- pip
- Git
- Optional: Node.js if you plan to work with the frontend in `frontend/`.

- Check versions (example):
  - `python --version`
  - `pip --version`
  - `git --version`

---

## Installation & Setup
From the repository root (where this README lives):

1) Clone the repo (if you haven't already)
   git clone https://github.com/Shantanukpro/LMS.git
   cd LMS

2) Create and activate a virtual environment
   Windows:
   - python -m venv venv
   - venv\Scripts\activate
   
   macOS/Linux:
   - python3 -m venv venv
   - source venv/bin/activate

3) Install dependencies
   If you have requirements.txt at the repo root:
   - pip install -r requirements.txt
   If not, install Django and DRF manually:
   - pip install django djangorestframework
   
   Optional: freeze deps after install
   - pip freeze > requirements.txt

4) Django project setup & run
   Navigate into the Django project root (where manage.py exists):
   - cd backend/LMS

   Migrate & create admin:
   - python manage.py makemigrations
   - python manage.py migrate
   - python manage.py createsuperuser

   Run the development server:
   - python manage.py runserver 8000

Open in browser:
- Admin: http://127.0.0.1:8000/admin
- API root (adjust to your endpoints): http://127.0.0.1:8000/api/

---

## Local Development & Directory Structure
- Entry point: `backend/LMS/manage.py`
- Django project package: `backend/LMS/LMS/` (settings, urls, wsgi)
- Core apps: `labs/`, `users/`, `tickets/`, etc. under `backend/LMS/`.
- Optional frontend: `frontend/`.

---

## Data Model Snapshot (high level)
- Lab: physical lab metadata
- PC: computers and hardware specs
- LabEquipment: main equipment registry with subtables
- Subtables: `NetworkEquipmentDetails`, `ServerDetails`, `ProjectorDetails`, `ElectricalApplianceDetails`
- MaintenanceLog: records maintenance actions against targets (PC, LabEquipment, Peripheral)

For detailed models, see `backend/LMS/labs/models.py`.

---

## Importer (Bulk Import)
- Import labs, PCs, and LabEquipment from CSV/XLSX via `backend/LMS/labs/importers.py`.
- Handles edge cases and common data issues; run tests or use Django shell to validate data.

---

## Testing
- Run tests: `python manage.py test`
- Tests live in the apps' `tests.py` files (e.g., `labs/tests.py`).

---
## Troubleshooting
- Common issues:
  - Virtual environment activation problems
  - Pending migrations after model changes
  - Port conflicts when running the dev server
- Quick fixes:
  - `python manage.py makemigrations` && `python manage.py migrate`
  - If port 8000 is in use: `python manage.py runserver 8001`
- If Django isn't found in a fresh env, ensure the virtualenv is activated and dependencies are installed.

---
## Contributing
- PRs are welcome. Open an issue to discuss major changes before starting.

---
## Full Setup Guide
For a comprehensive, step-by-step setup, see the dedicated guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)

## License
- MIT (adjust as needed)

If you want me to tailor this README precisely to your repo structure (manage.py location and app names), I can generate a fully customized README.md next.
