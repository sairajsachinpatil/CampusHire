from flask import Flask, render_template, request, redirect, flash, url_for
from database import db, User, Drive, Application
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

#login
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)


app = Flask(__name__)


#resume location config
app.config["UPLOAD_FOLDER"] = (
    "static/uploads/resumes"
)


#setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = "placement_portal_secret"


#database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# INITIALIZE DATABASE
db.init_app(app)


#loader
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )



# =========================================
# Home Route to index.html
# =========================================
@app.route("/")
def home():
    return render_template("index.html")



# =========================================
# sign up
# =========================================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already exists")

            return redirect("/signup")

        hashed_password = generate_password_hash(
            password
        )

        new_user = User(

            fullname=fullname,

            email=email,

            password=hashed_password,

            role="student"

        )

        db.session.add(new_user)

        db.session.commit()

        flash("Account Created Successfully")

        return redirect("/login")

    return render_template(
        "auth/signup.html",
        show_navbar=False
    )
    



# =========================================
# LOGIN
# =========================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()


        # VERIFY PASSWORD

        if user and check_password_hash(

            user.password,

            password

        ):


            # BLACKLIST CHECK

            if user.is_blacklisted:

                if user.role == "company":

                    flash(

                        "Your Company Has Been Blacklisted. Contact Admin: admin@gmail.com"

                    )

                else:

                    flash(

                        "Your Account Has Been Blacklisted. ||" \
                        " Contact Admin : admin@gmail.com"

                    )

                return redirect("/login")


            # COMPANY APPROVAL CHECK

            if user.role == "company" and not user.is_approved:

                flash(

                    "Company Awaiting Approval"

                )

                return redirect("/login")


            # LOGIN USER

            login_user(user)


            # ROLE REDIRECTS

            if user.role == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )


            elif user.role == "company":

                return redirect(
                    url_for("company_dashboard")
                )


            else:

                if not user.is_profile_completed:

                    return redirect(
                        url_for("complete_profile")
                    )

                return redirect(
                    url_for("student_dashboard")
                )


        else:

            flash("Invalid Email or Password")

            return redirect("/login")


    return render_template(

        "auth/login.html",

        show_navbar=False

    )




# =========================================
# Student Dashboard
# =========================================

#STUDENT-COMPLETE PROFILE
@app.route(
    "/complete-profile",
    methods=["GET", "POST"]
)

@login_required
def complete_profile():

    # ONLY STUDENT CAN ACCESS

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    # IF ALREADY COMPLETED

    if current_user.is_profile_completed:

        return redirect(
            url_for("student_dashboard")
        )


    if request.method == "POST":

        current_user.phone = request.form["phone"]

        current_user.prn = request.form["prn"]

        current_user.department = request.form["department"]

        current_user.year = request.form["year"]

        current_user.cgpa = request.form["cgpa"]

        current_user.skills = request.form["skills"]


    
        # RESUME FILE

        resume = request.files["resume"]

        if resume and resume.filename != "":

            filename = secure_filename(
                resume.filename
            )

            save_path = os.path.join(

                app.config["UPLOAD_FOLDER"],

                filename

            )

            resume.save(save_path)

            current_user.resume = filename


        current_user.is_profile_completed = True

        db.session.commit()

        flash(
            "Profile Completed Successfully"
        )

        return redirect(
            url_for("student_dashboard")
        )

    return render_template(
        "student/complete_profile.html"
    )
#STUDENT- dashboard page route 
@app.route("/student/dashboard")
@login_required
def student_dashboard():

    # ONLY STUDENT ACCESS

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    # PROFILE CHECK

    if not current_user.is_profile_completed:

        return redirect(
            url_for("complete_profile")
        )


    # GET STUDENT APPLICATIONS

    applications = Application.query.filter_by(

        student_id=current_user.id

    ).all()


    # STATS

    total_applications = len(
        applications
    )

    selected = len([

        application

        for application in applications

        if application.status == "Selected"

    ])


    rejected = len([

        application

        for application in applications

        if application.status == "Rejected"

    ])


    shortlisted = len([

        application

        for application in applications

        if application.status == "Shortlisted"

    ])


    return render_template(

        "student/student_dashboard.html",

        student=current_user,

        applications=applications,

        total_applications=total_applications,

        shortlisted=shortlisted,

        selected=selected,

        rejected=rejected,


    )

