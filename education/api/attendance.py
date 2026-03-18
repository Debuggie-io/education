"""
Attendance Scanner API
"""

import frappe
from frappe import _
from frappe.utils import today, nowtime


@frappe.whitelist()
def lookup_student(scan_value):
    """Look up student by Student ID"""
    if not scan_value:
        return {"success": False, "message": "No scan value provided"}
    
    scan_value = scan_value.strip()
    
    if frappe.db.exists("Student", scan_value):
        student = frappe.get_doc("Student", scan_value)
        program = frappe.db.get_value("Program Enrollment",
            {"student": student.name, "docstatus": ["!=", 2]}, "program", order_by="creation desc")
        
        full_name = " ".join(filter(None, [student.first_name, student.middle_name, student.last_name]))
        
        return {
            "success": True,
            "student": {
                "name": student.name,
                "student_name": full_name or student.name,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "program": program,
                "image": student.image
            }
        }
    
    return {"success": False, "message": f"Student ID not found: {scan_value}"}


def get_student_hostel_room(student):
    """Get student's assigned hostel room"""
    room = frappe.db.sql("""
        SELECT hr.name, hr.hostel
        FROM `tabHostel Room` hr
        JOIN `tabHostel Room Occupant` hro ON hro.parent = hr.name
        WHERE hro.student = %s
        AND (hro.to_date IS NULL OR hro.to_date >= CURDATE())
        AND hro.from_date <= CURDATE()
        LIMIT 1
    """, student, as_dict=True)
    
    return room[0] if room else None


