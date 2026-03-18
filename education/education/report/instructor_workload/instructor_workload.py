import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"fieldname": "instructor", "label": _("Instructor"), "fieldtype": "Link", "options": "Instructor", "width": 150},
        {"fieldname": "instructor_name", "label": _("Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "department", "label": _("Department"), "fieldtype": "Link", "options": "Department", "width": 150},
        {"fieldname": "total_classes", "label": _("Total Classes/Week"), "fieldtype": "Int", "width": 130},
        {"fieldname": "total_hours", "label": _("Total Hours/Week"), "fieldtype": "Float", "width": 120},
        {"fieldname": "courses_taught", "label": _("Courses"), "fieldtype": "Int", "width": 80},
        {"fieldname": "monday", "label": _("Mon"), "fieldtype": "Int", "width": 60},
        {"fieldname": "tuesday", "label": _("Tue"), "fieldtype": "Int", "width": 60},
        {"fieldname": "wednesday", "label": _("Wed"), "fieldtype": "Int", "width": 60},
        {"fieldname": "thursday", "label": _("Thu"), "fieldtype": "Int", "width": 60},
        {"fieldname": "friday", "label": _("Fri"), "fieldtype": "Int", "width": 60},
    ]

def get_data(filters):
    conditions = ""
    if filters.get("academic_term"):
        conditions += " AND te.academic_term = %(academic_term)s"
    if filters.get("department"):
        conditions += " AND i.department = %(department)s"
    if filters.get("timetable"):
        conditions += " AND te.timetable = %(timetable)s"
    
    data = frappe.db.sql("""
        SELECT 
            i.name as instructor,
            i.instructor_name,
            i.department,
            COUNT(te.name) as total_classes,
            ROUND(SUM(IFNULL(te.duration_minutes, 60)) / 60.0, 1) as total_hours,
            COUNT(DISTINCT te.course) as courses_taught,
            SUM(CASE WHEN te.day = 'Monday' THEN 1 ELSE 0 END) as monday,
            SUM(CASE WHEN te.day = 'Tuesday' THEN 1 ELSE 0 END) as tuesday,
            SUM(CASE WHEN te.day = 'Wednesday' THEN 1 ELSE 0 END) as wednesday,
            SUM(CASE WHEN te.day = 'Thursday' THEN 1 ELSE 0 END) as thursday,
            SUM(CASE WHEN te.day = 'Friday' THEN 1 ELSE 0 END) as friday
        FROM `tabInstructor` i
        LEFT JOIN `tabTimetable Entry` te ON i.name = te.instructor 
            AND te.status NOT IN ('Cancelled', 'Draft') {conditions}
        GROUP BY i.name, i.instructor_name, i.department
        HAVING total_classes > 0
        ORDER BY total_hours DESC
    """.format(conditions=conditions), filters, as_dict=1)
    
    return data

def get_chart(data):
    if not data:
        return None
    
    labels = [d.instructor_name or d.instructor for d in data[:10]]
    values = [d.total_hours or 0 for d in data[:10]]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Hours/Week", "values": values}]
        },
        "type": "bar",
        "colors": ["#36a2eb"]
    }
