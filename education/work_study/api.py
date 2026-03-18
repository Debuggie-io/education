# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, getdate, flt

@frappe.whitelist()
def get_open_positions(department=None, program=None):
    """Get all open work study positions for student portal"""
    filters = {
        "status": "Open",
        "published": 1
    }
    
    if department:
        filters["department"] = department
    
    positions = frappe.get_all("Work Study Position",
        filters=filters,
        fields=[
            "name", "position_title", "department", "description",
            "hourly_rate", "max_hours_per_week", "available_slots",
            "minimum_gpa", "application_start_date", "application_end_date",
            "requirements", "skills_needed"
        ]
    )
    
    # Filter by application period
    today_date = getdate(today())
    open_positions = []
    
    for pos in positions:
        if pos.application_start_date and getdate(pos.application_start_date) > today_date:
            continue
        if pos.application_end_date and getdate(pos.application_end_date) < today_date:
            continue
        if pos.available_slots <= 0:
            continue
        
        # Filter by program if specified
        if program:
            eligible_programs = frappe.get_all("Work Study Eligible Program",
                filters={"parent": pos.name},
                pluck="program"
            )
            if eligible_programs and program not in eligible_programs:
                continue
        
        open_positions.append(pos)
    
    return open_positions


@frappe.whitelist()
def get_student_applications(student=None):
    """Get all applications for a student"""
    if not student:
        student = get_current_student()
    
    if not student:
        frappe.throw(_("Student not found"))
    
    applications = frappe.get_all("Work Study Application",
        filters={"student": student},
        fields=[
            "name", "work_study_position", "status", "application_date",
            "is_eligible", "screening_notes", "current_gpa", "financial_need_score"
        ],
        order_by="creation desc"
    )
    
    for app in applications:
        app["position_title"] = frappe.db.get_value(
            "Work Study Position", app.work_study_position, "position_title"
        )
    
    return applications


@frappe.whitelist()
def get_student_assignment(student=None):
    """Get active work study assignment for a student"""
    if not student:
        student = get_current_student()
    
    if not student:
        return None
    
    assignment = frappe.db.get_value("Work Study Assignment",
        {"student": student, "status": "Active"},
        ["name", "work_study_position", "start_date", "hourly_rate",
         "max_hours_per_week", "total_hours_worked", "total_earnings",
         "total_wallet_credits", "supervisor", "department"],
        as_dict=True
    )
    
    if assignment:
        assignment["position_title"] = frappe.db.get_value(
            "Work Study Position", assignment.work_study_position, "position_title"
        )
        assignment["supervisor_name"] = frappe.db.get_value(
            "Employee", assignment.supervisor, "employee_name"
        )
    
    return assignment


@frappe.whitelist()
def submit_work_study_application(position, cover_letter, available_hours, 
                                   relevant_experience=None, preferred_schedule=None):
    """Submit a new work study application from student portal"""
    student = get_current_student()
    
    if not student:
        frappe.throw(_("You must be a registered student to apply"))
    
    # Check if position is accepting applications
    position_doc = frappe.get_doc("Work Study Position", position)
    if not position_doc.is_application_open():
        frappe.throw(_("This position is not accepting applications"))
    
    # Check for existing application
    existing = frappe.db.exists("Work Study Application", {
        "student": student,
        "work_study_position": position,
        "status": ["not in", ["Rejected", "Withdrawn", "Screening Failed", "Appeal Rejected"]]
    })
    
    if existing:
        frappe.throw(_("You have already applied for this position"))
    
    # Create application
    app = frappe.new_doc("Work Study Application")
    app.student = student
    app.work_study_position = position
    app.cover_letter = cover_letter
    app.available_hours = available_hours
    app.relevant_experience = relevant_experience
    app.preferred_schedule = preferred_schedule
    app.save()
    app.submit()
    
    return {
        "name": app.name,
        "status": app.status,
        "is_eligible": app.is_eligible,
        "screening_notes": app.screening_notes
    }


@frappe.whitelist()
def get_student_timesheets(student=None, status=None):
    """Get timesheets for a student"""
    if not student:
        student = get_current_student()
    
    if not student:
        return []
    
    filters = {"student": student}
    if status:
        filters["status"] = status
    
    timesheets = frappe.get_all("Work Study Timesheet",
        filters=filters,
        fields=[
            "name", "week_start_date", "week_end_date", "status",
            "total_hours", "total_amount", "work_study_position"
        ],
        order_by="week_start_date desc"
    )
    
    return timesheets


