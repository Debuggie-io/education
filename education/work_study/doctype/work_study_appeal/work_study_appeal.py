# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class WorkStudyAppeal(Document):
    def validate(self):
        self.fetch_original_details()
    
    def on_submit(self):
        self.status = "Under Review"
        self.update_application_status("Appeal Under Review")
    
    def fetch_original_details(self):
        """Fetch details from original application"""
        if self.work_study_application:
            app = frappe.get_doc("Work Study Application", self.work_study_application)
            self.original_rejection_reason = app.rejection_reason
            self.original_screening_notes = app.screening_notes
    
    def update_application_status(self, status):
        """Update the original application status"""
        frappe.db.set_value("Work Study Application", self.work_study_application, "status", status)
    
    @frappe.whitelist()
    def approve_appeal(self, comments=None):
        """Approve the appeal"""
        if self.status not in ["Pending Review", "Under Review"]:
            frappe.throw("Appeal cannot be approved at this stage")
        
        self.status = "Approved"
        self.reviewed_by = frappe.session.user
        self.review_date = today()
        self.review_comments = comments
        self.save(ignore_permissions=True)
        
        # Update original application
        app = frappe.get_doc("Work Study Application", self.work_study_application)
        app.status = "Appeal Approved"
        app.is_eligible = 1  # Override eligibility
        app.screening_notes = "Eligibility overridden via appeal approval"
        app.save(ignore_permissions=True)
        
        # Move to HOD approval
        app.status = "Pending HOD Approval"
        app.save(ignore_permissions=True)
        
        frappe.msgprint("Appeal approved. Application moved to HOD approval.")
    
    @frappe.whitelist()
    def reject_appeal(self, comments=None):
        """Reject the appeal"""
        if self.status not in ["Pending Review", "Under Review"]:
            frappe.throw("Appeal cannot be rejected at this stage")
        
        self.status = "Rejected"
        self.reviewed_by = frappe.session.user
        self.review_date = today()
        self.review_comments = comments
        self.save(ignore_permissions=True)
        
        # Update original application
        self.update_application_status("Appeal Rejected")
        
        frappe.msgprint("Appeal rejected.")
