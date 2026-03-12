# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def submit_room_application(student, application_period, preferred_hostel=None, preferred_room_type=None, special_requirements=None):
    """Submit a room booking application from web portal"""
    
    # Verify student belongs to current user
    student_user = frappe.db.get_value("Student", student, "user")
    if student_user != frappe.session.user:
        frappe.throw(_("Unauthorized access"))
    
    # Check for existing application
    existing = frappe.db.exists("Room Booking Application", {
        "student": student,
        "application_period": application_period,
        "docstatus": ["!=", 2]
    })
    
    if existing:
        frappe.throw(_("You have already submitted an application for this period"))
    
    # Create application
    app = frappe.new_doc("Room Booking Application")
    app.student = student
    app.application_period = application_period
    app.preferred_hostel = preferred_hostel
    app.preferred_room_type = preferred_room_type
    app.special_requirements = special_requirements
    app.insert(ignore_permissions=True)
    app.submit()
    
    frappe.db.commit()
    
    return {
        "success": True,
        "message": _("Application submitted successfully"),
        "application": app.name
    }

@frappe.whitelist()
def get_available_rooms(hostel):
    """Get available rooms for a hostel"""
    rooms = frappe.get_all(
        "Hostel Room",
        filters={
            "hostel": hostel,
            "is_available": 1
        },
        fields=["name", "room_number", "room_capacity", "occupied_beds", "room_type", "floor"]
    )
    
    # Filter rooms with available beds
    available_rooms = []
    for room in rooms:
        available_beds = room.room_capacity - room.occupied_beds
        if available_beds > 0:
            room["available_beds"] = available_beds
            available_rooms.append(room)
    
    return available_rooms

@frappe.whitelist()
def get_student_residence_status(student=None):
    """Get current residence status for a student"""
    if not student:
        student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
    
    if not student:
        return None
    
    # Get current academic year
    current_year = frappe.db.get_single_value("Education Settings", "current_academic_year")
    
    residence = frappe.db.get_value(
        "Student Residence",
        {
            "student": student,
            "academic_year": current_year,
            "status": "Active"
        },
        ["name", "residence_type", "hostel", "hostel_room", "check_in_date"],
        as_dict=True
    )
    
    return residence
