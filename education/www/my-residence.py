# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def get_context(context):
    context.no_cache = 1
    context.student = None
    context.residence = None
    context.applications = []
    
    if frappe.session.user and frappe.session.user != "Guest":
        # Get student record
        student = frappe.db.get_value(
            "Student",
            {"user": frappe.session.user},
            ["name", "student_name", "gender", "program"],
            as_dict=True
        )
        
        if student:
            context.student = student
            
            # Get current residence
            residence = frappe.db.get_value(
                "Student Residence",
                {
                    "student": student.name,
                    "status": "Active"
                },
                ["name", "residence_type", "hostel", "hostel_room", "academic_year", "check_in_date"],
                as_dict=True,
                order_by="creation desc"
            )
            context.residence = residence
            
            # Get application history
            applications = frappe.get_all(
                "Room Booking Application",
                filters={"student": student.name},
                fields=["name", "academic_year", "status", "allocated_room", "application_date"],
                order_by="creation desc"
            )
            context.applications = applications
    
    return context
