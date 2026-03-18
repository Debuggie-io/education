import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    return columns, data, summary

def get_columns():
    return [
        {"fieldname": "conflict_type", "label": _("Conflict Type"), "fieldtype": "Data", "width": 150},
        {"fieldname": "day", "label": _("Day"), "fieldtype": "Data", "width": 100},
        {"fieldname": "time_slot", "label": _("Time Slot"), "fieldtype": "Data", "width": 120},
        {"fieldname": "resource", "label": _("Resource"), "fieldtype": "Data", "width": 150},
        {"fieldname": "entry1", "label": _("Entry 1"), "fieldtype": "Link", "options": "Timetable Entry", "width": 120},
        {"fieldname": "course1", "label": _("Course 1"), "fieldtype": "Data", "width": 150},
        {"fieldname": "entry2", "label": _("Entry 2"), "fieldtype": "Link", "options": "Timetable Entry", "width": 120},
        {"fieldname": "course2", "label": _("Course 2"), "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    conflicts = []
    
    term_condition = ""
    if filters.get("academic_term"):
        term_condition = "AND te1.academic_term = %(academic_term)s"
    if filters.get("timetable"):
        term_condition += " AND te1.timetable = %(timetable)s"
    
    # Room conflicts
    room_conflicts = frappe.db.sql("""
        SELECT 
            te1.name as entry1, te1.course as course1,
            te2.name as entry2, te2.course as course2,
            te1.day, te1.time_slot, te1.room as resource
        FROM `tabTimetable Entry` te1
        JOIN `tabTimetable Entry` te2 ON 
            te1.room = te2.room AND 
            te1.day = te2.day AND 
            te1.time_slot = te2.time_slot AND
            te1.name < te2.name AND
            te1.status NOT IN ('Cancelled', 'Draft') AND
            te2.status NOT IN ('Cancelled', 'Draft')
        WHERE 1=1 {term_condition}
    """.format(term_condition=term_condition), filters, as_dict=1)
    
    for c in room_conflicts:
        conflicts.append({
            "conflict_type": "Room Double-Booked",
            "day": c.day,
            "time_slot": c.time_slot,
            "resource": c.resource,
            "entry1": c.entry1,
            "course1": c.course1,
            "entry2": c.entry2,
            "course2": c.course2
        })
    
    # Instructor conflicts
    instructor_conflicts = frappe.db.sql("""
        SELECT 
            te1.name as entry1, te1.course as course1,
            te2.name as entry2, te2.course as course2,
            te1.day, te1.time_slot, i.instructor_name as resource
        FROM `tabTimetable Entry` te1
        JOIN `tabTimetable Entry` te2 ON 
            te1.instructor = te2.instructor AND 
            te1.day = te2.day AND 
            te1.time_slot = te2.time_slot AND
            te1.name < te2.name AND
            te1.status NOT IN ('Cancelled', 'Draft') AND
            te2.status NOT IN ('Cancelled', 'Draft')
        LEFT JOIN `tabInstructor` i ON te1.instructor = i.name
        WHERE 1=1 {term_condition}
    """.format(term_condition=term_condition), filters, as_dict=1)
    
    for c in instructor_conflicts:
        conflicts.append({
            "conflict_type": "Instructor Double-Booked",
            "day": c.day,
            "time_slot": c.time_slot,
            "resource": c.resource,
            "entry1": c.entry1,
            "course1": c.course1,
            "entry2": c.entry2,
            "course2": c.course2
        })
    
    return conflicts

def get_summary(data):
    room_conflicts = len([d for d in data if d["conflict_type"] == "Room Double-Booked"])
    instructor_conflicts = len([d for d in data if d["conflict_type"] == "Instructor Double-Booked"])
    
    return [
        {"label": _("Room Conflicts"), "value": room_conflicts, "indicator": "Red" if room_conflicts else "Green"},
        {"label": _("Instructor Conflicts"), "value": instructor_conflicts, "indicator": "Red" if instructor_conflicts else "Green"},
        {"label": _("Total Conflicts"), "value": len(data), "indicator": "Red" if data else "Green"}
    ]
