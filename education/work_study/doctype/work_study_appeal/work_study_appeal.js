// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Study Appeal', {
    refresh: function(frm) {
        if (['Pending Review', 'Under Review'].includes(frm.doc.status) && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Approve Appeal'), function() {
                frappe.prompt({
                    label: 'Comments',
                    fieldname: 'comments',
                    fieldtype: 'Text Editor'
                }, function(values) {
                    frm.call('approve_appeal', {
                        comments: values.comments
                    }).then(() => frm.reload_doc());
                }, __('Approve Appeal'));
            }, __('Actions')).addClass('btn-primary');
            
            frm.add_custom_button(__('Reject Appeal'), function() {
                frappe.prompt({
                    label: 'Rejection Reason',
                    fieldname: 'comments',
                    fieldtype: 'Text Editor',
                    reqd: 1
                }, function(values) {
                    frm.call('reject_appeal', {
                        comments: values.comments
                    }).then(() => frm.reload_doc());
                }, __('Actions')).addClass('btn-danger');
            }, __('Actions'));
        }
    }
});
