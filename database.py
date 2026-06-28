from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# INITIALIZE DATABASE

db = SQLAlchemy()


# USER MODEL

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    fullname = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_approved = db.Column(
        db.Boolean,
        default=False
    )

    is_blacklisted = db.Column(
        db.Boolean,
        default=False
    )

    phone = db.Column(
        db.String(20)
    )

    prn = db.Column(
        db.String(50)
    )

    department = db.Column(
        db.String(100)
    )

    year = db.Column(
        db.String(50)
    )

    cgpa = db.Column(
        db.Float
    )

    skills = db.Column(
        db.Text
    )

    resume = db.Column(
        db.String(200)
    )

    is_profile_completed = db.Column(
        db.Boolean,
        default=False
    )

    # COMPANY PROFILE

    website = db.Column(
        db.String(200)
    )

    hr_name = db.Column(
        db.String(100)
    )

    hr_contact = db.Column(
        db.String(20)
    )

    industry = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )


# DRIVE MODEL

class Drive(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    company_name = db.Column(
        db.String(200)
    )

    job_role = db.Column(
        db.String(200)
    )

    package = db.Column(
        db.Float
    )

    location = db.Column(
        db.String(200)
    )

    eligibility = db.Column(
        db.String(100)
    )

    skills = db.Column(
        db.Text
    )

    deadline = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )

    admin_status = db.Column(
        db.String(50),
        default="Pending"
    )
    drive_status = db.Column(
        db.String(50),
        default="Active"
    )


# APPLICATION MODEL

class Application(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("drive.id")
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    student = db.relationship(
        "User",
        backref="applications"
    )

    drive = db.relationship(
        "Drive",
        backref="applications"
    )
    