# Copyright (c) 2026, UEAB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class LandlordProperty(Document):
    def validate(self):
        self.validate_landlord_status()
        self.calculate_available_units()
    
    def validate_landlord_status(self):
        """Only approved landlords can list properties"""
        if self.landlord:
            status = frappe.db.get_value("Landlord", self.landlord, "status")
            if status != "Approved":
                frappe.throw(_("Only approved landlords can list properties. Current status: {0}").format(status))
    
    def calculate_available_units(self):
        """Calculate available units"""
        self.available_units = (self.total_units or 0) - (self.occupied_units or 0)
    
    def on_update(self):
        """Update available units when occupancy changes"""
        self.calculate_available_units()
