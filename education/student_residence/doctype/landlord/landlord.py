# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class Landlord(Document):
    def validate(self):
        self.validate_id_number()
    
    def validate_id_number(self):
        """Ensure ID number is unique"""
        if self.id_number:
            existing = frappe.db.exists("Landlord", {
                "id_number": self.id_number,
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(_("A landlord with ID Number {0} already exists").format(self.id_number))
    
    def on_update(self):
        """Create user account for landlord if approved"""
        if self.status == "Approved" and self.email and not self.user:
            self.create_user_account()
    
    def create_user_account(self):
        """Create a portal user for the landlord"""
        if frappe.db.exists("User", self.email):
            self.user = self.email
            return
        
        user = frappe.new_doc("User")
        user.email = self.email
        user.first_name = self.landlord_name.split()[0]
        user.last_name = " ".join(self.landlord_name.split()[1:]) if len(self.landlord_name.split()) > 1 else ""
        user.send_welcome_email = 1
        user.user_type = "Website User"
        user.append("roles", {"role": "Landlord"})
        user.insert(ignore_permissions=True)
        
        self.user = user.name
        frappe.db.set_value("Landlord", self.name, "user", user.name)
        frappe.msgprint(_("User account created for {0}").format(self.landlord_name))
