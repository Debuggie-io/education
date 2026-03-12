// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Residence', {
    refresh: function(frm) {
        // Set query for hostel based on student gender
        frm.set_query('hostel', function() {
            if (frm.doc.student) {
                return {
                    filters: {
                        'is_active': 1
                    }
                };
            }
        });
        
        // Set query for hostel_room based on selected hostel
        frm.set_query('hostel_room', function() {
            return {
                filters: {
                    'hostel': frm.doc.hostel,
                    'is_available': 1
                }
            };
        });
    },
    
    student: function(frm) {
        // When student changes, filter hostels by gender
        if (frm.doc.student) {
            frappe.db.get_value('Student', frm.doc.student, 'gender', function(r) {
                if (r && r.gender) {
                    let hostel_type = r.gender === 'Male' ? 'Mens Hostel' : 'Ladies Hostel';
                    frm.set_query('hostel', function() {
                        return {
                            filters: {
                                'hostel_type': hostel_type,
                                'is_active': 1
                            }
                        };
                    });
                    // Clear hostel and room if gender changed
                    frm.set_value('hostel', '');
                    frm.set_value('hostel_room', '');
                }
            });
        }
    },
    
    hostel: function(frm) {
        // Clear room when hostel changes
        frm.set_value('hostel_room', '');
        
        // Update room filter
        frm.set_query('hostel_room', function() {
            return {
                filters: {
                    'hostel': frm.doc.hostel,
                    'is_available': 1
                }
            };
        });
    },
    
    residence_type: function(frm) {
        // Clear hostel fields if off campus
        if (frm.doc.residence_type === 'Off Campus') {
            frm.set_value('hostel', '');
            frm.set_value('hostel_room', '');
        }
    }
});
