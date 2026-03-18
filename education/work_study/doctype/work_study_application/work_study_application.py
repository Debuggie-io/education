# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, flt

class WorkStudyApplication(Document):
    def validate(self):
        self.validate_position_open()
        self.fetch_student_data()
        if self.status == "Draft":
            self.run_automated_screening()
    
    def before_submit(self):
        if self.status == "Draft":
            self.status = "Pending Screening"
            self.run_automated_screening()
        
        if not self.is_eligible and self.status not in ["Appeal Submitted", "Appeal Under Review", "Appeal Approved"]:
            self.status = "Screening Failed"
    
    def on_submit(self):
        if self.is_eligible:
            self.status = "Pending HOD Approval"
            self.db_set("status", "Pending HOD Approval")
    
    def validate_position_open(self):
        """Validate position is accepting applications"""
        if not self.work_study_position:
            return
        
        position = frappe.get_doc("Work Study Position", self.work_study_position)
        
        if not position.is_application_open():
            frappe.throw(f"Position '{position.position_title}' is not accepting applications")
        
        # Check for duplicate applications
        existing = frappe.db.exists("Work Study Application", {
            "student": self.student,
            "work_study_position": self.work_study_position,
            "status": ["not in", ["Rejected", "Withdrawn", "Screening Failed", "Appeal Rejected"]],
            "name": ["!=", self.name]
        })
        
        if existing:
            frappe.throw("You have already applied for this position")
    
    def fetch_student_data(self):
        """Fetch student academic and financial data"""
        if not self.student:
            return
        
        student = frappe.get_doc("Student", self.student)
        
        # Get current program enrollment
        enrollment = frappe.db.get_value("Program Enrollment", 
            {"student": self.student, "docstatus": 1},
            ["program", "academic_year", "academic_term"],
            as_dict=True,
            order_by="creation desc"
        )
        
        if enrollment:
            self.current_program = enrollment.program
            
            # Calculate year of study from enrollment year
            self.year_of_study = self.calculate_year_of_study(enrollment)
        
        # Get GPA
        self.current_gpa = self.get_student_gpa()
        
        # Get financial data
        self.fetch_financial_data()
    
    def calculate_year_of_study(self, enrollment):
        """Calculate year of study based on enrollment"""
        try:
            # Get the enrollment year
            if enrollment.academic_year:
                year_doc = frappe.get_doc("Academic Year", enrollment.academic_year)
                start_year = getdate(year_doc.year_start_date).year if year_doc.year_start_date else None
                
                if start_year:
                    current_year = getdate(today()).year
                    year_of_study = current_year - start_year + 1
                    return min(max(year_of_study, 1), 6)  # Cap between 1-6
        except:
            pass
        return 1
    
    def get_student_gpa(self):
        """Get student's current GPA from assessment results"""
        # Try to get GPA from Student record first
        gpa = frappe.db.get_value("Student", self.student, "custom_gpa")
        if gpa:
            return flt(gpa, 2)
        
        # Alternative: Calculate from Assessment Results
        results = frappe.db.sql("""
            SELECT AVG(ar.grade_points) as gpa
            FROM `tabAssessment Result` ar
            WHERE ar.student = %s
            AND ar.docstatus = 1
            AND ar.grade_points IS NOT NULL
        """, self.student, as_dict=True)
        
        if results and results[0].gpa:
            return flt(results[0].gpa, 2)
        
        return 0.0
    
    def fetch_financial_data(self):
        """Fetch student financial data from Sales Invoices"""
        student = frappe.get_doc("Student", self.student)
        customer = None
        
        # Try to find linked customer
        if hasattr(student, 'customer') and student.customer:
            customer = student.customer
        else:
            # Search by student name
            customer = frappe.db.get_value("Customer", {"customer_name": student.student_name})
        
        if customer:
            # Get total billed
            total_billed = frappe.db.sql("""
                SELECT COALESCE(SUM(grand_total), 0) as total
                FROM `tabSales Invoice`
                WHERE customer = %s AND docstatus = 1
            """, customer)[0][0] or 0
            
            # Get total paid
            total_paid = frappe.db.sql("""
                SELECT COALESCE(SUM(paid_amount), 0) as total
                FROM `tabPayment Entry`
                WHERE party_type = 'Customer' AND party = %s AND docstatus = 1
            """, customer)[0][0] or 0
            
            self.total_billed = flt(total_billed, 2)
            self.outstanding_balance = flt(total_billed - total_paid, 2)
            
            # Calculate financial need score (0-100)
            # Higher outstanding balance ratio = higher need score
            if self.total_billed > 0:
                self.financial_need_score = flt((self.outstanding_balance / self.total_billed) * 100, 2)
            else:
                self.financial_need_score = 50  # Default mid-score if no billing history
        else:
            self.total_billed = 0
            self.outstanding_balance = 0
            self.financial_need_score = 50
    
    def run_automated_screening(self):
        """Run automated eligibility screening"""
        if not self.work_study_position:
            return
        
        position = frappe.get_doc("Work Study Position", self.work_study_position)
        screening_notes = []
        
        # 1. GPA Check
        required_gpa = position.minimum_gpa or 2.0
        self.gpa_eligible = self.current_gpa >= required_gpa
        if not self.gpa_eligible:
            screening_notes.append(f"GPA {self.current_gpa} below required {required_gpa}")
        
        # 2. Financial Need Check
        required_score = position.minimum_financial_need_score or 0
        self.financial_need_eligible = self.financial_need_score >= required_score
        if not self.financial_need_eligible:
            screening_notes.append(f"Financial need score {self.financial_need_score} below required {required_score}")
        
        # 3. Program Eligibility Check
        if position.eligible_programs and len(position.eligible_programs) > 0:
            eligible_programs = [ep.program for ep in position.eligible_programs]
            self.program_eligible = self.current_program in eligible_programs
            if not self.program_eligible:
                screening_notes.append(f"Program {self.current_program} not in eligible list")
        else:
            self.program_eligible = True  # No restrictions
        
        # 4. Year of Study Check
        if position.eligible_year_of_study:
            min_year = int(position.eligible_year_of_study)
            self.year_eligible = (self.year_of_study or 1) >= min_year
            if not self.year_eligible:
                screening_notes.append(f"Year {self.year_of_study} below required year {min_year}")
        else:
            self.year_eligible = True
        
        # Overall Eligibility
        self.is_eligible = all([
            self.gpa_eligible,
            self.financial_need_eligible,
            self.program_eligible,
            self.year_eligible
        ])
        
        if screening_notes:
            self.screening_notes = "; ".join(screening_notes)
        else:
            self.screening_notes = "All eligibility criteria met"
    
    @frappe.whitelist()
    def approve_hod(self, comments=None):
        """HOD approves the application"""
        if self.status != "Pending HOD Approval":
            frappe.throw("Application is not pending HOD approval")
        
        self.hod_approved = 1
        self.hod_approved_by = frappe.session.user
        self.hod_approval_date = today()
        self.hod_comments = comments
        self.status = "Pending Dean Approval"
        self.save(ignore_permissions=True)
        
        frappe.msgprint("Application approved. Pending Dean approval.")
    
    @frappe.whitelist()
    def approve_dean(self, comments=None):
        """Dean gives final approval"""
        if self.status != "Pending Dean Approval":
            frappe.throw("Application is not pending Dean approval")
        
        self.dean_approved = 1
        self.dean_approved_by = frappe.session.user
        self.dean_approval_date = today()
        self.dean_comments = comments
        self.status = "Approved"
        self.save(ignore_permissions=True)
        
        # Create Work Study Assignment
        self.create_assignment()
        
        frappe.msgprint("Application approved! Work Study Assignment created.")
    
    @frappe.whitelist()
    def reject_application(self, reason):
        """Reject the application"""
        if self.status not in ["Pending HOD Approval", "Pending Dean Approval", "Appeal Under Review"]:
            frappe.throw("Application cannot be rejected at this stage")
        
        self.status = "Rejected"
        self.rejection_reason = reason
        self.save(ignore_permissions=True)
        
        frappe.msgprint("Application rejected.")
    
    @frappe.whitelist()
    def submit_appeal(self):
        """Submit an appeal for a rejected application"""
        if self.status not in ["Screening Failed", "Rejected"]:
            frappe.throw("Only rejected applications can be appealed")
        
        self.status = "Appeal Submitted"
        self.save(ignore_permissions=True)
        
        # Create Appeal Document
        appeal = frappe.new_doc("Work Study Appeal")
        appeal.work_study_application = self.name
        appeal.student = self.student
        appeal.save(ignore_permissions=True)
        
        frappe.msgprint(f"Appeal submitted: {appeal.name}")
        return appeal.name
    
    def create_assignment(self):
        """Create Work Study Assignment after approval"""
        # Create or link Employee record
        employee = self.get_or_create_employee()
        
        # Create Work Study Assignment
        assignment = frappe.new_doc("Work Study Assignment")
        assignment.student = self.student
        assignment.employee = employee
        assignment.work_study_position = self.work_study_position
        assignment.work_study_application = self.name
        assignment.start_date = today()
        assignment.status = "Active"
        assignment.save(ignore_permissions=True)
        
        self.db_set("work_study_assignment", assignment.name)
        self.db_set("employee_created", employee)
        
        # Update position filled slots
        position = frappe.get_doc("Work Study Position", self.work_study_position)
        position.update_filled_slots()
    
    def get_or_create_employee(self):
        """Get existing or create new Employee record for student"""
        student = frappe.get_doc("Student", self.student)
        
        # Check if employee exists
        existing = frappe.db.get_value("Employee", {
            "employee_name": student.student_name,
            "custom_student": self.student
        })
        
        if existing:
            return existing
        
        # Create new Employee
        employee = frappe.new_doc("Employee")
        employee.employee_name = student.student_name
        employee.first_name = student.first_name
        employee.last_name = getattr(student, 'last_name', '') or ''
        employee.gender = student.gender
        employee.date_of_birth = student.date_of_birth
        employee.personal_email = student.student_email_id
        employee.company = frappe.defaults.get_defaults().get("company")
        employee.status = "Active"
        employee.employment_type = "Part-time"
        
        # Link to student (custom field)
        if frappe.db.has_column("Employee", "custom_student"):
            employee.custom_student = self.student
        
        # Set department from position
        position = frappe.get_doc("Work Study Position", self.work_study_position)
        employee.department = position.department
        
        employee.insert(ignore_permissions=True)
        
        return employee.name
