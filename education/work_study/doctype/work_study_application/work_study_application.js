// Copyright (c) 2026, UEAB and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Study Application', {
    refresh: function(frm) {
        // HOD Approval Button
        if (frm.doc.status === 'Pending HOD Approval' && !frm.doc.__islocal) {
            frm.add_custom_button(__('Approve (HOD)'), function() {
                frappe.prompt({
                    label: 'Comments',
                    fieldname: 'comments',
                    fieldtype: 'Small Text'
                }, function(values) {
                    frm.call('approve_hod', {
                        comments: values.comments
                    }).then(() => frm.reload_doc());
                }, __('HOD Approval'));
            }, __('Actions')).addClass('btn-primary');
        }
        
        // Dean Approval Button
        if (frm.doc.status === 'Pending Dean Approval' && !frm.doc.__islocal) {
            frm.add_custom_button(__('Approve (Dean)'), function() {
                frappe.prompt({
                    label: 'Comments',
                    fieldname: 'comments',
                    fieldtype: 'Small Text'
                }, function(values) {
                    frm.call('approve_dean', {
                        comments: values.comments
                    }).then(() => frm.reload_doc());
                }, __('Dean Approval'));
            }, __('Actions')).addClass('btn-primary');
        }
        
        // Reject Button
        if (['Pending HOD Approval', 'Pending Dean Approval', 'Appeal Under Review'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Reject'), function() {
                frappe.prompt({
                    label: 'Rejection Reason',
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    reqd: 1
                }, function(values) {
                    frm.call('reject_application', {
                        reason: values.reason
                    }).then(() => frm.reload_doc());
                }, __('Reject Application'));
            }, __('Actions')).addClass('btn-danger');
        }
        
        // Appeal Button
        if (['Screening Failed', 'Rejected'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Submit Appeal'), function() {
                frappe.confirm(
                    'Are you sure you want to submit an appeal?',
                    function() {
                        frm.call('submit_appeal').then((r) => {
                            if (r.message) {
                                frappe.set_route('Form', 'Work Study Appeal', r.message);
                            }
                        });
                    }
                );
            }, __('Actions'));
        }
        
        // Show eligibility status
        if (frm.doc.is_eligible) {
            frm.dashboard.set_headline_alert(
                '<div class="alert alert-success">Eligible for Work Study</div>'
            );
        } else if (frm.doc.screening_notes && frm.doc.docstatus === 1) {
            frm.dashboard.set_headline_alert(
                '<div class="alert alert-warning">Not Eligible: ' + frm.doc.screening_notes + '</div>'
            );
        }
    },
    
    student: function(frm) {
        // Re-fetch data when student changes
        if (frm.doc.student) {
            frm.trigger('fetch_student_data');
        }
    },
    
    work_study_position: function(frm) {
        // Re-run screening when position changes
        if (frm.doc.work_study_position && frm.doc.student) {
            frm.trigger('validate');
        }
    }
});
