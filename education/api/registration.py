"""
Student Registration API
"""

import frappe
from frappe import _
from frappe.utils import today, getdate, now_datetime


@frappe.whitelist()
def get_registration_status():
    """Get current student's registration status"""
    user = frappe.session.user
    
    # Get student record
    student = frappe.db.get_value("Student", {"user": user}, 
        ["name", "first_name", "last_name", "student_email_id"], as_dict=True)
    
    if not student:
        return {"student": None, "message": "No student record found"}
    
    student_name = f"{student.first_name or ''} {student.last_name or ''}".strip()
    
    # Get program enrollment
    enrollment = frappe.db.get_value("Program Enrollment",
        {"student": student.name, "docstatus": ["!=", 2]},
        ["name", "program", "academic_year"],
        as_dict=True,
        order_by="creation desc"
    )
    
    program = enrollment.program if enrollment else None
    
    # Check for active registration period
    current_date = getdate(today())
    
    period = frappe.db.get_value("Registration Period",
        filters={
            "is_active": 1,
            "start_date": ["<=", current_date],
            "end_date": [">=", current_date]
        },
        fieldname=["name", "academic_year", "academic_term", "start_date", "end_date", 
                   "max_credits", "min_credits"],
        as_dict=True
    )
    
    # Also check late registration
    if not period:
        period = frappe.db.get_value("Registration Period",
            filters={
                "is_active": 1,
                "allow_late_registration": 1,
                "end_date": ["<", current_date],
                "late_registration_end": [">=", current_date]
            },
            fieldname=["name", "academic_year", "academic_term", "start_date", "end_date",
                       "max_credits", "min_credits", "late_fee"],
            as_dict=True
        )
        if period:
            period["is_late"] = True
    
    if not period:
        return {
            "student": student.name,
            "student_name": student_name,
            "program": program,
            "registration_open": False,
            "message": "Registration is not currently open"
        }
    
    # Check for existing registration
    existing = frappe.db.get_value("Semester Registration",
        filters={
            "student": student.name,
            "academic_term": period.academic_term,
            "docstatus": ["!=", 2]
        },
        fieldname="name"
    )
    
    registration = None
    if existing:
        registration = frappe.get_doc("Semester Registration", existing).as_dict()
        registration["courses"] = frappe.get_all("Semester Registration Course",
            filters={"parent": existing},
            fields=["*"]
        )
    
    return {
        "student": student.name,
        "student_name": student_name,
        "email": student.student_email_id,
        "program": program,
        "program_enrollment": enrollment.name if enrollment else None,
        "registration_open": True,
        "academic_year": period.academic_year,
        "academic_term": period.academic_term,
        "period_start": str(period.start_date),
        "period_end": str(period.end_date),
        "max_credits": period.max_credits or 21,
        "min_credits": period.min_credits or 12,
        "is_late": period.get("is_late", False),
        "late_fee": period.get("late_fee", 0),
        "registration": registration
    }


@frappe.whitelist()
def get_available_courses(student, program, academic_term):
    """Get courses available for registration"""
    # Get program courses
    program_courses = frappe.get_all("Program Course",
        filters={"parent": program},
        fields=["course", "required"]
    )
    
    courses = []
    for pc in program_courses:
        course = frappe.db.get_value("Course", pc.course, 
            ["name", "course_name", "course_code", "credit_hours", "department"], as_dict=True)
        
        if not course:
            continue
        
        # Get schedule info
        schedule = get_course_schedule(pc.course, academic_term)
        
        courses.append({
            "course": course.name,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "credit_hours": course.credit_hours or 3,
            "is_mandatory": pc.required,
            "department": course.department,
            "schedule": schedule
        })
    
    return courses


def get_course_schedule(course, academic_term):
    """Get timetable entries for a course"""
    entries = frappe.get_all("Timetable Entry",
        filters={
            "course": course,
            "academic_term": academic_term
        },
        fields=["day", "start_time", "end_time", "room", "instructor"]
    )
    
    if not entries:
        return "Schedule TBA"
    
    schedule_parts = []
    for e in entries:
        room_name = e.room or ""
        if e.room:
            room_name = frappe.db.get_value("Room", e.room, "room_number") or e.room
        
        time_str = format_time(e.start_time) + "-" + format_time(e.end_time)
        schedule_parts.append(f"{e.day[:3]}: {time_str} @ {room_name}")
    
    return "; ".join(schedule_parts)


def format_time(t):
    if not t:
        return ""
    parts = str(t).split(":")
    h = int(parts[0]) if parts else 0
    m = parts[1] if len(parts) > 1 else "00"
    ap = "PM" if h >= 12 else "AM"
    h = h % 12 or 12
    return f"{h}:{m}{ap}"


