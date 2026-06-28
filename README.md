# CampusHire
CampusHire is a centralized, full-stack campus placement and recruitment platform that streamlines placement drives, application tracking, and hiring workflows through secure role-based access for students, companies, and administrators.

## Features

### Student Module

* Student Registration and Login
* Profile Completion and Management
* Resume Upload
* View Available Placement Drives
* Apply for Placement Drives
* Track Application Status
* View Application History

### Company Module

* Company Registration
* Company Profile Management
* Create Placement Drives
* Manage Placement Drives
* View Student Applications
* Shortlist, Select, or Reject Candidates

### Admin Module

* Manage Students
* Manage Companies
* Approve or Reject Companies
* Blacklist or Unblacklist Companies
* Approve or Reject Placement Drives
* Manage Applications
* View Placement Statistics

  * Total Students
  * Total Companies
  * Selected Students
  * Unselected Students
  * Placement Percentage
  * Highest Package
  * Lowest Package
  * Average Package

---

## Technology Stack

### Backend

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy

### Database

* SQLite

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* Jinja2 Templates

---

## Database Design

### User Table

Stores:

* Admin Accounts
* Student Accounts
* Company Accounts

### Drive Table

Stores:

* Placement Drive Information
* Company Details
* Package Details
* Eligibility Criteria

### Application Table

Acts as a bridge table between Students and Placement Drives and stores:

* Applied Student
* Drive Applied For
* Application Status

---

## Project Structure

```text
CampusHire/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── instance/
│   └── database.db
│
├── static/
│   └── uploads/
│       └── resumes/
│
└── templates/
    ├── admin/
    ├── auth/
    ├── company/
    └── student/
```

---

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Application

```bash
python app.py
```

### Step 3: Open Browser

```text
http://127.0.0.1:5000
```

---

## Security Features

* Password Hashing using Werkzeug
* Role-Based Access Control
* Company Approval System
* Student and Company Blacklisting
* Login Authentication using Flask-Login
* Duplicate Application Prevention

---

## Future Enhancements

* Email Notifications
* Interview Scheduling
* Analytics Dashboard
* Online Assessment Integration
* Resume Screening using AI
* Company Performance Reports

---

 
