"""
Timetable API for UEAB
"""

import frappe
from frappe import _
from frappe.utils import today


@frappe.whitelist()
def get_my_timetable(academic_term=None, student=None, instructor=None):
    """Get timetable for current user or specified student/instructor"""
    user = frappe.session.user
    
    user_type = None
    user_name = None
    user_doc = None
    program = None
    
    # Check if user is an instructor (via Employee link)
    instructor_data = frappe.db.sql("""
        SELECT i.name, i.instructor_name, i.department
        FROM `tabInstructor` i
        JOIN `tabEmployee` e ON i.employee = e.name
        WHERE e.user_id = %s
        LIMIT 1
    """, user, as_dict=True)
    
    if instructor_data:
        user_type = "Instructor"
        user_doc = frappe._dict(instructor_data[0])
        user_name = user_doc.instructor_name or user_doc.name
    
    # Check if user is a student
    if not user_type:
        student_name = frappe.db.get_value("Student", {"user": user}, "name")
        
        if student_name:
            user_type = "Student"
            user_doc = frappe.get_doc("Student", student_name)
            user_name = getattr(user_doc, 'student_name', None) or getattr(user_doc, 'first_name', None) or user_doc.name
            
            # Get student's program from Program Enrollment
            program = frappe.db.get_value("Program Enrollment",
                {"student": student_name, "docstatus": ["!=", 2]},
                "program",
                order_by="creation desc"
            )
    
    # Check if admin
    if not user_type:
        user_roles = frappe.get_roles(user)
        if "System Manager" in user_roles or "Education Manager" in user_roles or "Academics User" in user_roles:
            user_type = "Admin"
            user_name = frappe.db.get_value("User", user, "full_name") or user
        else:
            return {
                "success": False,
                "message": "No student or instructor record linked to your user account. Please contact the administrator.",
                "entries": [],
                "time_slots": []
            }
    
    # Get current academic term if not specified
    if not academic_term:
        academic_term = get_current_academic_term()
    
    # Get timetable entries
    entries = get_timetable_entries(academic_term, user_type, user_doc, program)
    
    # Get time slots
    time_slots = frappe.get_all("Time Slot",
        filters={"is_active": 1},
        fields=["name", "start_time", "end_time", "slot_type"],
        order_by="start_time"
    )
    
    return {
        "success": True,
        "user_type": user_type,
        "user_name": user_name,
        "program": program,
        "academic_term": academic_term,
        "entries": entries,
        "time_slots": time_slots,
        "total_hours": calculate_total_hours(entries),
        "courses_count": len(set(e.get("course") for e in entries))
    }


def get_current_academic_term():
    """Get current academic term based on today's date"""
    current_date = today()
    
    # First try to find term where today is within the date range
    term = frappe.db.get_value("Academic Term",
        filters={
            "term_start_date": ["<=", current_date],
            "term_end_date": [">=", current_date]
        },
        fieldname="name"
    )
    
    if term:
        return term
    
    # If no current term, find the most recent past term
    past_term = frappe.db.get_value("Academic Term",
        filters={"term_end_date": ["<", current_date]},
        fieldname="name",
        order_by="term_end_date desc"
    )
    
    if past_term:
        return past_term
    
    # Fallback to any term
    return frappe.db.get_value("Academic Term", {}, "name", order_by="term_start_date desc")


def get_timetable_entries(academic_term, user_type, user_doc, program=None):
    """Get timetable entries based on user type"""
    filters = {"academic_term": academic_term}
    
    # Add status filter if field exists
    try:
        filters["status"] = ["!=", "Cancelled"]
    except:
        pass
    
    if user_type == "Instructor" and user_doc:
        filters["instructor"] = user_doc.name
    elif user_type == "Student" and user_doc:
        enrolled_courses = get_student_courses(user_doc.name)
        if enrolled_courses:
            filters["course"] = ["in", enrolled_courses]
        elif program:
            program_courses = get_program_courses(program)
            if program_courses:
                filters["course"] = ["in", program_courses]
            else:
                return []
        else:
            return []
    elif user_type == "Admin":
        # Admin sees limited entries
        pass
    else:
        return []
    
    try:
        entries = frappe.get_all("Timetable Entry",
            filters=filters,
            fields=[
                "name", "course", "day", "time_slot", "start_time", "end_time",
                "room", "instructor", "class_type", "is_lab_session",
                "duration_minutes", "notes"
            ],
            order_by="day, start_time",
            limit=200
        )
    except Exception as e:
        frappe.log_error(f"Error fetching timetable entries: {e}")
        entries = []
    
    # Enrich entries with related data
    for entry in entries:
        try:
            course_data = frappe.db.get_value("Course", entry.course,
                ["course_name", "course_code"], as_dict=True)
            if course_data:
                entry["course_name"] = course_data.course_name
                entry["course_code"] = course_data.course_code
        except:
            pass
        
        try:
            if entry.room:
                room_data = frappe.db.get_value("Room", entry.room,
                    ["room_number", "building"], as_dict=True)
                if room_data:
                    entry["room_number"] = room_data.room_number
                    entry["building"] = room_data.building
        except:
            pass
        
        try:
            if entry.instructor:
                entry["instructor_name"] = frappe.db.get_value("Instructor",
                    entry.instructor, "instructor_name")
        except:
            pass
    
    return entries


def get_student_courses(student_name):
    """Get courses a student is enrolled in"""
    enrollments = frappe.get_all("Course Enrollment",
        filters={"student": student_name},
        pluck="course"
    )
    
    if enrollments:
        return enrollments
    
    # Fallback: get from program enrollment
    program = frappe.db.get_value("Program Enrollment",
        filters={"student": student_name, "docstatus": ["!=", 2]},
        fieldname="program"
    )
    
    if program:
        return get_program_courses(program)
    
    return []


def get_program_courses(program):
    """Get all courses in a program"""
    if not program:
        return []
    
    courses = frappe.get_all("Program Course",
        filters={"parent": program},
        pluck="course"
    )
    
    return courses


def calculate_total_hours(entries):
    """Calculate total hours from entries"""
    total_minutes = 0
    for entry in entries:
        duration = entry.get("duration_minutes")
        if duration:
            try:
                total_minutes += int(duration)
            except:
                total_minutes += 60
        else:
            total_minutes += 60
    
    return round(total_minutes / 60, 1)


@frappe.whitelist()
def get_room_schedule(room, academic_term=None):
    """Get schedule for a specific room"""
    if not academic_term:
        academic_term = get_current_academic_term()
    
    return frappe.get_all("Timetable Entry",
        filters={"room": room, "academic_term": academic_term},
        fields=["name", "course", "day", "start_time", "end_time", "instructor"],
        order_by="day, start_time"
    )


@frappe.whitelist()
def get_instructor_schedule(instructor, academic_term=None):
    """Get schedule for a specific instructor"""
    if not academic_term:
        academic_term = get_current_academic_term()
    
    return frappe.get_all("Timetable Entry",
        filters={"instructor": instructor, "academic_term": academic_term},
        fields=["name", "course", "day", "start_time", "end_time", "room"],
        order_by="day, start_time"
    )
