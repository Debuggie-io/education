// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Study Payroll Entry', {
    refresh: function(frm) {
        // Fetch Timesheets button
        if (frm.doc.docstatus === 0 && frm.doc.payroll_period_start && frm.doc.payroll_period_end) {
            frm.add_custom_button(__('Fetch Timesheets'), function() {
                frappe.confirm(
                    'This will fetch all approved timesheets for the selected period. Continue?',
                    function() {
                        frm.call('fetch_timesheets').then(() => frm.reload_doc());
                    }
                );
            }).addClass('btn-primary');
        }
        
        // Retry Failed button
        if (frm.doc.docstatus === 1 && frm.doc.failed_count > 0) {
            frm.add_custom_button(__('Retry Failed Payments'), function() {
                frappe.confirm(
                    `Retry ${frm.doc.failed_count} failed payment(s)?`,
                    function() {
                        frm.call('retry_failed_payments').then(() => frm.reload_doc());
                    }
                );
            }).addClass('btn-warning');
        }
        
        // Summary indicators
        if (frm.doc.total_timesheets) {
            frm.dashboard.add_indicator(__('Timesheets: {0}', [frm.doc.total_timesheets]), 'blue');
        }
        if (frm.doc.total_students) {
            frm.dashboard.add_indicator(__('Students: {0}', [frm.doc.total_students]), 'blue');
        }
        if (frm.doc.total_amount) {
            frm.dashboard.add_indicator(__('Total: {0}', [format_currency(frm.doc.total_amount)]), 'green');
        }
        if (frm.doc.processed_count) {
            frm.dashboard.add_indicator(__('Processed: {0}', [frm.doc.processed_count]), 'green');
        }
        if (frm.doc.failed_count) {
            frm.dashboard.add_indicator(__('Failed: {0}', [frm.doc.failed_count]), 'red');
        }
    },
    
    onload: function(frm) {
        // Set default accounts
        if (!frm.doc.work_study_expense_account) {
            frappe.db.get_value('Company', frm.doc.company, 'default_expense_account', (r) => {
                if (r && r.default_expense_account) {
                    frm.set_value('work_study_expense_account', r.default_expense_account);
                }
            });
        }
        
        if (!frm.doc.cost_center) {
            frappe.db.get_value('Company', frm.doc.company, 'cost_center', (r) => {
                if (r && r.cost_center) {
                    frm.set_value('cost_center', r.cost_center);
                }
            });
        }
    }
});