#STUDENT- my_profile view and update route
@app.route(
    "/my-profile",
    methods=["GET", "POST"]
)

@login_required
def my_profile():

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    if request.method == "POST":

        current_user.phone = request.form["phone"]

        current_user.department = request.form["department"]

        current_user.cgpa = request.form["cgpa"]

        current_user.skills = request.form["skills"]

        # RESUME
        resume = request.files["resume"]

        if resume and resume.filename != "":

            filename = secure_filename(
                resume.filename
            )

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            resume.save(save_path)

            current_user.resume = filename

       

        db.session.commit()

        flash("Profile Updated Successfully")

        return redirect("/my-profile")


    return render_template(

        "student/my_profile.html",

        student=current_user

    )

#STUDENT-issue-queries route
@app.route("/issues-queries")
@login_required
def issues_queries():

    # ONLY STUDENT ACCESS

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")

    return render_template(
        "student/issues_queries.html"
    )
#STUDENT- available drives for apply route
@app.route("/available-drives")
@login_required
def available_drives():

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    drives = Drive.query.filter_by(

        admin_status="Approved",

        drive_status="Active"

    ).all()


    # STORE APPLIED DRIVE IDS

    applied_drive_ids = []


    applications = Application.query.filter_by(

        student_id=current_user.id

    ).all()


    for application in applications:

        applied_drive_ids.append(

            application.drive_id

        )


    return render_template(

        "student/available_drives.html",

        drives=drives,

        applied_drive_ids=applied_drive_ids

    )
#STUDENT-apply to drive/placement
@app.route("/apply-drive/<int:drive_id>")
@login_required
def apply_drive(drive_id):

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    # CHECK ALREADY APPLIED

    existing_application = Application.query.filter_by(

        student_id=current_user.id,

        drive_id=drive_id

    ).first()


    if existing_application:

        flash("Already Applied")

        return redirect("/available-drives")


    # NEW APPLICATION

    new_application = Application(

        student_id=current_user.id,

        drive_id=drive_id

    )

    db.session.add(new_application)

    db.session.commit()

    flash("Applied Successfully")

    return redirect("/available-drives")
#STUDENT- my-applications history
@app.route("/my-applications")
@login_required
def my_applications():

    # ONLY STUDENT ACCESS

    if current_user.role != "student":

        flash("Access Denied")

        return redirect("/login")


    applications = Application.query.filter_by(

        student_id=current_user.id

    ).all()


    return render_template(

        "student/my_applications.html",

        applications=applications

    )






# =========================================
# Company Dashboard
# =========================================
#COMPANY-signup route
@app.route("/company/register", methods=["GET", "POST"])
def company_register():

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already exists")

            return redirect("/company/register")

        hashed_password = generate_password_hash(
            password
        )

        new_company = User(

            fullname=fullname,

            email=email,

            password=hashed_password,

            role="company",

            is_approved=False

        )

        db.session.add(new_company)

        db.session.commit()

        flash(
            "Company Registration Submitted"
        )

        return redirect("/login")

    return render_template(
        "auth/company_register.html"
    )
#COMPANY- dashboard page route
@app.route("/company/dashboard")
@login_required
def company_dashboard():

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    # COMPANY DRIVES

    company_drives = Drive.query.filter_by(

        company_id=current_user.id

    ).all()


    # TOTAL DRIVES

    total_drives = len(company_drives)


    # INITIALIZE VARIABLES

    total_applicants = 0

    shortlisted = 0

    selected = 0


    # LOOP THROUGH ALL DRIVES

    for drive in company_drives:

        applications = Application.query.filter_by(

            drive_id=drive.id

        ).all()


        # TOTAL APPLICANTS

        total_applicants += len(applications)


        # SHORTLISTED COUNT

        shortlisted += Application.query.filter_by(

            drive_id=drive.id,

            status="Shortlisted"

        ).count()


        # SELECTED COUNT

        selected += Application.query.filter_by(

            drive_id=drive.id,

            status="Selected"

        ).count()


    return render_template(

        "company/company_dashboard.html",

        total_drives=total_drives,

        total_applicants=total_applicants,

        shortlisted=shortlisted,

        selected=selected

    )
#COMPANY- profile route
@app.route(
    "/company-profile",
    methods=["GET", "POST"]
)

