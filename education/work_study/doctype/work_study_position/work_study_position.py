# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class WorkStudyPosition(Document):
    def validate(self):
        self.calculate_available_slots()
        self.validate_dates()
    
    def calculate_available_slots(self):
        """Calculate available slots"""
        self.available_slots = (self.total_slots or 0) - (self.filled_slots or 0)
        if self.available_slots < 0:
            self.available_slots = 0
    
    def validate_dates(self):
        """Validate application period dates"""
        if self.application_start_date and self.application_end_date:
            if getdate(self.application_start_date) > getdate(self.application_end_date):
                frappe.throw("Application End Date must be after Start Date")
    
    def update_filled_slots(self):
        """Update filled slots count based on approved assignments"""
        count = frappe.db.count("Work Study Assignment", {
            "work_study_position": self.name,
            "status": ["in", ["Active", "On Leave"]]
        })
        self.filled_slots = count
        self.calculate_available_slots()
        
        # Auto-update status
        if self.available_slots == 0 and self.status == "Open":
            self.status = "Filled"
        
        self.save(ignore_permissions=True)
    
    def is_application_open(self):
        """Check if applications are currently open"""
        if self.status != "Open" or not self.published:
            return False
        
        today_date = getdate(today())
        
        if self.application_start_date and getdate(self.application_start_date) > today_date:
            return False
        
        if self.application_end_date and getdate(self.application_end_date) < today_date:
            return False
        
        return self.available_slots > 0
