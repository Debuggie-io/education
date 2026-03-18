# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt, time_diff_in_hours, get_datetime

class WorkStudyTimesheet(Document):
    def validate(self):
        self.validate_assignment_active()
        self.validate_dates()
        self.calculate_hours()
        self.validate_max_hours()
    
    def before_submit(self):
        if self.status == "Draft":
            self.status = "Pending Approval"
    
    def on_update_after_submit(self):
        if self.status == "Approved":
            self.update_assignment_totals()
    
    def validate_assignment_active(self):
        """Ensure assignment is active"""
        if self.work_study_assignment:
            status = frappe.db.get_value("Work Study Assignment", 
                self.work_study_assignment, "status")
            if status not in ["Active", "On Leave"]:
                frappe.throw("Cannot create timesheet for inactive assignment")
    
    def validate_dates(self):
        """Validate timesheet dates"""
        if self.week_start_date and self.week_end_date:
            if getdate(self.week_end_date) < getdate(self.week_start_date):
                frappe.throw("Week End Date cannot be before Week Start Date")
        
        # Validate time log dates are within week
        for log in self.time_logs:
            if log.date:
                log_date = getdate(log.date)
                if self.week_start_date and log_date < getdate(self.week_start_date):
                    frappe.throw(f"Time log date {log.date} is before week start date")
                if self.week_end_date and log_date > getdate(self.week_end_date):
                    frappe.throw(f"Time log date {log.date} is after week end date")
    
    def calculate_hours(self):
        """Calculate hours for each time log and totals"""
        total_hours = 0
        
        for log in self.time_logs:
            if log.start_time and log.end_time:
                # Calculate hours between start and end time
                start = get_datetime(f"2000-01-01 {log.start_time}")
                end = get_datetime(f"2000-01-01 {log.end_time}")
                
                hours = time_diff_in_hours(end, start)
                if hours < 0:
                    hours += 24  # Handle overnight shifts
                
                log.hours = flt(hours, 2)
                total_hours += log.hours
        
        self.total_hours = flt(total_hours, 2)
        self.total_amount = flt(self.total_hours * flt(self.hourly_rate), 2)
        self.hours_remaining = flt(flt(self.max_hours_per_week) - self.total_hours, 2)
    
    def validate_max_hours(self):
        """Validate hours don't exceed maximum allowed"""
        if self.max_hours_per_week and self.total_hours > self.max_hours_per_week:
            frappe.throw(f"Total hours ({self.total_hours}) exceeds maximum allowed per week ({self.max_hours_per_week})")
        
        # Check semester limit
        if self.work_study_assignment:
            assignment = frappe.get_doc("Work Study Assignment", self.work_study_assignment)
            max_semester = assignment.max_hours_per_semester or 0
            
            if max_semester:
                # Get total hours already logged
                existing_hours = frappe.db.sql("""
                    SELECT COALESCE(SUM(total_hours), 0)
                    FROM `tabWork Study Timesheet`
                    WHERE work_study_assignment = %s
                    AND docstatus = 1
                    AND name != %s
                """, (self.work_study_assignment, self.name))[0][0]
                
                total_semester_hours = flt(existing_hours) + self.total_hours
                
                if total_semester_hours > max_semester:
                    frappe.throw(f"Total semester hours ({total_semester_hours}) would exceed maximum ({max_semester})")
    
    def update_assignment_totals(self):
        """Update assignment with total hours and earnings"""
        if self.work_study_assignment:
            assignment = frappe.get_doc("Work Study Assignment", self.work_study_assignment)
            assignment.update_hours_and_earnings()
    
    @frappe.whitelist()
    def approve_timesheet(self, comments=None):
        """Approve the timesheet"""
        if self.status != "Pending Approval":
            frappe.throw("Timesheet is not pending approval")
        
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = today()
        self.approval_comments = comments
        self.save(ignore_permissions=True)
        
        # Update assignment totals
        self.update_assignment_totals()
        
        frappe.msgprint("Timesheet approved")
    
    @frappe.whitelist()
    def reject_timesheet(self, reason):
        """Reject the timesheet"""
        if self.status != "Pending Approval":
            frappe.throw("Timesheet is not pending approval")
        
        self.status = "Rejected"
        self.rejection_reason = reason
        self.save(ignore_permissions=True)
        
        frappe.msgprint("Timesheet rejected")
    
    @frappe.whitelist()
    def process_payment(self):
        """Process payment - create wallet credit"""
        if self.status != "Approved":
            frappe.throw("Only approved timesheets can be processed for payment")
        
        # Get assignment details
        assignment = frappe.get_doc("Work Study Assignment", self.work_study_assignment)
        
        if not assignment.wallet_account:
            frappe.throw("Student wallet account not configured on assignment")
        
        # Create Journal Entry for wallet credit
        je = self.create_wallet_journal_entry(assignment)
        
        self.status = "Paid"
        self.journal_entry = je.name
        self.save(ignore_permissions=True)
        
        frappe.msgprint(f"Payment processed. Wallet credited: {je.name}")
        return je.name
    
    def create_wallet_journal_entry(self, assignment):
        """Create Journal Entry to credit student wallet"""
        company = frappe.defaults.get_defaults().get("company")
        
        # Get work study expense account
        expense_account = frappe.db.get_value("Company", company, "default_expense_account")
        if not expense_account:
            expense_account = frappe.db.get_value("Account", {
                "account_type": "Expense Account",
                "company": company,
                "is_group": 0
            })
        
        je = frappe.new_doc("Journal Entry")
        je.posting_date = today()
        je.company = company
        je.voucher_type = "Journal Entry"
        je.user_remark = f"Work Study Payment - {self.student_name} - {self.name}"
        
        # Debit: Work Study Expense
        je.append("accounts", {
            "account": expense_account,
            "debit_in_account_currency": self.total_amount,
            "cost_center": frappe.db.get_value("Company", company, "cost_center")
        })
        
        # Credit: Student Wallet (Liability)
        je.append("accounts", {
            "account": assignment.wallet_account,
            "credit_in_account_currency": self.total_amount,
            "party_type": "Student",
            "party": self.student
        })
        
        je.insert(ignore_permissions=True)
        je.submit()
        
        # Update assignment wallet credits
        assignment.total_wallet_credits = flt(assignment.total_wallet_credits or 0) + self.total_amount
        assignment.save(ignore_permissions=True)
        
        return je