@frappe.whitelist()
def scan_and_save_attendance(scan_value, attendance_type, date, status, 
                              student_group=None, school_activity=None, 
                              meal_type=None, room_check_schedule=None):
    """Scan student ID and immediately save attendance"""
    
    if not scan_value:
        return {"success": False, "message": "No scan value provided"}
    
    scan_value = scan_value.strip()
    
    if not frappe.db.exists("Student", scan_value):
        return {"success": False, "message": f"Student not found: {scan_value}"}
    
    student = frappe.get_doc("Student", scan_value)
    program = frappe.db.get_value("Program Enrollment",
        {"student": student.name, "docstatus": ["!=", 2]}, "program", order_by="creation desc")
    
    full_name = " ".join(filter(None, [student.first_name, student.middle_name, student.last_name]))
    
    # Get hostel room for room check
    hostel_room = None
    if attendance_type == "Room Check":
        room_info = get_student_hostel_room(student.name)
        if room_info:
            hostel_room = room_info.name
        else:
            return {"success": False, "message": f"Student {full_name} is not assigned to any hostel room"}
    
    # Build filters for existing attendance
    filters = {
        "student": student.name,
        "date": date,
        "docstatus": ["!=", 2],
        "attendance_type": attendance_type
    }
    
    if attendance_type == "Class" and student_group:
        filters["student_group"] = student_group
    elif attendance_type == "School Activity" and school_activity:
        filters["school_activity"] = school_activity
    elif attendance_type == "Meals" and meal_type:
        filters["meal_type"] = meal_type
    elif attendance_type == "Room Check" and room_check_schedule:
        filters["room_check_schedule"] = room_check_schedule
    
    existing = frappe.db.get_value("Student Attendance", filters, "name")
    check_in_time = nowtime()
    
    if existing:
        return {
            "success": True,
            "message": "Already recorded",
            "student": {
                "name": student.name,
                "student_name": full_name,
                "program": program,
                "image": student.image
            },
            "check_in_time": check_in_time,
            "hostel_room": hostel_room,
            "already_exists": True
        }
    
    try:
        doc = frappe.get_doc({
            "doctype": "Student Attendance",
            "student": student.name,
            "date": date,
            "status": status,
            "attendance_type": attendance_type,
            "student_group": student_group if attendance_type == "Class" else None,
            "school_activity": school_activity if attendance_type == "School Activity" else None,
            "meal_type": meal_type if attendance_type == "Meals" else None,
            "room_check_schedule": room_check_schedule if attendance_type == "Room Check" else None,
            "hostel_room": hostel_room,
            "scanned_id": scan_value,
            "check_in_time": check_in_time
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update room check schedule counts
        if attendance_type == "Room Check" and room_check_schedule:
            update_room_check_counts(room_check_schedule)
        
        return {
            "success": True,
            "message": "Attendance saved",
            "student": {
                "name": student.name,
                "student_name": full_name,
                "program": program,
                "image": student.image
            },
            "check_in_time": check_in_time,
            "hostel_room": hostel_room,
            "attendance_id": doc.name
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}


def update_room_check_counts(room_check_schedule):
    """Update room check schedule attendance counts"""
    try:
        present = frappe.db.count("Student Attendance", {
            "room_check_schedule": room_check_schedule,
            "status": "Present",
            "docstatus": ["!=", 2]
        })
        total = frappe.db.count("Student Attendance", {
            "room_check_schedule": room_check_schedule,
            "docstatus": ["!=", 2]
        })
        
        frappe.db.set_value("Room Check Schedule", room_check_schedule, {
            "total_checked": total,
            "total_present": present,
            "status": "In Progress"
        })
    except:
        pass


@frappe.whitelist()
def get_attendance_list(date, attendance_type=None, student_group=None, 
                        school_activity=None, meal_type=None, room_check_schedule=None):
    """Get attendance list for a date/event"""
    
    filters = {"date": date, "docstatus": ["!=", 2]}
    
    if attendance_type:
        filters["attendance_type"] = attendance_type
    if student_group:
        filters["student_group"] = student_group
    if school_activity:
        filters["school_activity"] = school_activity
    if meal_type:
        filters["meal_type"] = meal_type
    if room_check_schedule:
        filters["room_check_schedule"] = room_check_schedule
    
    attendance = frappe.get_all("Student Attendance",
        filters=filters,
        fields=["name", "student", "student_name", "status", "check_in_time", "meal_type", "hostel_room"],
        order_by="check_in_time desc"
    )
    
    return attendance


@frappe.whitelist()
def get_students_for_id_cards(program=None, academic_year=None, student_group=None, student=None):
    """Get students for ID card generation"""
    
    if student:
        students = frappe.get_all("Student", filters={"name": student, "enabled": 1},
            fields=["name", "first_name", "middle_name", "last_name", "image", "student_email_id"])
    elif student_group:
        group_students = frappe.get_all("Student Group Student", filters={"parent": student_group}, fields=["student"])
        student_ids = [s.student for s in group_students]
        students = frappe.get_all("Student", filters={"name": ["in", student_ids], "enabled": 1},
            fields=["name", "first_name", "middle_name", "last_name", "image", "student_email_id"]) if student_ids else []
    elif program or academic_year:
        pe_filters = {"docstatus": ["!=", 2]}
        if program: pe_filters["program"] = program
        if academic_year: pe_filters["academic_year"] = academic_year
        enrollments = frappe.get_all("Program Enrollment", filters=pe_filters, fields=["student"], distinct=True)
        student_ids = [e.student for e in enrollments]
        students = frappe.get_all("Student", filters={"name": ["in", student_ids], "enabled": 1},
            fields=["name", "first_name", "middle_name", "last_name", "image", "student_email_id"], limit=50) if student_ids else []
    else:
        students = frappe.get_all("Student", filters={"enabled": 1},
            fields=["name", "first_name", "middle_name", "last_name", "image", "student_email_id"],
            order_by="creation desc", limit=20)
    
    result = []
    for s in students:
        full_name = " ".join(filter(None, [s.first_name, s.middle_name, s.last_name]))
        program = frappe.db.get_value("Program Enrollment", {"student": s.name, "docstatus": ["!=", 2]}, "program", order_by="creation desc")
        result.append({
            "name": s.name, "student_name": full_name or s.name, "first_name": s.first_name,
            "last_name": s.last_name, "email": s.student_email_id, "image": s.image, "program": program
        })
    
    return result
