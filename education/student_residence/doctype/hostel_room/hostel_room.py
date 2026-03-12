# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HostelRoom(Document):
    def validate(self):
        self.update_available_beds()
    
    def update_available_beds(self):
        """Calculate available beds"""
        self.available_beds = (self.room_capacity or 0) - (self.occupied_beds or 0)
    
    def before_save(self):
        # Update hostel statistics
        pass
    
    def on_update(self):
        self.update_hostel_stats()
    
    def on_trash(self):
        self.update_hostel_stats()
    
    def update_hostel_stats(self):
        """Update total rooms and capacity in parent hostel"""
        if self.hostel:
            hostel = frappe.get_doc("Hostel", self.hostel)
            
            # Get room statistics
            stats = frappe.db.sql("""
                SELECT 
                    COUNT(*) as total_rooms,
                    SUM(room_capacity) as total_capacity,
                    SUM(occupied_beds) as occupied_beds
                FROM `tabHostel Room`
                WHERE hostel = %s
            """, self.hostel, as_dict=True)[0]
            
            hostel.total_rooms = stats.total_rooms or 0
            hostel.total_capacity = stats.total_capacity or 0
            hostel.occupied_beds = stats.occupied_beds or 0
            hostel.save(ignore_permissions=True)
