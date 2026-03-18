// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Study Timesheet', {
    refresh: function(frm) {
        // Approve button
        if (frm.doc.status === 'Pending Approval' && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Approve'), function() {
                frappe.prompt({
                    label: 'Comments',
                    fieldname: 'comments',
                    fieldtype: 'Small Text'
                }, function(values) {
                    frm.call('approve_timesheet', {
                        comments: values.comments
                    }).then(() => frm.reload_doc());
                }, __('Approve Timesheet'));
            }, __('Actions')).addClass('btn-primary');
            
            frm.add_custom_button(__('Reject'), function() {
                frappe.prompt({
                    label: 'Rejection Reason',
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    reqd: 1
                }, function(values) {
                    frm.call('reject_timesheet', {
                        reason: values.reason
                    }).then(() => frm.reload_doc());
                }, __('Actions')).addClass('btn-danger');
            }, __('Actions'));
        }
        
        // Process Payment button
        if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Process Payment'), function() {
                frappe.confirm(
                    __('Credit {0} to student wallet?', [format_currency(frm.doc.total_amount)]),
                    function() {
                        frm.call('process_payment').then((r) => {
                            frm.reload_doc();
                            if (r.message) {
                                frappe.set_route('Form', 'Journal Entry', r.message);
                            }
                        });
                    }
                );
            }, __('Actions')).addClass('btn-success');
        }
        
        // Summary indicators
        if (frm.doc.total_hours) {
            frm.dashboard.add_indicator(__('Hours: {0}', [frm.doc.total_hours]), 'blue');
        }
        if (frm.doc.total_amount) {
            frm.dashboard.add_indicator(__('Amount: {0}', [format_currency(frm.doc.total_amount)]), 'green');
        }
        if (frm.doc.hours_remaining !== undefined && frm.doc.hours_remaining < 0) {
            frm.dashboard.add_indicator(__('Over Limit!'), 'red');
        }
    },
    
    work_study_assignment: function(frm) {
        // Set default week dates
        if (frm.doc.work_study_assignment && !frm.doc.week_start_date) {
            // Get Monday of current week
            let today = frappe.datetime.get_today();
            let day = new Date(today).getDay();
            let diff = day === 0 ? 6 : day - 1;
            let monday = frappe.datetime.add_days(today, -diff);
            let sunday = frappe.datetime.add_days(monday, 6);
            
            frm.set_value('week_start_date', monday);
            frm.set_value('week_end_date', sunday);
        }
    }
});

frappe.ui.form.on('Work Study Time Log', {
    start_time: function(frm, cdt, cdn) {
        calculate_log_hours(frm, cdt, cdn);
    },
    
    end_time: function(frm, cdt, cdn) {
        calculate_log_hours(frm, cdt, cdn);
    },
    
    time_logs_remove: function(frm) {
        calculate_totals(frm);
    }
});

function calculate_log_hours(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.start_time && row.end_time) {
        let start = moment(row.start_time, 'HH:mm:ss');
        let end = moment(row.end_time, 'HH:mm:ss');
        let hours = end.diff(start, 'hours', true);
        
        if (hours < 0) hours += 24; // Handle overnight
        
        frappe.model.set_value(cdt, cdn, 'hours', Math.round(hours * 100) / 100);
        calculate_totals(frm);
    }
}

function calculate_totals(frm) {
    let total = 0;
    (frm.doc.time_logs || []).forEach(row => {
        total += flt(row.hours);
    });
    
    frm.set_value('total_hours', Math.round(total * 100) / 100);
    frm.set_value('total_amount', flt(total * flt(frm.doc.hourly_rate)));
    frm.set_value('hours_remaining', flt(frm.doc.max_hours_per_week) - total);
}
