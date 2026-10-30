# Online Learning Management System (LMS)

A full-stack learning platform built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**.

## Features

- **Secure Authentication** – Register / Login with hashed passwords (Werkzeug)
- **Role-based Access Control**
  - **Admin** – manage users & roles
  - **Instructor** – create/edit courses & quizzes, view student attempts
  - **Student** – enroll in courses, take quizzes, view scores
- **Course Management** – create, edit, publish, delete courses
- **Quiz System**
  - Multiple-choice questions (A/B/C/D)
  - Automatic evaluation & percentage scoring
  - Pass/fail based on configurable threshold
  - Detailed result review with correct answers
  - Attempt history for instructors
- **RESTful-style backend modules** (Flask blueprints)
- **SQLite** database with SQLAlchemy ORM

## Tech Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Backend     | Python 3, Flask 3       |
| ORM         | Flask-SQLAlchemy        |
| Auth        | Flask-Login + Werkzeug  |
| Database    | SQLite                  |
| Frontend    | HTML5, CSS3, Vanilla JS |

## Quick Start

```bash
# 1. Clone / enter project
cd lms_project

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

### Default Admin Account
- **Username:** `admin`
- **Password:** `admin123`

## Project Structure

```
lms_project/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # User, Course, Quiz, Question, Attempt, Enrollment
│   ├── routes/
│   │   ├── auth.py          # Login / Register / Logout
│   │   ├── main.py          # Home + role-based dashboards
│   │   ├── courses.py       # Course CRUD + enrollment
│   │   ├── quizzes.py       # Quiz creation, taking, evaluation
│   │   └── admin.py         # User management
│   ├── templates/           # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── instance/                # SQLite DB lives here (auto-created)
├── run.py                   # Entry point
├── requirements.txt
└── README.md
```

## Typical Workflow

1. **Admin** logs in → manages users (promote to instructor if needed)
2. **Instructor** registers / is promoted → creates a Course → adds Quizzes + Questions
3. **Student** registers → enrolls in a course → takes quizzes → views score & review

## Git

```bash
git init
git add .
git commit -m "Initial commit: Online Learning Management System"
# Then add your remote and push
git remote add origin <your-repo-url>
git push -u origin main
```

## License

MIT – feel free to use and modify.
