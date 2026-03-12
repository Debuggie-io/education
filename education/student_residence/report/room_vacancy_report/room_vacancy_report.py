# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"fieldname": "hostel", "label": _("Hostel"), "fieldtype": "Link", "options": "Hostel", "width": 180},
        {"fieldname": "room", "label": _("Room"), "fieldtype": "Link", "options": "Hostel Room", "width": 180},
        {"fieldname": "floor", "label": _("Floor"), "fieldtype": "Data", "width": 100},
        {"fieldname": "room_type", "label": _("Room Type"), "fieldtype": "Data", "width": 100},
        {"fieldname": "capacity", "label": _("Capacity"), "fieldtype": "Int", "width": 80},
        {"fieldname": "occupied", "label": _("Occupied"), "fieldtype": "Int", "width": 80},
        {"fieldname": "available", "label": _("Available"), "fieldtype": "Int", "width": 80},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    conditions = "WHERE r.is_available = 1"
    
    if filters.get("hostel"):
        conditions += f" AND r.hostel = '{filters.get('hostel')}'"
    
    if filters.get("hostel_type"):
        conditions += f" AND h.hostel_type = '{filters.get('hostel_type')}'"
    
    if filters.get("show_only_vacant"):
        conditions += " AND (r.room_capacity - r.occupied_beds) > 0"
    
    data = frappe.db.sql(f"""
        SELECT 
            r.hostel,
            r.name as room,
            r.floor,
            r.room_type,
            r.room_capacity as capacity,
            r.occupied_beds as occupied,
            (r.room_capacity - r.occupied_beds) as available,
            CASE 
                WHEN r.occupied_beds = 0 THEN 'Empty'
                WHEN r.occupied_beds < r.room_capacity THEN 'Partial'
                ELSE 'Full'
            END as status
        FROM `tabHostel Room` r
        JOIN `tabHostel` h ON r.hostel = h.name
        {conditions}
        ORDER BY r.hostel, r.room_number
    """, as_dict=True)
    
    return data
