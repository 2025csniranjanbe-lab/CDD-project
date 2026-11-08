# AttendSync: Dockerized Attendance Management and Environment Reproducibility System

AttendSync is a modular, production-ready attendance management application designed for containerized deployment, high reproducibility, and streamlined team collaboration.

Built with **Python (Flask)**, **SQLite**, and **HTML5 / Bootstrap 5**.

---

## 📁 Project Directory Structure

```text
CDD_project/
├── app/
│   ├── __init__.py           # Application Factory (create_app) & CLI registration
│   ├── extensions.py         # SQLAlchemy instance & SQLite PRAGMA listeners
│   ├── models.py             # Core SQLAlchemy models (Student, AttendanceRecord)
│   ├── models/               # Modular model exports (MVC Model)
│   │   └── __init__.py       # Re-exports Student, AttendanceRecord, AttendanceStatus
│   ├── crud.py               # CRUD query utilities & business logic helpers
│   ├── commands.py           # Custom Flask CLI commands (flask init-db, flask seed-db)
│   ├── routes/               # Blueprints & controllers (MVC Controller)
│   │   ├── __init__.py
│   │   └── main.py           # Root ('/') and health check ('/health') routes
│   ├── static/               # Static assets
│   │   ├── css/
│   │   │   └── style.css     # Global custom styles
│   │   └── js/
│   │       └── main.js       # Client-side scripts
│   └── templates/            # Jinja2 presentation templates (MVC View)
│       ├── base.html         # Bootstrap 5 layout skeleton & navbar
│       ├── index.html        # Landing page & status dashboard
│       └── errors/
│           ├── 404.html      # 404 Not Found page
│           └── 500.html      # 500 Internal Server Error page
├── instance/                 # Ignored by git; stores persistent SQLite DB
├── tests/                    # Automated testing suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures and app factory config
│   ├── test_health.py        # Baseline health check unit tests
│   └── test_database.py      # Database models, constraints, CRUD & CLI tests
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions (pycache, .venv, sqlite db, .env)
├── config.py                 # 12-factor configuration (Dev, Test, Prod)
├── requirements.txt          # Pinned Python package dependencies
├── wsgi.py                   # Development runner & production WSGI entry point
└── README.md                 # Project documentation & setup instructions
```

---

## 🗄️ Phase 2: Database Schema & CLI Commands

### 1. Database Schema
- **`Student` (`students`)**:
  - `id`: Integer Primary Key (Autoincrement)
  - `usn`: Unique, indexed String(20) (e.g., `1MS21CS001`)
  - `name`: String(100)
  - `email`: Unique, indexed String(120)
  - `department`: String(80)
  - `semester`: Integer (1–8)
  - `section`: String(10) (e.g., 'A', 'B')
  - `attendance_records`: One-to-many relationship (`cascade="all, delete-orphan"`)
- **`AttendanceRecord` (`attendance_records`)**:
  - `id`: Integer Primary Key (Autoincrement)
  - `student_id`: Foreign Key (`students.id`, `ondelete="CASCADE"`)
  - `date`: `Date` object (defaults to current date)
  - `status`: String/Enum (`Present` / `Absent`)
  - **Constraint**: `uq_student_date` composite unique constraint on `(student_id, date)` preventing duplicate entries for a student on the same day.

### 2. Database CLI Commands

#### Initialize Database Tables:
```bash
flask init-db
```
*(Optional: Recreate tables from scratch with `flask init-db --drop`)*

#### Seed Realistic Sample Engineering Students & Attendance:
```bash
flask seed-db
```
This populates 8 realistic engineering students across departments (CSE, ISE, ECE, AIML, ME) and seeds initial attendance records across recent dates.

---

## 🛠️ CRUD Query Helper Utilities (`app/crud.py`)

The `app.crud` module provides high-performance, modular query functions:

```python
from datetime import date
from app.crud import (
    get_all_students_sorted,
    get_attendance_by_date,
    get_student_attendance_history,
    record_attendance,
    get_student_attendance_summary,
)

# 1. Fetch all students sorted alphabetically by USN
students = get_all_students_sorted()

# 2. Fetch all attendance records for a specific date (date object or 'YYYY-MM-DD')
records_today = get_attendance_by_date(date.today())

# 3. Fetch attendance history for a single student by USN (sorted newest first)
student, history = get_student_attendance_history("1MS21CS001")

# 4. Record or update attendance idempotently
record = record_attendance("1MS21CS001", date.today(), status="Present")

# 5. Get student metrics (total classes, present count, percentage)
summary = get_student_attendance_summary("1MS21CS001")
print(summary["attendance_percentage"])
```

---

## 🚀 Quickstart Local Environment Setup

### 1. Clone the Repository & Open Project Directory
```bash
git clone <repository-url>
cd CDD_project
```

### 2. Create and Activate Virtual Environment (.venv)

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt - CMD):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Initialize Database & Seed Sample Data
```bash
# Initialize SQLite tables
flask init-db

# Seed 8 sample students and attendance records
flask seed-db
```

---

### 5. Run the Application
```bash
python wsgi.py
```

Navigate to:
- **Dashboard:** [http://localhost:5000/](http://localhost:5000/)
- **Health Check API:** [http://localhost:5000/health](http://localhost:5000/health)

---

### 6. Run Automated Tests
```bash
pytest
```
Runs tests covering:
- Baseline health check routes
- Student creation and uniqueness checks
- Foreign key relations and cascade deletion
- Composite unique constraint `(student_id, date)`
- CRUD helper functions
- Flask CLI commands (`init-db` and `seed-db`)
