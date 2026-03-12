// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Landlord', {
    refresh: function(frm) {
        // Add Approve/Reject buttons for admin
        if (frm.doc.status === 'Pending' || frm.doc.status === 'Under Review') {
            frm.add_custom_button(__('Approve'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Landlord',
                        name: frm.doc.name,
                        fieldname: {
                            'status': 'Approved',
                            'approved_by': frappe.session.user,
                            'approval_date': frappe.datetime.get_today()
                        }
                    },
                    callback: function() {
                        frm.reload_doc();
                        frappe.show_alert({message: __('Landlord Approved'), indicator: 'green'});
                    }
                });
            }, __('Actions'));
            
            frm.add_custom_button(__('Reject'), function() {
                frappe.prompt({
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    label: 'Rejection Reason',
                    reqd: 1
                }, function(values) {
                    frappe.call({
                        method: 'frappe.client.set_value',
                        args: {
                            doctype: 'Landlord',
                            name: frm.doc.name,
                            fieldname: {
                                'status': 'Rejected',
                                'rejection_reason': values.reason
                            }
                        },
                        callback: function() {
                            frm.reload_doc();
                        }
                    });
                }, __('Rejection Reason'), __('Reject'));
            }, __('Actions'));
            
            frm.add_custom_button(__('Mark Under Review'), function() {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'Landlord',
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'Under Review'
                    },
                    callback: function() {
                        frm.reload_doc();
                    }
                });
            }, __('Actions'));
        }
        
        // Show properties count
        if (!frm.is_new() && frm.doc.status === 'Approved') {
            frappe.call({
                method: 'frappe.client.get_count',
                args: {
                    doctype: 'Landlord Property',
                    filters: {landlord: frm.doc.name}
                },
                callback: function(r) {
                    frm.dashboard.add_indicator(__('Properties: {0}', [r.message]), 'blue');
                }
            });
        }
    }
});