@login_required
def company_profile():

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    if request.method == "POST":

        # COMPANY DETAILS

        current_user.fullname = request.form[
            "company_name"
        ]

        current_user.website = request.form[
            "website"
        ]

        current_user.hr_name = request.form[
            "hr_name"
        ]

        current_user.hr_contact = request.form[
            "hr_contact"
        ]

        current_user.industry = request.form[
            "industry"
        ]

        current_user.description = request.form[
            "description"
        ]


        # SAVE DATABASE

        db.session.commit()

        flash(
            "Company Profile Updated Successfully"
        )

        return redirect(
            "/company-profile"
        )


    return render_template(

        "company/company_profile.html",

        company=current_user

    )
#COMPANY- issues-support route
@app.route("/company-support")
@login_required
def company_support():

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    return render_template(
        "company/issues_support.html"
    )

#COMPANY - create-drive
@app.route(
    "/create-drive",
    methods=["GET", "POST"]
)

@login_required
def create_drive():

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    if request.method == "POST":

        new_drive = Drive(

            company_id=current_user.id,

            company_name=current_user.fullname,

            job_role=request.form["job_role"],

            package=request.form["package"],

            location=request.form["location"],

            eligibility=request.form["eligibility"],

            skills=request.form["skills"],

            deadline=request.form["deadline"],

            description=request.form["description"]

        )

        db.session.add(new_drive)

        db.session.commit()

        flash("Placement Drive Created Successfully")

        return redirect("/company/dashboard")


    return render_template(
        "company/create_drive.html"
    )

#COMPANY-manage drive
@app.route("/manage-drives")
@login_required
def manage_drives():

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    drives = Drive.query.filter_by(

        company_id=current_user.id

    ).all()


    return render_template(

        "company/manage_drives.html",

        drives=drives

    )


#COMPANY- view-applications from manage drive route
@app.route("/view-applications/<int:drive_id>")
@login_required
def view_applications(drive_id):

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    # GET DRIVE

    drive = Drive.query.get_or_404(
        drive_id
    )


    # ONLY OWNER COMPANY CAN VIEW

    if drive.company_id != current_user.id:

        flash("Unauthorized Access")

        return redirect("/company/dashboard")


    # APPLICATIONS

    applications = Application.query.filter_by(

        drive_id=drive_id

    ).all()


    # STATS

    total_applications = len(applications)

    shortlisted = len([
        a for a in applications
        if a.status == "Shortlisted"
    ])

    selected = len([
        a for a in applications
        if a.status == "Selected"
    ])

    rejected = len([
        a for a in applications
        if a.status == "Rejected"
    ])

    pending = len([
        a for a in applications
        if a.status == "Pending"
    ])


    return render_template(

        "company/view_applications.html",

        drive=drive,

        applications=applications,

        total_applications=total_applications,

        shortlisted=shortlisted,

        selected=selected,

        rejected=rejected,

        pending=pending

    )
#COMPANY -update status of student application
@app.route(
    "/update-application-status/<int:application_id>/<status>"
)

@login_required
def update_application_status(

    application_id,
    status

):

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    application = Application.query.get_or_404(
        application_id
    )


    # VALID STATUSES ONLY

    allowed_status = [

        "Pending",

        "Shortlisted",

        "Selected",

        "Rejected"

    ]


    if status not in allowed_status:

        flash("Invalid Status")

        return redirect(request.referrer)


    # UPDATE STATUS

    application.status = status

    db.session.commit()

    flash("Application Status Updated")


    return redirect(request.referrer)

#COMPANY -edit drive option in manage drive
@app.route(
    "/edit-drive/<int:id>",
    methods=["GET", "POST"]
)

@login_required
def edit_drive(id):

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    drive = Drive.query.get_or_404(id)


    # SECURITY

    if drive.company_id != current_user.id:

        flash("Unauthorized Access")

        return redirect("/manage-drives")


    if request.method == "POST":

        drive.job_role = request.form[
            "job_role"
        ]

        drive.package = request.form[
            "package"
        ]

        drive.location = request.form[
            "location"
        ]

        drive.eligibility = request.form[
            "eligibility"
        ]

        drive.skills = request.form[
            "skills"
        ]

        drive.deadline = request.form[
            "deadline"
        ]

        drive.description = request.form[
            "description"
        ]


        # AGAIN PENDING

        drive.admin_status = "Pending"


        db.session.commit()

        flash("Drive Updated Successfully")

        return redirect("/manage-drives")


    return render_template(

        "company/create_drive.html",

        drive=drive,

        edit_mode=True

    )
