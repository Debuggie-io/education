import frappe
from frappe.model.document import Document
from frappe import _

class CandidateNomination(Document):
    def validate(self):
        self.fetch_student_details()
        self.perform_automated_vetting()
    
    def fetch_student_details(self):
        """Fetch student details for vetting"""
        if self.student:
            student = frappe.get_doc("Student", self.student)
            
            # Get GPA from student record (assuming there's a gpa field or we calculate it)
            self.current_gpa = self.get_student_gpa(self.student)
            
            # Get year of study
            self.year_of_study = self.get_year_of_study(self.student)
            
            # Get disciplinary status
            self.disciplinary_status = self.get_disciplinary_status(self.student)
    
    def get_student_gpa(self, student_id):
        """Get student's current GPA"""
        # Try to get from Student record first
        gpa = frappe.db.get_value("Student", student_id, "custom_gpa")
        if gpa:
            return gpa
        
        # If no custom_gpa field, try to calculate from Assessment Results
        # This is a simplified calculation - adjust based on your actual data model
        return 0.0
    
    def get_year_of_study(self, student_id):
        """Get student's year of study"""
        # Try to get from program enrollment
        enrollment = frappe.db.get_value(
            "Program Enrollment",
            {"student": student_id, "docstatus": 1},
            ["academic_year", "enrollment_date"],
            as_dict=True,
            order_by="enrollment_date desc"
        )
        
        if enrollment:
            # Calculate year based on enrollment
            return 1  # Simplified - adjust based on your logic
        return 1
    
    def get_disciplinary_status(self, student_id):
        """Check if student has active disciplinary cases"""
        # Check if Student Conduct Case doctype exists
        if frappe.db.exists("DocType", "Student Conduct Case"):
            active_cases = frappe.db.count(
                "Student Conduct Case",
                {"student": student_id, "status": ["in", ["Open", "Under Investigation", "Pending Hearing"]]}
            )
            if active_cases > 0:
                return "Active Case"
        
        return "Clear"
    
    def perform_automated_vetting(self):
        """Perform automated eligibility vetting"""
        if not self.election:
            return
        
        election = frappe.get_doc("Election", self.election)
        remarks = []
        
        # Check GPA eligibility
        min_gpa = election.minimum_gpa_to_contest or 0
        
        # Check if position has override
        if self.election_position:
            position = frappe.get_doc("Election Position", self.election_position)
            if position.override_election_gpa and position.minimum_gpa:
                min_gpa = position.minimum_gpa
        
        if self.current_gpa and self.current_gpa >= min_gpa:
            self.gpa_eligible = 1
        else:
            self.gpa_eligible = 0
            remarks.append(f"GPA {self.current_gpa or 0} is below minimum requirement of {min_gpa}")
        
        # Check disciplinary eligibility
        if self.disciplinary_status == "Clear" or election.allow_disciplinary_cases:
            self.disciplinary_eligible = 1
        else:
            self.disciplinary_eligible = 0
            remarks.append(f"Student has {self.disciplinary_status} - not eligible to contest")
        
        # Update vetting remarks
        if remarks:
            self.vetting_remarks = "\n".join(remarks)
            self.vetting_status = "Pending"
        else:
            self.vetting_remarks = "All automated checks passed"
    
    def before_submit(self):
        """Block submission if not eligible"""
        if not self.gpa_eligible:
            frappe.throw(
                _("Cannot submit nomination. Student does not meet GPA requirements."),
                frappe.ValidationError
            )
        
        if not self.disciplinary_eligible:
            frappe.throw(
                _("Cannot submit nomination. Student has active disciplinary cases."),
                frappe.ValidationError
            )
        
        # Set vetted info
        self.vetted_by = frappe.session.user
        self.vetted_on = frappe.utils.now_datetime()
        self.vetting_status = "Approved"
