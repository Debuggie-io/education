// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Landlord Property', {
    refresh: function(frm) {
        // Filter landlord to only approved ones
        frm.set_query('landlord', function() {
            return {
                filters: {
                    'status': 'Approved'
                }
            };
        });
        
        // Add vetting buttons
        if (frm.doc.status === 'Pending Vetting' || frm.doc.status === 'Under Review') {
            frm.add_custom_button(__('Approve Property'), function() {
                frappe.prompt({
                    fieldname: 'notes',
                    fieldtype: 'Small Text',
                    label: 'Vetting Notes'
                }, function(values) {
                    frappe.call({
                        method: 'frappe.client.set_value',
                        args: {
                            doctype: 'Landlord Property',
                            name: frm.doc.name,
                            fieldname: {
                                'status': 'Approved',
                                'vetted_by': frappe.session.user,
                                'vetting_date': frappe.datetime.get_today(),
                                'vetting_notes': values.notes
                            }
                        },
                        callback: function() {
                            frm.reload_doc();
                            frappe.show_alert({message: __('Property Approved'), indicator: 'green'});
                        }
                    });
                }, __('Vetting Notes'), __('Approve'));
            }, __('Vetting'));
            
            frm.add_custom_button(__('Reject Property'), function() {
                frappe.prompt({
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    label: 'Rejection Reason',
                    reqd: 1
                }, function(values) {
                    frappe.call({
                        method: 'frappe.client.set_value',
                        args: {
                            doctype: 'Landlord Property',
                            name: frm.doc.name,
                            fieldname: {
                                'status': 'Rejected',
                                'rejection_reason': values.reason,
                                'vetted_by': frappe.session.user,
                                'vetting_date': frappe.datetime.get_today()
                            }
                        },
                        callback: function() {
                            frm.reload_doc();
                        }
                    });
                }, __('Rejection Reason'), __('Reject'));
            }, __('Vetting'));
        }
        
        // Show current occupants
        if (frm.doc.status === 'Approved') {
            frappe.call({
                method: 'frappe.client.get_count',
                args: {
                    doctype: 'Off Campus Registration',
                    filters: {
                        listed_property: frm.doc.name,
                        docstatus: 1
                    }
                },
                callback: function(r) {
                    frm.dashboard.add_indicator(__('Current Students: {0}', [r.message || 0]), 'blue');
                }
            });
        }
    },
    
    total_units: function(frm) {
        frm.set_value('available_units', (frm.doc.total_units || 0) - (frm.doc.occupied_units || 0));
    },
    
    occupied_units: function(frm) {
        frm.set_value('available_units', (frm.doc.total_units || 0) - (frm.doc.occupied_units || 0));
    }
});
