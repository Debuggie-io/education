// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Study Assignment', {
    refresh: function(frm) {
        if (!frm.doc.__islocal && frm.doc.status === 'Active') {
            // Create Timesheet button
            frm.add_custom_button(__('Create Timesheet'), function() {
                frm.call('create_timesheet').then((r) => {
                    if (r.message) {
                        frappe.set_route('Form', 'Work Study Timesheet', r.message);
                    }
                });
            }, __('Actions'));
            
            // View Timesheets
            frm.add_custom_button(__('View Timesheets'), function() {
                frappe.set_route('List', 'Work Study Timesheet', {
                    work_study_assignment: frm.doc.name
                });
            }, __('Actions'));
            
            // Terminate Assignment
            frm.add_custom_button(__('Terminate'), function() {
                frappe.prompt({
                    label: 'Termination Reason',
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    reqd: 1
                }, function(values) {
                    frm.call('terminate_assignment', {
                        reason: values.reason
                    }).then(() => frm.reload_doc());
                }, __('Terminate Assignment'));
            }, __('Actions'));
            
            // Complete Assignment
            frm.add_custom_button(__('Mark Completed'), function() {
                frappe.confirm(
                    'Mark this assignment as completed?',
                    function() {
                        frm.call('complete_assignment').then(() => frm.reload_doc());
                    }
                );
            }, __('Actions'));
        }
        
        // Show summary
        if (frm.doc.total_hours_worked) {
            frm.dashboard.add_indicator(
                __('Hours Worked: {0}', [frm.doc.total_hours_worked]), 'blue'
            );
        }
        if (frm.doc.total_earnings) {
            frm.dashboard.add_indicator(
                __('Total Earnings: {0}', [format_currency(frm.doc.total_earnings)]), 'green'
            );
        }
    }
});
