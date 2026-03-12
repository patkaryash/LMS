# Step-by-Step Setup Guide for LMS

This guide walks you through setting up the LMS project from scratch, including backend and frontend dependencies, git initialization, migrations, and user setup.

Prerequisites
- Python 3.9+
- Node.js + npm (for frontend)
- Git

1) Clone the repository
```
git clone https://github.com/Shantanukpro/LMS.git
cd LMS
```

2) Virtual environment
- Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
- macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3) Backend dependencies
- If requirements.txt exists:
```bash
pip install -r requirements.txt
```
- If not, install Django & DRF manually and later generate requirements.txt:
```bash
pip install django djangorestframework
```
- Freeze dependencies:
```bash
pip freeze > requirements.txt
```

4) Frontend dependencies (if a frontend exists)
- Navigate to frontend directory:
```bash
cd frontend
```
- Install and build:
```bash
npm install
npm run build   # production build
npm start       # development server (optional)
```

5) Git initialization (if not done yet) & first push
- Initialize git (only if not a git repo yet):
```bash
git init
git add .
git commit -m "Initial project skeleton"
```
- Add remote and push (replace with your repo URL):
```bash
git branch -M main
git remote add origin <REPO_URL>
git push -u origin main
```

6) Django migrations & admin
- Change to backend/LMS (project root for Django):
```bash
cd backend/LMS
```
- Create migrations and apply
```bash
python manage.py makemigrations
python manage.py migrate
```
- Create superuser
```bash
python manage.py createsuperuser
```

7) Run servers
- Backend (Django):
```bash
python manage.py runserver 8000
```
- Frontend (if exists):
```bash
cd frontend
npm start
```

8) Verification
- Admin: http://127.0.0.1:8000/admin
- API: http://127.0.0.1:8000/api/  (adjust per your router)

9) Optional: Docker
- If you plan to dockerize, prepare Dockerfile and docker-compose.yml and adjust environment vars.

10) Troubleshooting tips
- Ensure venv is activated before installing packages.
- If migrations fail, re-run makemigrations and migrate.
- Check port availability if runserver cannot start.

When you’re ready, replace placeholder repo URLs and adjust commands to match your exact folder structure.