#COMPANY -close drive option in manage drive
@app.route("/close-drive/<int:id>")
@login_required
def close_drive(id):

    # ONLY COMPANY ACCESS

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    drive = Drive.query.get_or_404(id)


    # SECURITY CHECK

    if drive.company_id != current_user.id:

        flash("Unauthorized Access")

        return redirect("/company/dashboard")


    # CLOSE DRIVE

    drive.drive_status = "Closed"

    db.session.commit()

    flash("Drive Closed Successfully")

    return redirect("/manage-drives")
#COMPANY -remove drive actions in manage drive
@app.route("/remove-drive/<int:id>")
@login_required
def delete_drive(id):

    if current_user.role != "company":

        flash("Access Denied")

        return redirect("/login")


    drive = Drive.query.get_or_404(id)


    # SECURITY

    if drive.company_id != current_user.id:

        flash("Unauthorized Access")

        return redirect("/manage-drives")


    # DELETE APPLICATIONS

    applications = Application.query.filter_by(

        drive_id=drive.id

    ).all()


    for application in applications:

        db.session.delete(application)


    db.session.delete(drive)

    db.session.commit()

    flash("Drive Removed Successfully")

    return redirect("/manage-drives")






# =========================================
# Admin Dashboard
# =========================================
#ADMIN- dashboard page route
@app.route("/admin/dashboard")

@login_required

def admin_dashboard():

    # TOTAL STUDENTS

    total_students = User.query.filter_by(
        role="student"
    ).count()


    # TOTAL COMPANIES

    total_companies = User.query.filter_by(
        role="company"
    ).count()


    # SELECTED STUDENTS
    selected_students = db.session.query(
        Application.student_id
    ).filter(
        Application.status == "Selected"
    ).distinct().count()

  

    # UNSELECTED STUDENTS

    unselected_students = (
        total_students - selected_students
    )


    # PLACEMENT PERCENTAGE

    if total_students > 0:

        placement_percentage = round(

            (selected_students / total_students) * 100,

            2

        )

    else:

        placement_percentage = 0


    # HIGHEST PACKAGE

    highest_package = db.session.query(

        func.max(Drive.package)

    ).scalar() or 0


    # LOWEST PACKAGE

    lowest_package = db.session.query(

        func.min(Drive.package)

    ).scalar() or 0


    # AVERAGE PACKAGE

    average_package = db.session.query(

        func.avg(Drive.package)

    ).scalar() or 0

    average_package = round(
        average_package,
        2
    )


    return render_template(

        "admin/admin_dashboard.html",

        total_students=total_students,

        total_companies=total_companies,

        selected_students=selected_students,

        unselected_students=unselected_students,

        placement_percentage=placement_percentage,

        highest_package=highest_package,

        lowest_package=lowest_package,

        average_package=average_package

    )
#ADMIN -all companies and pending companies
@app.route("/admin/manage-companies")
@login_required
def manage_companies():

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    # GET ALL COMPANIES

    companies = User.query.filter_by(

        role="company"

    ).all()


    return render_template(

        "admin/manage_companies.html",

        companies=companies

    )
#ADMIN -drive request approval(drive_approval_request.html) to admin route
@app.route("/admin/manage-drive")
@login_required
def drive_requests():

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    drives = Drive.query.all()


    return render_template(

        "admin/drive_approval_requests.html",

        drives=drives

    )
#if admin APPROVE DRIVE of company
@app.route("/approve-drive/<int:id>")
@login_required
def approve_drive(id):

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    drive = Drive.query.get_or_404(id)

    drive.admin_status = "Approved"

    db.session.commit()

    flash("Drive Approved Successfully")

    return redirect("/admin/manage-drive")
#if admin reject drive of company
@app.route("/reject-drive/<int:id>")
@login_required
def reject_drive(id):

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    drive = Drive.query.get_or_404(id)

    drive.admin_status = "Rejected"

    db.session.commit()

    flash("Drive Rejected")

    return redirect("/admin/manage-drive")

