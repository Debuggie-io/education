# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class OffCampusRegistration(Document):
    def validate(self):
        self.validate_duplicate_registration()
        self.set_student_details()
    
    def validate_duplicate_registration(self):
        """Prevent duplicate registrations for same semester"""
        if self.is_new():
            existing = frappe.db.exists("Off Campus Registration", {
                "student": self.student,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "docstatus": ["!=", 2]
            })
            if existing:
                frappe.throw(_("You have already registered your off-campus residence for this semester"))
    
    def set_student_details(self):
        """Fetch student details"""
        if self.student:
            student = frappe.get_doc("Student", self.student)
            self.student_name = student.student_name
            self.gender = student.gender
            self.program = student.program
    
    def on_submit(self):
        """Create or update Student Residence record"""
        self.create_student_residence()
    
    def create_student_residence(self):
        """Create Student Residence record for off-campus student"""
        # Check if residence record exists
        existing = frappe.db.exists("Student Residence", {
            "student": self.student,
            "academic_year": self.academic_year,
            "status": "Active"
        })
        
        if existing:
            # Update existing record
            frappe.db.set_value("Student Residence", existing, {
                "residence_type": "Off Campus",
                "off_campus_address": self.full_address,
                "guardian_contact": self.landlord_phone
            })
        else:
            # Create new record
            residence = frappe.new_doc("Student Residence")
            residence.student = self.student
            residence.academic_year = self.academic_year
            residence.academic_term = self.academic_term
            residence.residence_type = "Off Campus"
            residence.off_campus_address = self.full_address
            residence.guardian_contact = self.landlord_phone
            residence.status = "Active"
            residence.check_in_date = frappe.utils.today()
            residence.insert(ignore_permissions=True)
        
        frappe.msgprint(_("Off-campus residence registered successfully"))
    
    @frappe.whitelist()
    def confirm_continuation(self):
        """Confirm continuing at same residence for next semester"""
        self.status = "Confirmed"
        self.confirmation_date = frappe.utils.today()
        self.save(ignore_permissions=True)
        frappe.msgprint(_("Residence continuation confirmed for next semester"))
