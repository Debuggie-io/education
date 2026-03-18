import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"fieldname": "room", "label": _("Room"), "fieldtype": "Link", "options": "Room", "width": 150},
        {"fieldname": "room_number", "label": _("Room No"), "fieldtype": "Data", "width": 100},
        {"fieldname": "building", "label": _("Building"), "fieldtype": "Link", "options": "Building", "width": 120},
        {"fieldname": "capacity", "label": _("Capacity"), "fieldtype": "Int", "width": 80},
        {"fieldname": "total_slots", "label": _("Total Slots/Week"), "fieldtype": "Int", "width": 120},
        {"fieldname": "booked_slots", "label": _("Booked Slots"), "fieldtype": "Int", "width": 100},
        {"fieldname": "utilization_pct", "label": _("Utilization %"), "fieldtype": "Percent", "width": 100},
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
    if filters.get("building"):
        conditions += " AND r.building = %(building)s"
    if filters.get("timetable"):
        conditions += " AND te.timetable = %(timetable)s"
    
    slots_per_day = frappe.db.count("Time Slot", {"slot_type": "Regular", "is_active": 1}) or 11
    total_weekly_slots = slots_per_day * 5
    
    data = frappe.db.sql("""
        SELECT 
            r.name as room,
            r.room_number,
            r.building,
            r.seating_capacity as capacity,
            {total_slots} as total_slots,
            COUNT(te.name) as booked_slots,
            ROUND(COUNT(te.name) * 100.0 / {total_slots}, 1) as utilization_pct,
            SUM(CASE WHEN te.day = 'Monday' THEN 1 ELSE 0 END) as monday,
            SUM(CASE WHEN te.day = 'Tuesday' THEN 1 ELSE 0 END) as tuesday,
            SUM(CASE WHEN te.day = 'Wednesday' THEN 1 ELSE 0 END) as wednesday,
            SUM(CASE WHEN te.day = 'Thursday' THEN 1 ELSE 0 END) as thursday,
            SUM(CASE WHEN te.day = 'Friday' THEN 1 ELSE 0 END) as friday
        FROM `tabRoom` r
        LEFT JOIN `tabTimetable Entry` te ON r.name = te.room 
            AND te.status NOT IN ('Cancelled', 'Draft') {conditions}
        GROUP BY r.name, r.room_number, r.building, r.seating_capacity
        ORDER BY utilization_pct DESC
    """.format(total_slots=total_weekly_slots, conditions=conditions), filters, as_dict=1)
    
    return data

def get_chart(data):
    if not data:
        return None
    
    labels = [d.room_number or d.room for d in data[:15]]
    values = [d.utilization_pct or 0 for d in data[:15]]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": "Utilization %", "values": values}]
        },
        "type": "bar",
        "colors": ["#5e64ff"]
    }
