# ResuAI - AI Resume Analyzer

ResuAI is a complete, production-ready Django web application designed to parse, analyze, and grade resume PDFs. It checks for ATS compliance using keyword detection, structure scanning, and section completeness metrics. It then provides users with job role alignment recommendations, corporate targets, and detailed improvement feedback.

---

> [!IMPORTANT]
> **Active Workspace Recommendation**
> This project has been fully initialized in the directory:  
> `C:\Users\ADMIN\.gemini\antigravity\scratch\resume_analyzer`  
> We strongly recommend setting **this subdirectory** as your active workspace in your IDE to ensure paths, local configuration files, and terminal run hooks align correctly.

---

## Technical Architecture

### 1. Database Schema

The application uses standard Django models mapped to either **SQLite** (for easy, zero-setup local dev) or **MySQL** (for production-grade persistence).

#### Model: `ResumeAnalysis`
| Field Name | Data Type | Purpose |
| :--- | :--- | :--- |
| `id` | BigAutoField (Primary Key) | Auto-incrementing identifier. |
| `user` | ForeignKey (`auth.User`) | Cascading relation linking each analysis to a specific user. |
| `resume_file` | FileField | Path on disk to the uploaded PDF (stored inside the `/media/resumes/` directory). |
| `filename` | CharField(255) | Name of the original uploaded file. |
| `extracted_text` | TextField | The raw string content extracted from the PDF. |
| `skills_found` | JSONField | Array of strings representing detected tech skills. |
| `ats_score` | IntegerField | Heuristic grading score from `0` to `100`. |
| `suggestions` | JSONField | List of improvement objects containing severity ('critical', 'warning', 'info') and advice. |
| `recommended_roles` | JSONField | List of recommended professional titles based on skills. |
| `recommended_companies` | JSONField | List of matched potential tech employers. |
| `created_at` | DateTimeField | Timestamp of when the file was processed. |

---

### 2. PyMySQL Hook for Windows Compatibility

Under Windows environments, installing `mysqlclient` often fails due to a lack of MSVC C++ compilation tools. To solve this, ResuAI implements a senior-level Python hook in `manage.py` and `resume_analyzer/__init__.py`:

```python
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```
This forces Django's default `mysql` engine to utilize `pymysql` as a drop-in replacement, avoiding native compilation issues entirely.

---

### 3. Parse & Score Mechanics

* **PDF Extraction**: Reads the byte stream of the uploaded resume using `pypdf`, merges all pages, and normalizes whitespaces.
* **Skill Taxonomy**: Employs optimized case-insensitive regex checks. Short skill names (e.g. `Go`, `C`, `R`) utilize word boundary anchors (`\b`) to prevent false matches in adjacent words.
* **ATS Score Calculation**:
  * **Section completeness (25%)**: Searches for standard sections: *Experience*, *Education*, *Skills*, *Projects*, and *Certifications*.
  * **Skill coverage (30%)**: Grades candidate based on total number of detected skills.
  * **Contact availability (25%)**: Assesses availability of email address, telephone number, and LinkedIn/GitHub profiles.
  * **Formatting & Word length (20%)**: Penalizes profiles that are either too brief (< 200 words) or too long (> 1000 words).

---

## Deployment & Setup Guide (Windows)

Follow these steps to run the application on your local machine:

### Step 1: Open a Terminal
Navigate to the project root directory:
```powershell
cd C:\Users\ADMIN\.gemini\antigravity\scratch\resume_analyzer
```

### Step 2: Set Up Virtual Environment
Create and activate a Python virtual environment to manage isolation:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Requirements
Install dependencies (including Django, PyMySQL, pypdf, and django-environ):
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database
1. By default, the app runs on **SQLite** with zero configurations (runs immediately).
2. To use **MySQL**:
   * Open your MySQL terminal or client (e.g. phpMyAdmin, DBeaver) and create a database:
     ```sql
     CREATE DATABASE resume_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
     ```
   * Open the `.env` file in the project root and make the following edits:
     ```ini
     # Toggle database type
     DB_TYPE=mysql

     # MySQL credentials
     DB_NAME=resume_analyzer
     DB_USER=root
     DB_PASSWORD=your_actual_mysql_password
     DB_HOST=127.0.0.1
     DB_PORT=3306
     ```

### Step 5: Execute Database Migrations
Create database schemas and tables:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Administrative Account
Create a Django superuser (optional, to access the admin portal at `/admin`):
```powershell
python manage.py createsuperuser
```

### Step 7: Verify via Automated Unit Tests
Run the automated testing suite to verify models, parser utilities, score metrics, and auth endpoints:
```powershell
python manage.py test
```

### Step 8: Start the Local Server
Launch the development server:
```powershell
python manage.py runserver
```
Once started, visit **`http://127.0.0.1:8000`** in your browser.

---

## User Interface & Features

* **Authentication Pages (`/login/`, `/register/`)**: Premium glassmorphic boxes with border glows and input focus transitions.
* **Dashboard (`/`)**: Displays average score charts, overall statistics, an active file drop-zone, and a table history of past analysis records.
* **Detailed Reports (`/analysis/<id>/`)**: Displays a radial score gauge, color-coded skill labels, detailed recommendation lists, actionable feedback, and an embedded debug console containing the raw parsed text.
