# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class StudentResidence(Document):
    def validate(self):
        if self.residence_type == "On Campus":
            self.validate_hostel_gender()
            self.validate_room_availability()
    
    def validate_hostel_gender(self):
        """Ensure student gender matches hostel type"""
        if not self.hostel:
            return
        
        student = frappe.get_doc("Student", self.student)
        hostel = frappe.get_doc("Hostel", self.hostel)
        
        gender = student.gender
        hostel_type = hostel.hostel_type
        
        # Validate gender-hostel match
        if gender == "Male" and hostel_type != "Mens Hostel":
            frappe.throw(_("Male students can only be assigned to Mens Hostels"))
        
        if gender == "Female" and hostel_type != "Ladies Hostel":
            frappe.throw(_("Female students can only be assigned to Ladies Hostels"))
    
    def validate_room_availability(self):
        """Check if room has available beds"""
        if not self.hostel_room:
            return
        
        room = frappe.get_doc("Hostel Room", self.hostel_room)
        
        if not room.is_available:
            frappe.throw(_("Room {0} is not available").format(self.hostel_room))
        
        # Check current occupancy (excluding this record if updating)
        filters = {
            "hostel_room": self.hostel_room,
            "status": "Active",
            "academic_year": self.academic_year
        }
        if self.name and not self.is_new():
            filters["name"] = ["!=", self.name]
        
        current_occupants = frappe.db.count("Student Residence", filters)
        
        if current_occupants >= room.room_capacity:
            frappe.throw(_("Room {0} is fully occupied ({1}/{2} beds)").format(
                self.hostel_room, current_occupants, room.room_capacity
            ))
    
    def on_update(self):
        if self.residence_type == "On Campus" and self.hostel_room:
            self.update_room_occupancy()
    
    def on_trash(self):
        if self.residence_type == "On Campus" and self.hostel_room:
            self.update_room_occupancy()
    
    def update_room_occupancy(self):
        """Update occupied beds count in room"""
        if not self.hostel_room:
            return
        
        occupied = frappe.db.count("Student Residence", {
            "hostel_room": self.hostel_room,
            "status": "Active"
        })
        
        frappe.db.set_value("Hostel Room", self.hostel_room, "occupied_beds", occupied)
        
        # Trigger hostel stats update
        room = frappe.get_doc("Hostel Room", self.hostel_room)
        room.update_hostel_stats()
