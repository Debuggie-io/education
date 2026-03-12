# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class RoomBookingApplication(Document):
    def validate(self):
        self.validate_application_period()
        self.validate_duplicate_application()
        self.filter_hostel_by_gender()
    
    def validate_application_period(self):
        """Check if application period is open"""
        if not self.application_period:
            return
        
        period = frappe.get_doc("Residence Application Period", self.application_period)
        
        if not period.is_open:
            frappe.throw(_("Application period {0} is closed").format(self.application_period))
        
        from frappe.utils import getdate, today
        if getdate(today()) < getdate(period.application_start_date):
            frappe.throw(_("Application period has not started yet"))
        
        if getdate(today()) > getdate(period.application_end_date):
            frappe.throw(_("Application period has ended"))
    
    def validate_duplicate_application(self):
        """Prevent duplicate applications for same period"""
        if self.is_new():
            existing = frappe.db.exists("Room Booking Application", {
                "student": self.student,
                "application_period": self.application_period,
                "docstatus": ["!=", 2]  # Not cancelled
            })
            
            if existing:
                frappe.throw(_("You have already submitted an application for this period"))
    
    def filter_hostel_by_gender(self):
        """Set preferred hostel based on gender"""
        if self.preferred_hostel:
            student = frappe.get_doc("Student", self.student)
            hostel = frappe.get_doc("Hostel", self.preferred_hostel)
            
            if student.gender == "Male" and hostel.hostel_type != "Mens Hostel":
                frappe.throw(_("Male students can only apply for Mens Hostels"))
            
            if student.gender == "Female" and hostel.hostel_type != "Ladies Hostel":
                frappe.throw(_("Female students can only apply for Ladies Hostels"))
    
    def on_submit(self):
        self.status = "Pending"
        frappe.db.set_value(self.doctype, self.name, "status", "Pending")
    
    def on_cancel(self):
        self.status = "Cancelled"
        frappe.db.set_value(self.doctype, self.name, "status", "Cancelled")
    
    @frappe.whitelist()
    def allocate_room(self, hostel, room):
        """Allocate room to student"""
        self.allocated_hostel = hostel
        self.allocated_room = room
        self.allocation_date = frappe.utils.today()
        self.allocated_by = frappe.session.user
        self.status = "Allocated"
        self.save(ignore_permissions=True)
        
        # Create Student Residence record
        residence = frappe.new_doc("Student Residence")
        residence.student = self.student
        residence.academic_year = self.academic_year
        residence.residence_type = "On Campus"
        residence.hostel = hostel
        residence.hostel_room = room
        residence.check_in_date = frappe.utils.today()
        residence.status = "Active"
        residence.insert(ignore_permissions=True)
        
        frappe.msgprint(_("Room {0} allocated to {1}").format(room, self.student_name))
        
        return residence.name
