import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "course", "label": _("Course"), "fieldtype": "Link", "options": "Course", "width": 180},
        {"fieldname": "course_code", "label": _("Code"), "fieldtype": "Data", "width": 80},
        {"fieldname": "instructor_name", "label": _("Instructor"), "fieldtype": "Data", "width": 150},
        {"fieldname": "day", "label": _("Day"), "fieldtype": "Data", "width": 100},
        {"fieldname": "time", "label": _("Time"), "fieldtype": "Data", "width": 120},
        {"fieldname": "room", "label": _("Room"), "fieldtype": "Link", "options": "Room", "width": 120},
        {"fieldname": "building", "label": _("Building"), "fieldtype": "Data", "width": 120},
        {"fieldname": "class_type", "label": _("Type"), "fieldtype": "Data", "width": 100},
        {"fieldname": "expected_students", "label": _("Students"), "fieldtype": "Int", "width": 80},
    ]

def get_data(filters):
    conditions = "WHERE te.status NOT IN ('Cancelled', 'Draft')"
    
    if filters.get("academic_term"):
        conditions += " AND te.academic_term = %(academic_term)s"
    if filters.get("timetable"):
        conditions += " AND te.timetable = %(timetable)s"
    if filters.get("course"):
        conditions += " AND te.course = %(course)s"
    if filters.get("instructor"):
        conditions += " AND te.instructor = %(instructor)s"
    if filters.get("department"):
        conditions += " AND c.department = %(department)s"
    if filters.get("day"):
        conditions += " AND te.day = %(day)s"
    
    data = frappe.db.sql("""
        SELECT 
            te.course,
            c.course_code,
            i.instructor_name,
            te.day,
            CONCAT(TIME_FORMAT(te.start_time, '%%H:%%i'), ' - ', TIME_FORMAT(te.end_time, '%%H:%%i')) as time,
            te.room,
            r.building,
            te.class_type,
            te.expected_students
        FROM `tabTimetable Entry` te
        LEFT JOIN `tabCourse` c ON te.course = c.name
        LEFT JOIN `tabInstructor` i ON te.instructor = i.name
        LEFT JOIN `tabRoom` r ON te.room = r.name
        {conditions}
        ORDER BY 
            FIELD(te.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
            te.start_time,
            c.course_code
    """.format(conditions=conditions), filters, as_dict=1)
    
    return data