@frappe.whitelist()
def create_registration(academic_term, courses):
    """Create new semester registration"""
    import json
    
    user = frappe.session.user
    student = frappe.db.get_value("Student", {"user": user}, "name")
    
    if not student:
        return {"success": False, "message": "No student record found"}
    
    if isinstance(courses, str):
        courses = json.loads(courses)
    
    # Get program enrollment
    enrollment = frappe.db.get_value("Program Enrollment",
        {"student": student, "docstatus": ["!=", 2]},
        ["name", "program", "academic_year"],
        as_dict=True,
        order_by="creation desc"
    )
    
    if not enrollment:
        return {"success": False, "message": "No program enrollment found"}
    
    # Get academic year from term
    academic_year = frappe.db.get_value("Academic Term", academic_term, "academic_year")
    
    # Check if registration already exists
    existing = frappe.db.exists("Semester Registration", {
        "student": student,
        "academic_term": academic_term,
        "docstatus": ["!=", 2]
    })
    
    if existing:
        return {"success": False, "message": "Registration already exists for this term"}
    
    # Create registration
    reg = frappe.get_doc({
        "doctype": "Semester Registration",
        "student": student,
        "program": enrollment.program,
        "program_enrollment": enrollment.name,
        "academic_year": academic_year,
        "academic_term": academic_term,
        "registration_date": today(),
        "registration_status": "Draft"
    })
    
    # Add courses
    for course_name in courses:
        course_data = frappe.db.get_value("Course", course_name,
            ["name", "course_name", "course_code", "credit_hours"], as_dict=True)
        
        if course_data:
            schedule = get_course_schedule(course_name, academic_term)
            
            reg.append("courses", {
                "course": course_name,
                "course_name": course_data.course_name,
                "course_code": course_data.course_code,
                "credit_hours": course_data.credit_hours or 3,
                "schedule_info": schedule
            })
    
    # Calculate totals
    reg.total_courses = len(reg.courses)
    reg.total_credits = sum(c.credit_hours or 0 for c in reg.courses)
    
    reg.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {"success": True, "registration": reg.name, "message": "Registration created successfully"}


@frappe.whitelist()
def submit_for_approval(registration_name):
    """Submit registration for finance approval"""
    doc = frappe.get_doc("Semester Registration", registration_name)
    
    if doc.registration_status != "Draft":
        return {"success": False, "message": "Registration already submitted"}
    
    doc.registration_status = "Pending Finance Approval"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {"success": True, "message": "Registration submitted for Finance approval"}


@frappe.whitelist()
def approve_registration(registration_name, approval_type, remarks=""):
    """Approve registration at different levels"""
    doc = frappe.get_doc("Semester Registration", registration_name)
    user = frappe.session.user
    now = now_datetime()
    
    if approval_type == "finance":
        doc.finance_status = "Approved"
        doc.finance_approved_by = user
        doc.finance_approval_date = now
        doc.finance_remarks = remarks
        doc.registration_status = "Pending HOD Approval"
        
    elif approval_type == "hod":
        doc.hod_status = "Approved"
        doc.hod_approved_by = user
        doc.hod_approval_date = now
        doc.hod_remarks = remarks
        doc.registration_status = "Pending Registrar Approval"
        
    elif approval_type == "registrar":
        doc.registrar_status = "Approved"
        doc.registrar_approved_by = user
        doc.registrar_approval_date = now
        doc.registrar_remarks = remarks
        doc.registration_status = "Approved"
        doc.is_registered = 1
    
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {"success": True, "message": f"{approval_type.title()} approval complete"}


@frappe.whitelist()
def reject_registration(registration_name, approval_type, remarks=""):
    """Reject registration"""
    doc = frappe.get_doc("Semester Registration", registration_name)
    user = frappe.session.user
    now = now_datetime()
    
    if approval_type == "finance":
        doc.finance_status = "Rejected"
        doc.finance_approved_by = user
        doc.finance_approval_date = now
        doc.finance_remarks = remarks
    elif approval_type == "hod":
        doc.hod_status = "Rejected"
        doc.hod_approved_by = user
        doc.hod_approval_date = now
        doc.hod_remarks = remarks
    elif approval_type == "registrar":
        doc.registrar_status = "Rejected"
        doc.registrar_approved_by = user
        doc.registrar_approval_date = now
        doc.registrar_remarks = remarks
    
    doc.registration_status = "Rejected"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {"success": True, "message": "Registration rejected"}