@frappe.whitelist()
def create_timesheet_entry(assignment, week_start_date, week_end_date, time_logs):
    """Create a new timesheet from student portal"""
    import json
    
    student = get_current_student()
    
    if not student:
        frappe.throw(_("Student not found"))
    
    # Verify assignment belongs to student
    assignment_doc = frappe.get_doc("Work Study Assignment", assignment)
    if assignment_doc.student != student:
        frappe.throw(_("Invalid assignment"))
    
    if assignment_doc.status != "Active":
        frappe.throw(_("Assignment is not active"))
    
    # Parse time_logs if string
    if isinstance(time_logs, str):
        time_logs = json.loads(time_logs)
    
    # Create timesheet
    ts = frappe.new_doc("Work Study Timesheet")
    ts.work_study_assignment = assignment
    ts.week_start_date = week_start_date
    ts.week_end_date = week_end_date
    
    for log in time_logs:
        ts.append("time_logs", {
            "date": log.get("date"),
            "start_time": log.get("start_time"),
            "end_time": log.get("end_time"),
            "task_description": log.get("task_description"),
            "notes": log.get("notes")
        })
    
    ts.save()
    
    return {
        "name": ts.name,
        "total_hours": ts.total_hours,
        "total_amount": ts.total_amount
    }


@frappe.whitelist()
def submit_timesheet(timesheet):
    """Submit a timesheet for approval"""
    student = get_current_student()
    
    ts = frappe.get_doc("Work Study Timesheet", timesheet)
    
    if ts.student != student:
        frappe.throw(_("Invalid timesheet"))
    
    if ts.docstatus != 0:
        frappe.throw(_("Timesheet already submitted"))
    
    ts.submit()
    
    return {"status": ts.status}


@frappe.whitelist()
def get_student_wallet_balance(student=None):
    """Get student's wallet balance"""
    if not student:
        student = get_current_student()
    
    if not student:
        return {"balance": 0}
    
    # Get wallet account from active assignment
    wallet_account = frappe.db.get_value("Work Study Assignment",
        {"student": student, "status": "Active"},
        "wallet_account"
    )
    
    if not wallet_account:
        return {"balance": 0, "wallet_account": None}
    
    # Get balance from GL Entry
    balance = frappe.db.sql("""
        SELECT SUM(credit - debit) as balance
        FROM `tabGL Entry`
        WHERE account = %s
        AND is_cancelled = 0
    """, wallet_account)[0][0] or 0
    
    return {
        "balance": flt(balance, 2),
        "wallet_account": wallet_account
    }


@frappe.whitelist()
def get_work_study_dashboard(student=None):
    """Get complete work study dashboard data for student"""
    if not student:
        student = get_current_student()
    
    if not student:
        return None
    
    dashboard = {
        "assignment": get_student_assignment(student),
        "applications": get_student_applications(student),
        "recent_timesheets": get_student_timesheets(student)[:5],
        "wallet": get_student_wallet_balance(student),
        "open_positions": get_open_positions() if not get_student_assignment(student) else []
    }
    
    return dashboard


def get_current_student():
    """Get the student linked to current user"""
    if frappe.session.user == "Guest":
        return None
    
    student = frappe.db.get_value("Student",
        {"student_email_id": frappe.session.user},
        "name"
    )
    
    if not student:
        # Try user email
        student = frappe.db.get_value("Student",
            {"user": frappe.session.user},
            "name"
        )
    
    return student


@frappe.whitelist()
def check_eligibility(student, position):
    """Pre-check student eligibility for a position"""
    position_doc = frappe.get_doc("Work Study Position", position)
    student_doc = frappe.get_doc("Student", student)
    
    result = {
        "eligible": True,
        "checks": []
    }
    
    # GPA Check
    gpa = frappe.db.get_value("Student", student, "custom_gpa") or 0
    min_gpa = position_doc.minimum_gpa or 2.0
    gpa_ok = flt(gpa) >= min_gpa
    result["checks"].append({
        "name": "GPA",
        "passed": gpa_ok,
        "current": gpa,
        "required": min_gpa
    })
    if not gpa_ok:
        result["eligible"] = False
    
    # Program Check
    eligible_programs = [ep.program for ep in position_doc.eligible_programs]
    if eligible_programs:
        enrollment = frappe.db.get_value("Program Enrollment",
            {"student": student, "docstatus": 1},
            "program",
            order_by="creation desc"
        )
        program_ok = enrollment in eligible_programs
        result["checks"].append({
            "name": "Program",
            "passed": program_ok,
            "current": enrollment,
            "required": ", ".join(eligible_programs)
        })
        if not program_ok:
            result["eligible"] = False
    
    return result