#ADMIN-approve company route
@app.route("/approve-company/<int:id>")
@login_required
def approve_company(id):

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    company = User.query.get_or_404(id)

    # APPROVE COMPANY

    company.is_approved = True

    # REMOVE BLACKLIST IF EXISTS

    company.is_blacklisted = False

    # ADD THIS — reopen all drives when company is approved
    drives = Drive.query.filter_by(company_id=company.id).all()

    db.session.commit()

    flash("Company Approved Successfully")

    return redirect("/admin/manage-companies")

#ADMIN-reject company
@app.route("/reject-company/<int:id>")
@login_required
def reject_company(id):

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    company = User.query.get_or_404(id)

    # REJECT

    company.is_approved = False

    db.session.commit()

    flash("Company Rejected")

    return redirect("/admin/manage-companies")

#ADMIN-blacklist company
@app.route("/blacklist-company/<int:id>")
@login_required
def blacklist_company(id):

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    company = User.query.get_or_404(id)

    # BLACKLIST COMPANY

    company.is_blacklisted = True

    company.is_approved = False


    # REJECT/CLOSE ALL DRIVES

    drives = Drive.query.filter_by(

        company_id=company.id

    ).all()


    for drive in drives:

        drive.admin_status = "Rejected"



    db.session.commit()

    flash("Company Blacklisted Successfully")

    return redirect("/admin/manage-companies")
#ADMIN -un-blaclist company
@app.route("/unblacklist-company/<int:id>")
@login_required
def unblacklist_company(id):

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    company = User.query.get_or_404(id)

    # REMOVE BLACKLIST

    company.is_blacklisted = False

    db.session.commit()

    flash("Company Removed From Blacklist")

    return redirect("/admin/manage-companies")
#ADMIN -manage students
@app.route("/admin/manage-students")
@login_required
def manage_students():

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    # GET SEARCH VALUE

    search = request.args.get(
        "search"
    )


    # IF SEARCH EXISTS

    if search:

        students = User.query.filter(

            User.role == "student",

            (

                User.fullname.ilike(
                    f"%{search}%"
                )

            ) |

            (

                User.prn.ilike(
                    f"%{search}%"
                )

            )

        ).all()

    else:

        students = User.query.filter_by(

            role="student"

        ).all()


    return render_template(

        "admin/manage_students.html",

        students=students

    )
#ADMIN -blacklist students route
@app.route("/blacklist-student/<int:id>")
@login_required
def blacklist_student(id):

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    student = User.query.get_or_404(id)

    student.is_blacklisted = True

    db.session.commit()

    flash("Student Blacklisted")

    return redirect("/admin/manage-students")
#ADMIN -unblacklist students route
@app.route("/unblacklist-student/<int:id>")
@login_required
def unblacklist_student(id):

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    student = User.query.get_or_404(id)

    student.is_blacklisted = False

    db.session.commit()

    flash("Student Removed From Blacklist")

    return redirect("/admin/manage-students")
#ADMIN -manage applications
@app.route("/admin/manage-applications")
@login_required
def manage_applications():

    # ONLY ADMIN ACCESS

    if current_user.role != "admin":

        flash("Access Denied")

        return redirect("/login")


    # SEARCH VALUE

    search = request.args.get(
        "search",
        ""
    )


    # ALL APPLICATIONS

    applications = Application.query.all()


    # SEARCH FILTER

    if search:

        filtered_applications = []


        for application in applications:

            student_name = (
                application.student.fullname or ""
            ).lower()

            prn = (
                application.student.prn or ""
            ).lower()

            company_name = (
                application.drive.company_name or ""
            ).lower()


            if (

                search.lower() in student_name

                or

                search.lower() in prn

                or

                search.lower() in company_name

            ):

                filtered_applications.append(
                    application
                )


        applications = filtered_applications


    return render_template(

        "admin/manage_applications.html",

        applications=applications

    )




#logout
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully")

    return redirect("/login")



# RUN APP
if __name__ == "__main__":
    with app.app_context():

        db.create_all()

        existing_admin = User.query.filter_by(
            email="admin@gmail.com"
        ).first()

        if not existing_admin:

            admin = User(

                fullname="Admin",

                email="admin@gmail.com",

                password=generate_password_hash(
                    "admin123"
                ),

                role="admin",

                is_approved=True

            )

            db.session.add(admin)

            db.session.commit()

            print("Admin Created")

    app.run(debug=True)