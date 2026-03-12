# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, getdate

def get_context(context):
    context.no_cache = 1
    
    # Get current user's student record
    context.student = None
    context.application_period = None
    context.existing_application = None
    context.hostels = []
    
    if frappe.session.user and frappe.session.user != "Guest":
        # Find student linked to this user
        student = frappe.db.get_value("Student", {"user": frappe.session.user}, ["name", "student_name", "gender", "program"], as_dict=True)
        
        if student:
            context.student = student
            
            # Get active application period
            application_period = frappe.db.get_value(
                "Residence Application Period",
                {
                    "is_open": 1,
                    "application_start_date": ["<=", today()],
                    "application_end_date": [">=", today()]
                },
                ["name", "academic_year", "application_start_date", "application_end_date"],
                as_dict=True
            )
            
            context.application_period = application_period
            
            if application_period:
                # Check for existing application
                existing = frappe.db.get_value(
                    "Room Booking Application",
                    {
                        "student": student.name,
                        "application_period": application_period.name,
                        "docstatus": ["!=", 2]
                    },
                    ["name", "status", "allocated_room"],
                    as_dict=True
                )
                context.existing_application = existing
                
                # Get hostels based on gender
                hostel_type = "Mens Hostel" if student.gender == "Male" else "Ladies Hostel"
                context.hostels = frappe.get_all(
                    "Hostel",
                    filters={"is_active": 1, "hostel_type": hostel_type},
                    fields=["name", "hostel_type"]
                )
    
    return context
