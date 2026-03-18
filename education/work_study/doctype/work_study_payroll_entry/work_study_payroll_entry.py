# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt, now_datetime

class WorkStudyPayrollEntry(Document):
    def validate(self):
        self.validate_dates()
    
    def validate_dates(self):
        """Validate payroll period dates"""
        if self.payroll_period_start and self.payroll_period_end:
            if getdate(self.payroll_period_end) < getdate(self.payroll_period_start):
                frappe.throw("Period End Date cannot be before Period Start Date")
    
    def on_submit(self):
        if not self.timesheets or len(self.timesheets) == 0:
            frappe.throw("No timesheets to process. Please fetch timesheets first.")
        
        self.process_payments()
    
    @frappe.whitelist()
    def fetch_timesheets(self):
        """Fetch all approved timesheets for the payroll period"""
        self.timesheets = []
        
        filters = {
            "status": "Approved",
            "docstatus": 1,
            "week_start_date": [">=", self.payroll_period_start],
            "week_end_date": ["<=", self.payroll_period_end]
        }
        
        # Apply optional filters
        if self.department:
            filters["department"] = self.department
        
        if self.work_study_position:
            filters["work_study_position"] = self.work_study_position
        
        timesheets = frappe.get_all("Work Study Timesheet",
            filters=filters,
            fields=["name", "student", "student_name", "total_hours", "total_amount"]
        )
        
        if not timesheets:
            frappe.msgprint("No approved timesheets found for the selected period")
            return
        
        total_hours = 0
        total_amount = 0
        students = set()
        
        for ts in timesheets:
            self.append("timesheets", {
                "timesheet": ts.name,
                "student": ts.student,
                "student_name": ts.student_name,
                "hours": ts.total_hours,
                "amount": ts.total_amount,
                "payment_status": "Pending"
            })
            total_hours += flt(ts.total_hours)
            total_amount += flt(ts.total_amount)
            students.add(ts.student)
        
        self.total_timesheets = len(timesheets)
        self.total_hours = flt(total_hours, 2)
        self.total_amount = flt(total_amount, 2)
        self.total_students = len(students)
        self.status = "Timesheets Fetched"
        
        self.save()
        
        frappe.msgprint(f"Fetched {len(timesheets)} timesheets for {len(students)} students. Total: {self.total_amount}")
    
    def process_payments(self):
        """Process payments for all timesheets - credit to student wallets"""
        self.status = "Processing"
        self.db_set("status", "Processing")
        
        processed = 0
        failed = 0
        log_entries = []
        
        for row in self.timesheets:
            try:
                # Get or create student wallet account
                wallet_account = self.get_or_create_wallet_account(row.student, row.student_name)
                
                # Create Journal Entry
                je = self.create_wallet_credit(row, wallet_account)
                
                # Update row
                row.payment_status = "Processed"
                row.journal_entry = je.name
                
                # Update original timesheet
                frappe.db.set_value("Work Study Timesheet", row.timesheet, {
                    "status": "Paid",
                    "journal_entry": je.name
                })
                
                processed += 1
                log_entries.append(f"[{now_datetime()}] SUCCESS: {row.student_name} - {row.amount} credited to wallet")
                
            except Exception as e:
                failed += 1
                row.payment_status = "Failed"
                row.error_message = str(e)
                log_entries.append(f"[{now_datetime()}] FAILED: {row.student_name} - {str(e)}")
                frappe.log_error(f"Work Study Payment Failed for {row.student}: {str(e)}")
        
        self.processed_count = processed
        self.failed_count = failed
        self.processing_log = "\n".join(log_entries)
        
        if failed == 0:
            self.status = "Completed"
        elif processed == 0:
            self.status = "Failed"
        else:
            self.status = "Completed"  # Partial success
        
        self.save(ignore_permissions=True)
        
        frappe.msgprint(f"Payment processing complete. Processed: {processed}, Failed: {failed}")
    
    def get_or_create_wallet_account(self, student, student_name):
        """Get or create a wallet account for the student"""
        # Check if wallet account exists on assignment
        assignment = frappe.db.get_value("Work Study Assignment",
            {"student": student, "status": "Active"},
            "wallet_account"
        )
        
        if assignment:
            return assignment
        
        # Look for existing wallet account
        account_name = f"Student Wallet - {student_name}"
        existing = frappe.db.get_value("Account", {
            "account_name": account_name,
            "company": self.company
        })
        
        if existing:
            return existing
        
        # Create new wallet account
        if not self.student_wallet_parent_account:
            frappe.throw("Student Wallet Parent Account not configured")
        
        account = frappe.new_doc("Account")
        account.account_name = account_name
        account.parent_account = self.student_wallet_parent_account
        account.company = self.company
        account.account_type = "Payable"
        account.account_currency = frappe.db.get_value("Company", self.company, "default_currency")
        account.insert(ignore_permissions=True)
        
        # Update assignment with wallet account
        frappe.db.set_value("Work Study Assignment",
            {"student": student, "status": "Active"},
            "wallet_account", account.name
        )
        
        return account.name
    
    def create_wallet_credit(self, row, wallet_account):
        """Create Journal Entry to credit student wallet"""
        je = frappe.new_doc("Journal Entry")
        je.posting_date = self.posting_date
        je.company = self.company
        je.voucher_type = "Journal Entry"
        je.user_remark = f"Work Study Payment - {row.student_name} - Payroll Entry: {self.name}"
        
        # Debit: Work Study Expense Account
        je.append("accounts", {
            "account": self.work_study_expense_account,
            "debit_in_account_currency": row.amount,
            "cost_center": self.cost_center
        })
        
        # Credit: Student Wallet (Liability)
        je.append("accounts", {
            "account": wallet_account,
            "credit_in_account_currency": row.amount,
            "party_type": "Student",
            "party": row.student
        })
        
        je.insert(ignore_permissions=True)
        je.submit()
        
        # Update assignment wallet credits
        frappe.db.sql("""
            UPDATE `tabWork Study Assignment`
            SET total_wallet_credits = COALESCE(total_wallet_credits, 0) + %s
            WHERE student = %s AND status = 'Active'
        """, (row.amount, row.student))
        
        return je
    
    @frappe.whitelist()
    def retry_failed_payments(self):
        """Retry failed payments"""
        failed_rows = [row for row in self.timesheets if row.payment_status == "Failed"]
        
        if not failed_rows:
            frappe.msgprint("No failed payments to retry")
            return
        
        retried = 0
        still_failed = 0
        
        for row in failed_rows:
            try:
                wallet_account = self.get_or_create_wallet_account(row.student, row.student_name)
                je = self.create_wallet_credit(row, wallet_account)
                
                row.payment_status = "Processed"
                row.journal_entry = je.name
                row.error_message = ""
                
                frappe.db.set_value("Work Study Timesheet", row.timesheet, {
                    "status": "Paid",
                    "journal_entry": je.name
                })
                
                retried += 1
                
            except Exception as e:
                still_failed += 1
                row.error_message = str(e)
        
        self.processed_count = (self.processed_count or 0) + retried
        self.failed_count = still_failed
        self.save(ignore_permissions=True)
        
        frappe.msgprint(f"Retry complete. Succeeded: {retried}, Still Failed: {still_failed}")
