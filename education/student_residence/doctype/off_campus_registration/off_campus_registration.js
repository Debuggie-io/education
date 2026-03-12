// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Off Campus Registration', {
    refresh: function(frm) {
        // Filter listed_property by gender
        frm.set_query('listed_property', function() {
            let gender_filter = frm.doc.gender === 'Male' ? 'Male Only' : 'Female Only';
            return {
                filters: {
                    'status': 'Approved',
                    'gender_preference': ['in', [gender_filter, 'Mixed']]
                }
            };
        });
        
        // Add verification button for admin
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Submitted') {
            frm.add_custom_button(__('Verify Registration'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Off Campus Registration',
                        name: frm.doc.name,
                        fieldname: {
                            'status': 'Verified',
                            'verified_by': frappe.session.user,
                            'verification_date': frappe.datetime.get_today()
                        }
                    },
                    callback: function() {
                        frm.reload_doc();
                        frappe.show_alert({message: __('Registration Verified'), indicator: 'green'});
                    }
                });
            }, __('Actions'));
        }
        
        // Add continuation confirmation for students
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Verified') {
            frm.add_custom_button(__('Confirm Continuation'), function() {
                frm.call('confirm_continuation').then(() => {
                    frm.reload_doc();
                });
            }, __('End of Semester'));
        }
    },
    
    student: function(frm) {
        // Clear listed property when student changes
        frm.set_value('listed_property', '');
    },
    
    listed_property: function(frm) {
        if (frm.doc.listed_property) {
            // Auto-fill from listed property
            frappe.db.get_doc('Landlord Property', frm.doc.listed_property).then(prop => {
                frm.set_value('plot_number', prop.plot_number || '');
                frm.set_value('street_road', prop.street_address || '');
                frm.set_value('area_estate', prop.area_name || '');
                frm.set_value('landmark', prop.landmark || '');
                frm.set_value('is_approved_property', 1);
                
                // Get landlord details
                if (prop.landlord) {
                    frappe.db.get_doc('Landlord', prop.landlord).then(landlord => {
                        frm.set_value('landlord_name', landlord.landlord_name);
                        frm.set_value('landlord_phone', landlord.phone);
                        frm.set_value('landlord_alternative_phone', landlord.alternative_phone);
                        frm.set_value('landlord_email', landlord.email);
                    });
                }
            });
        } else {
            frm.set_value('is_approved_property', 0);
        }
    },
    
    // Build full address
    plot_number: function(frm) { build_full_address(frm); },
    door_number: function(frm) { build_full_address(frm); },
    street_road: function(frm) { build_full_address(frm); },
    area_estate: function(frm) { build_full_address(frm); }
});

function build_full_address(frm) {
    let parts = [];
    if (frm.doc.door_number) parts.push('Door ' + frm.doc.door_number);
    if (frm.doc.plot_number) parts.push('Plot ' + frm.doc.plot_number);
    if (frm.doc.street_road) parts.push(frm.doc.street_road);
    if (frm.doc.area_estate) parts.push(frm.doc.area_estate);
    
    frm.set_value('full_address', parts.join(', '));
}
