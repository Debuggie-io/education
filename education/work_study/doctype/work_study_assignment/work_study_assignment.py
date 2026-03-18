# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt

class WorkStudyAssignment(Document):
    def validate(self):
        self.validate_dates()
        self.validate_duplicate()
    
    def after_insert(self):
        self.update_position_slots()
    
    def on_update(self):
        if self.has_value_changed("status"):
            self.update_position_slots()
    
    def on_trash(self):
        self.update_position_slots()
    
    def validate_dates(self):
        """Validate assignment dates"""
        if self.end_date and self.start_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw("End Date cannot be before Start Date")
    
    def validate_duplicate(self):
        """Prevent duplicate active assignments for same student-position"""
        existing = frappe.db.exists("Work Study Assignment", {
            "student": self.student,
            "work_study_position": self.work_study_position,
            "status": ["in", ["Active", "On Leave"]],
            "name": ["!=", self.name]
        })
        
        if existing:
            frappe.throw(f"Student already has an active assignment for this position: {existing}")
    
    def update_position_slots(self):
        """Update filled slots on position"""
        if self.work_study_position:
            position = frappe.get_doc("Work Study Position", self.work_study_position)
            position.update_filled_slots()
    
    def update_hours_and_earnings(self):
        """Calculate total hours worked and earnings from timesheets"""
        # Get all approved timesheets for this assignment
        timesheets = frappe.db.sql("""
            SELECT SUM(wst.hours) as total_hours
            FROM `tabWork Study Timesheet` wst
            WHERE wst.work_study_assignment = %s
            AND wst.status = 'Approved'
            AND wst.docstatus = 1
        """, self.name, as_dict=True)
        
        total_hours = flt(timesheets[0].total_hours if timesheets else 0, 2)
        self.total_hours_worked = total_hours
        self.total_earnings = flt(total_hours * flt(self.hourly_rate), 2)
        self.save(ignore_permissions=True)
    
    @frappe.whitelist()
    def terminate_assignment(self, reason):
        """Terminate the assignment"""
        self.status = "Terminated"
        self.termination_reason = reason
        self.end_date = today()
        self.save(ignore_permissions=True)
        
        # Update position slots
        self.update_position_slots()
        
        frappe.msgprint("Assignment terminated")
    
    @frappe.whitelist()
    def complete_assignment(self):
        """Mark assignment as completed"""
        self.status = "Completed"
        if not self.end_date:
            self.end_date = today()
        self.save(ignore_permissions=True)
        
        # Update position slots
        self.update_position_slots()
        
        frappe.msgprint("Assignment marked as completed")
    
    @frappe.whitelist()
    def create_timesheet(self):
        """Create a new timesheet for this assignment"""
        timesheet = frappe.new_doc("Work Study Timesheet")
        timesheet.work_study_assignment = self.name
        timesheet.student = self.student
        timesheet.employee = self.employee
        timesheet.work_study_position = self.work_study_position
        timesheet.save()
        
        return timesheet.name
