// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Room Booking Application', {
    refresh: function(frm) {
        // Filter hostel by student gender
        frm.set_query('preferred_hostel', function() {
            if (frm.doc.gender) {
                let hostel_type = frm.doc.gender === 'Male' ? 'Mens Hostel' : 'Ladies Hostel';
                return {
                    filters: {
                        'hostel_type': hostel_type,
                        'is_active': 1
                    }
                };
            }
            return { filters: { 'is_active': 1 } };
        });
        
        // Add Allocate Room button for admins
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Allocate Room'), function() {
                show_allocation_dialog(frm);
            }, __('Actions'));
            
            frm.add_custom_button(__('Approve'), function() {
                frappe.db.set_value(frm.doctype, frm.docname, 'status', 'Approved')
                    .then(() => frm.reload_doc());
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
                            doctype: frm.doctype,
                            name: frm.docname,
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
        }
    },
    
    student: function(frm) {
        // Clear preferred hostel when student changes
        frm.set_value('preferred_hostel', '');
    }
});

function show_allocation_dialog(frm) {
    let hostel_type = frm.doc.gender === 'Male' ? 'Mens Hostel' : 'Ladies Hostel';
    
    let d = new frappe.ui.Dialog({
        title: __('Allocate Room'),
        fields: [
            {
                fieldname: 'hostel',
                fieldtype: 'Link',
                label: 'Hostel',
                options: 'Hostel',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'hostel_type': hostel_type,
                            'is_active': 1
                        }
                    };
                }
            },
            {
                fieldname: 'room',
                fieldtype: 'Link',
                label: 'Room',
                options: 'Hostel Room',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'hostel': d.get_value('hostel'),
                            'is_available': 1
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Allocate'),
        primary_action: function(values) {
            frappe.call({
                method: 'allocate_room',
                doc: frm.doc,
                args: {
                    hostel: values.hostel,
                    room: values.room
                },
                callback: function(r) {
                    d.hide();
                    frm.reload_doc();
                }
            });
        }
    });
    
    d.show();
}
