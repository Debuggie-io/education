# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    
    return columns, data, None, chart

def get_columns():
    return [
        {"fieldname": "hostel", "label": _("Hostel"), "fieldtype": "Link", "options": "Hostel", "width": 200},
        {"fieldname": "hostel_type", "label": _("Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "total_rooms", "label": _("Total Rooms"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_capacity", "label": _("Total Beds"), "fieldtype": "Int", "width": 100},
        {"fieldname": "occupied_beds", "label": _("Occupied"), "fieldtype": "Int", "width": 100},
        {"fieldname": "available_beds", "label": _("Available"), "fieldtype": "Int", "width": 100},
        {"fieldname": "occupancy_rate", "label": _("Occupancy %"), "fieldtype": "Percent", "width": 120},
    ]

def get_data(filters):
    conditions = ""
    if filters.get("hostel_type"):
        conditions += f" AND h.hostel_type = '{filters.get('hostel_type')}'"
    
    data = frappe.db.sql(f"""
        SELECT 
            h.name as hostel,
            h.hostel_type,
            h.total_rooms,
            h.total_capacity,
            h.occupied_beds,
            (h.total_capacity - h.occupied_beds) as available_beds,
            ROUND((h.occupied_beds / NULLIF(h.total_capacity, 0)) * 100, 2) as occupancy_rate
        FROM `tabHostel` h
        WHERE h.is_active = 1 {conditions}
        ORDER BY h.hostel_type, h.name
    """, as_dict=True)
    
    return data

def get_chart(data):
    labels = [d.hostel for d in data]
    occupied = [d.occupied_beds for d in data]
    available = [d.available_beds for d in data]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Occupied", "values": occupied},
                {"name": "Available", "values": available}
            ]
        },
        "type": "bar",
        "colors": ["#FC4F51", "#36A2EB"]
    }
