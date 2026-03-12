import frappe
from frappe.model.document import Document
from frappe import _

class Election(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_eligible_voters()
    
    def validate_dates(self):
        """Validate election timeline"""
        if self.nomination_start_date and self.nomination_end_date:
            if self.nomination_end_date < self.nomination_start_date:
                frappe.throw(_("Nomination end date cannot be before start date"))
        
        if self.campaign_start_date and self.campaign_end_date:
            if self.campaign_end_date < self.campaign_start_date:
                frappe.throw(_("Campaign end date cannot be before start date"))
        
        if self.voting_start_date and self.voting_end_date:
            if self.voting_end_date < self.voting_start_date:
                frappe.throw(_("Voting end date cannot be before start date"))
        
        # Ensure logical order
        if self.nomination_end_date and self.voting_start_date:
            if self.voting_start_date < self.nomination_end_date:
                frappe.throw(_("Voting cannot start before nomination ends"))
    
    def calculate_eligible_voters(self):
        """Calculate total eligible voters based on criteria"""
        filters = {"enabled": 1}
        
        # Get all active students
        students = frappe.get_all("Student", filters=filters, pluck="name")
        
        eligible_count = 0
        for student in students:
            if self.is_student_eligible_to_vote(student):
                eligible_count += 1
        
        self.total_eligible_voters = eligible_count
        
        # Calculate turnout if votes exist
        if self.total_votes_cast and self.total_eligible_voters:
            self.voter_turnout_percentage = (self.total_votes_cast / self.total_eligible_voters) * 100
    
    def is_student_eligible_to_vote(self, student_id):
        """Check if a student is eligible to vote"""
        # Check GPA requirement
        if self.minimum_gpa_to_vote and self.minimum_gpa_to_vote > 0:
            student_gpa = frappe.db.get_value("Student", student_id, "custom_gpa") or 0
            if student_gpa < self.minimum_gpa_to_vote:
                return False
        
        # Check disciplinary status
        if not self.allow_disciplinary_cases:
            if frappe.db.exists("DocType", "Student Conduct Case"):
                active_cases = frappe.db.count(
                    "Student Conduct Case",
                    {"student": student_id, "status": ["in", ["Open", "Under Investigation"]]}
                )
                if active_cases > 0:
                    return False
        
        # Check program eligibility
        if self.eligible_programs and len(self.eligible_programs) > 0:
            student_program = frappe.db.get_value("Student", student_id, "program")
            eligible_program_list = [p.program for p in self.eligible_programs]
            if student_program not in eligible_program_list:
                return False
        
        return True
    
    @frappe.whitelist()
    def open_nominations(self):
        """Open election for nominations"""
        if self.status not in ["Draft"]:
            frappe.throw(_("Can only open nominations from Draft status"))
        
        self.status = "Nomination Open"
        self.save()
        frappe.msgprint(_("Nominations are now open"))
    
    @frappe.whitelist()
    def close_nominations(self):
        """Close nominations"""
        if self.status != "Nomination Open":
            frappe.throw(_("Nominations are not currently open"))
        
        self.status = "Nomination Closed"
        self.save()
        frappe.msgprint(_("Nominations are now closed"))
    
    @frappe.whitelist()
    def start_campaign(self):
        """Start campaign period"""
        if self.status != "Nomination Closed":
            frappe.throw(_("Nominations must be closed first"))
        
        self.status = "Campaigning"
        self.save()
        frappe.msgprint(_("Campaign period has started"))
    
    @frappe.whitelist()
    def open_voting(self):
        """Open election for voting"""
        if self.status not in ["Nomination Closed", "Campaigning"]:
            frappe.throw(_("Cannot open voting from current status"))
        
        # Ensure there are approved candidates
        approved_candidates = frappe.db.count(
            "Candidate Nomination",
            {"election": self.name, "vetting_status": "Approved", "docstatus": 1}
        )
        
        if approved_candidates == 0:
            frappe.throw(_("No approved candidates found. Cannot open voting."))
        
        self.status = "Voting Open"
        self.save()
        frappe.msgprint(_("Voting is now open"))
    
    @frappe.whitelist()
    def close_voting(self):
        """Close voting"""
        if self.status != "Voting Open":
            frappe.throw(_("Voting is not currently open"))
        
        self.status = "Voting Closed"
        self.save()
        frappe.msgprint(_("Voting is now closed"))
    
    @frappe.whitelist()
    def declare_results(self):
        """Declare election results"""
        if self.status != "Voting Closed":
            frappe.throw(_("Voting must be closed first"))
        
        self.status = "Results Declared"
        self.results_declaration_date = frappe.utils.now_datetime()
        self.save()
        frappe.msgprint(_("Results have been declared"))
    
    @frappe.whitelist()
    def get_results(self):
        """Get election results by position"""
        results = {}
        
        positions = frappe.get_all(
            "Election Position",
            filters={"election": self.name},
            fields=["name", "position"]
        )
        
        for pos in positions:
            # Get candidates and their votes
            candidates = frappe.db.sql("""
                SELECT 
                    cn.name,
                    cn.student_name,
                    cn.campaign_slogan,
                    COUNT(eb.name) as vote_count
                FROM `tabCandidate Nomination` cn
                LEFT JOIN `tabEncrypted Ballot` eb ON eb.voted_for = cn.name AND eb.docstatus != 2
                WHERE cn.election_position = %s
                AND cn.vetting_status = 'Approved'
                AND cn.docstatus = 1
                GROUP BY cn.name
                ORDER BY vote_count DESC
            """, pos.name, as_dict=True)
            
            results[pos.position] = candidates
        
        return results
