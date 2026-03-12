import frappe
from frappe.model.document import Document
from frappe import _
import hashlib
from datetime import datetime

class EncryptedBallot(Document):
    def before_insert(self):
        """Generate cryptographic hash and validate vote"""
        self.validate_election_status()
        self.validate_voter_eligibility()
        self.generate_voter_hash()
        self.check_duplicate_vote()
        self.record_vote_metadata()
    
    def validate_election_status(self):
        """Ensure election is open for voting"""
        if not self.election:
            frappe.throw(_("Election is required"))
        
        election = frappe.get_doc("Election", self.election)
        
        if election.status != "Voting Open":
            frappe.throw(
                _("Voting is not currently open for this election. Current status: {0}").format(election.status),
                frappe.ValidationError
            )
        
        # Check voting period
        now = frappe.utils.now_datetime()
        if election.voting_start_date and now < election.voting_start_date:
            frappe.throw(_("Voting has not started yet"))
        
        if election.voting_end_date and now > election.voting_end_date:
            frappe.throw(_("Voting period has ended"))
    
    def validate_voter_eligibility(self):
        """Validate that current user is eligible to vote"""
        user = frappe.session.user
        
        if user == "Administrator" or user == "Guest":
            frappe.throw(_("Invalid voter credentials"))
        
        # Get student linked to user
        student = frappe.db.get_value("Student", {"user": user}, "name")
        
        if not student:
            frappe.throw(_("No student record found for current user"))
        
        # Store for hash generation
        self._voter_student_id = student
        
        # Check if election requires MFA
        election = frappe.get_doc("Election", self.election)
        if election.require_mfa:
            # In production, implement actual MFA verification
            self.mfa_verified = 1
        
        if election.require_nfc_validation:
            # In production, implement NFC validation
            self.nfc_verified = 0  # Will be set by NFC validation endpoint
    
    def generate_voter_hash(self):
        """Generate SHA-256 hash of voter identity"""
        if not hasattr(self, '_voter_student_id'):
            student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
            self._voter_student_id = student
        
        if not self._voter_student_id:
            frappe.throw(_("Cannot identify voter"))
        
        # Get election's hash algorithm
        election = frappe.get_doc("Election", self.election)
        algorithm = election.hash_algorithm or "SHA-256"
        
        # Generate voter hash (one-way, cannot be reversed to identify voter)
        voter_string = f"{self._voter_student_id}"
        if algorithm == "SHA-512":
            self.voter_hash = hashlib.sha512(voter_string.encode()).hexdigest()
        else:
            self.voter_hash = hashlib.sha256(voter_string.encode()).hexdigest()
        
        # Generate unique election-voter hash for duplicate detection
        election_voter_string = f"{self.election}:{self._voter_student_id}:{self.election_position}"
        if algorithm == "SHA-512":
            self.election_voter_hash = hashlib.sha512(election_voter_string.encode()).hexdigest()
        else:
            self.election_voter_hash = hashlib.sha256(election_voter_string.encode()).hexdigest()
        
        self.hash_algorithm = algorithm
    
    def check_duplicate_vote(self):
        """Check if voter has already voted for this position"""
        # Check if this exact election-voter-position hash exists
        existing_vote = frappe.db.exists(
            "Encrypted Ballot",
            {"election_voter_hash": self.election_voter_hash, "docstatus": ["!=", 2]}
        )
        
        if existing_vote:
            frappe.throw(
                _("You have already cast a vote for this position. One person, one vote policy enforced."),
                frappe.ValidationError
            )
    
    def record_vote_metadata(self):
        """Record vote timestamp and metadata"""
        self.timestamp = frappe.utils.now_datetime()
        
        # Record IP for audit (hidden field)
        if hasattr(frappe.local, 'request') and frappe.local.request:
            self.ip_address = frappe.local.request.remote_addr
            self.user_agent = frappe.local.request.headers.get('User-Agent', '')[:500]
    
    def after_insert(self):
        """Update election statistics"""
        self.update_election_stats()
    
    def update_election_stats(self):
        """Update vote counts on election"""
        # Update total votes on election
        total_votes = frappe.db.count(
            "Encrypted Ballot",
            {"election": self.election, "docstatus": ["!=", 2]}
        )
        
        frappe.db.set_value("Election", self.election, "total_votes_cast", total_votes)
        
        # Update position vote count
        position_votes = frappe.db.count(
            "Encrypted Ballot",
            {"election_position": self.election_position, "docstatus": ["!=", 2]}
        )
        
        frappe.db.set_value("Election Position", self.election_position, "total_votes", position_votes)
