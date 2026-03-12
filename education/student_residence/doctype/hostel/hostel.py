# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Hostel(Document):
    def on_update(self):
        self.update_ra_permissions()
    
    def update_ra_permissions(self):
        """Add User Permissions for RA and Assistant RA to limit access to this hostel"""
        # Clear old permissions for this hostel
        frappe.db.delete("User Permission", {
            "allow": "Hostel",
            "for_value": self.name
        })
        
        # Add permission for Residence Administrator
        if self.residence_administrator:
            self.add_user_permission(self.residence_administrator)
        
        # Add permission for Assistant RA
        if self.assistant_ra:
            self.add_user_permission(self.assistant_ra)
        
        frappe.db.commit()
    
    def add_user_permission(self, user):
        """Add user permission for a specific user"""
        if not frappe.db.exists("User Permission", {
            "user": user,
            "allow": "Hostel",
            "for_value": self.name
        }):
            perm = frappe.new_doc("User Permission")
            perm.user = user
            perm.allow = "Hostel"
            perm.for_value = self.name
            perm.apply_to_all_doctypes = 0
            perm.insert(ignore_permissions=True)
            frappe.msgprint(f"User Permission added for {user} to access {self.name}")
    
    def on_trash(self):
        """Remove user permissions when hostel is deleted"""
        frappe.db.delete("User Permission", {
            "allow": "Hostel",
            "for_value": self.name
        })
