frappe.pages['semester-registration'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Semester Registration',
        single_column: true
    });
    
    wrapper.page = page;
    page.selected_courses = [];
    
    page.set_secondary_action('Refresh', function() {
        load_registration(page);
    });
    
    load_registration(page);
}

function load_registration(page) {
    page.main.html('<div class="text-center py-5"><i class="fa fa-spinner fa-spin fa-2x"></i><p class="mt-2">Loading...</p></div>');
    
    frappe.call({
        method: 'education.api.registration.get_registration_status',
        callback: function(r) {
            if (r.message) {
                page.data = r.message;
                render_page(page);
            }
        }
    });
}

function render_page(page) {
    var d = page.data;
    
    if (!d.student) {
        page.main.html('<div class="text-center py-5"><i class="fa fa-user-times fa-3x text-muted"></i><h4 class="mt-3">No Student Record</h4><p class="text-muted">Your account is not linked to a student record.</p></div>');
        return;
    }
    
    if (!d.registration_open) {
        page.main.html('<div class="text-center py-5"><i class="fa fa-calendar-times-o fa-3x text-muted"></i><h4 class="mt-3">Registration Closed</h4><p class="text-muted">' + (d.message || 'Registration is not open.') + '</p></div>');
        return;
    }
    
    if (d.registration) {
        render_existing(page, d);
    } else {
        render_new(page, d);
    }
}

function render_existing(page, d) {
    var reg = d.registration;
    var status_colors = {
        'Draft': 'secondary', 'Pending Finance Approval': 'warning',
        'Pending HOD Approval': 'info', 'Pending Registrar Approval': 'primary',
        'Approved': 'success', 'Rejected': 'danger'
    };
    
    var html = '<div class="container py-4" style="max-width:900px">';
    html += '<h3>Semester Registration</h3><p class="text-muted">' + d.academic_term + '</p>';
    
    html += '<div class="card mb-4"><div class="card-body">';
    html += '<div class="row"><div class="col-md-8">';
    html += '<h5>' + d.student_name + '</h5>';
    html += '<p class="mb-1">Program: ' + reg.program + '</p>';
    html += '<p class="mb-0">Credits: <strong>' + (reg.total_credits || 0) + '</strong> | Courses: <strong>' + (reg.total_courses || 0) + '</strong></p>';
    html += '</div><div class="col-md-4 text-right">';
    html += '<span class="badge badge-' + (status_colors[reg.registration_status] || 'secondary') + '" style="font-size:14px;padding:8px 12px">' + reg.registration_status + '</span>';
    html += '</div></div></div></div>';
    
    html += '<div class="card mb-4"><div class="card-header">Approval Progress</div><div class="card-body">';
    html += '<div class="row text-center">';
    
    var steps = [
        {name: 'Finance', status: reg.finance_status},
        {name: 'HOD', status: reg.hod_status},
        {name: 'Registrar', status: reg.registrar_status}
    ];
    
    steps.forEach(function(s) {
        var icon = s.status === 'Approved' ? 'check-circle text-success' : (s.status === 'Rejected' ? 'times-circle text-danger' : 'clock-o text-muted');
        html += '<div class="col-md-4"><i class="fa fa-' + icon + ' fa-2x"></i><div class="mt-2"><strong>' + s.name + '</strong></div><small>' + s.status + '</small></div>';
    });
    
    html += '</div></div></div>';
    
    html += '<div class="card mb-4"><div class="card-header">Selected Courses</div>';
    html += '<table class="table mb-0"><thead><tr><th>Code</th><th>Course</th><th>Credits</th><th>Schedule</th></tr></thead><tbody>';
    
    (reg.courses || []).forEach(function(c) {
        html += '<tr><td><strong>' + (c.course_code || '') + '</strong></td>';
        html += '<td>' + (c.course_name || c.course) + '</td>';
        html += '<td>' + (c.credit_hours || 3) + '</td>';
        html += '<td><small>' + (c.schedule_info || 'TBA') + '</small></td></tr>';
    });
    
    html += '</tbody></table></div>';
    
    if (reg.registration_status === 'Draft') {
        html += '<div class="text-right">';
        html += '<button class="btn btn-primary" onclick="submit_registration(\'' + reg.name + '\')"><i class="fa fa-paper-plane"></i> Submit for Approval</button>';
        html += '</div>';
    }
    
    if (reg.registration_status === 'Approved') {
        html += '<div class="text-center"><a href="/app/my-timetable" class="btn btn-success"><i class="fa fa-calendar"></i> View My Timetable</a></div>';
    }
    
    html += '</div>';
    page.main.html(html);
}

function render_new(page, d) {
    var html = '<div class="container py-4" style="max-width:1000px">';
    html += '<h3>New Semester Registration</h3>';
    html += '<p class="text-muted">' + d.academic_term + ' | Registration: ' + d.period_start + ' to ' + d.period_end + '</p>';
    
    html += '<div class="card mb-4"><div class="card-body">';
    html += '<strong>Student:</strong> ' + d.student_name + ' | <strong>Program:</strong> ' + d.program;
    html += '</div></div>';
    
    html += '<div class="card mb-4"><div class="card-header">Select Your Courses <span class="float-right">Credits: <span id="total-credits">0</span> / ' + (d.max_credits || 21) + '</span></div>';
    html += '<div class="card-body" id="course-list"><div class="text-center py-3"><i class="fa fa-spinner fa-spin"></i> Loading courses...</div></div></div>';
    
    html += '<div class="card mb-4" id="timetable-card" style="display:none"><div class="card-header">Timetable Preview</div><div class="card-body" id="timetable-preview"></div></div>';
    
    html += '<div class="text-right"><button class="btn btn-primary btn-lg" id="btn-register" disabled><i class="fa fa-check"></i> Complete Registration</button></div>';
    
    html += '</div>';
    page.main.html(html);
    
    load_courses(page, d);
}

function load_courses(page, d) {
    frappe.call({
        method: 'education.api.registration.get_available_courses',
        args: {student: d.student, program: d.program, academic_term: d.academic_term},
        callback: function(r) {
            if (r.message) {
                page.available_courses = r.message;
                render_courses(page, r.message);
            }
        }
    });
}

function render_courses(page, courses) {
    var html = '';
    page.selected_courses = [];
    
    courses.forEach(function(c) {
        var mandatory = c.is_mandatory ? ' mandatory' : '';
        var checked = c.is_mandatory ? ' checked' : '';
        var disabled = c.is_mandatory ? ' disabled' : '';
        
        if (c.is_mandatory) page.selected_courses.push(c.course);
        
        html += '<div class="course-row' + mandatory + '" data-course="' + c.course + '" data-credits="' + c.credit_hours + '">';
        html += '<div class="row align-items-center py-2 border-bottom">';
        html += '<div class="col-1"><input type="checkbox" class="course-cb"' + checked + disabled + '></div>';
        html += '<div class="col-2"><strong>' + (c.course_code || '') + '</strong></div>';
        html += '<div class="col-4">' + c.course_name + (c.is_mandatory ? ' <span class="badge badge-danger">Required</span>' : '') + '</div>';
        html += '<div class="col-1">' + c.credit_hours + ' cr</div>';
        html += '<div class="col-4"><small class="text-muted">' + (c.schedule || 'TBA') + '</small></div>';
        html += '</div></div>';
    });
    
    $('#course-list').html(html + '<style>.course-row{cursor:pointer;transition:background 0.2s}.course-row:hover{background:#f8f9fa}.course-row.selected{background:#e8f5e9}.course-row.mandatory{border-left:3px solid #dc3545}</style>');
    
    update_totals(page);
    
    $('.course-row').on('click', function(e) {
        if ($(e.target).is('input')) return;
        var $row = $(this);
        var $cb = $row.find('.course-cb');
        if ($cb.prop('disabled')) return;
        
        $cb.prop('checked', !$cb.prop('checked'));
        $row.toggleClass('selected', $cb.prop('checked'));
        
        var course = $row.data('course');
        if ($cb.prop('checked')) {
            if (!page.selected_courses.includes(course)) page.selected_courses.push(course);
        } else {
            page.selected_courses = page.selected_courses.filter(c => c !== course);
        }
        
        update_totals(page);
        update_preview(page);
    });
    
    $('#btn-register').on('click', function() {
        complete_registration(page);
    });
}

function update_totals(page) {
    var total = 0;
    page.available_courses.forEach(function(c) {
        if (page.selected_courses.includes(c.course)) total += c.credit_hours || 3;
    });
    $('#total-credits').text(total);
    $('#btn-register').prop('disabled', page.selected_courses.length === 0);
}

function update_preview(page) {
    if (page.selected_courses.length === 0) {
        $('#timetable-card').hide();
        return;
    }
    
    $('#timetable-card').show();
    var selected = page.available_courses.filter(c => page.selected_courses.includes(c.course));
    
    var html = '<table class="table table-sm"><thead><tr><th>Course</th><th>Schedule</th></tr></thead><tbody>';
    selected.forEach(function(c) {
        html += '<tr><td>' + c.course_code + ' - ' + c.course_name + '</td><td>' + (c.schedule || 'TBA') + '</td></tr>';
    });
    html += '</tbody></table>';
    
    $('#timetable-preview').html(html);
}

function complete_registration(page) {
    if (page.selected_courses.length === 0) {
        frappe.msgprint('Please select at least one course');
        return;
    }
    
    frappe.call({
        method: 'education.api.registration.create_registration',
        args: {academic_term: page.data.academic_term, courses: page.selected_courses},
        freeze: true,
        freeze_message: 'Creating registration...',
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint({title: 'Success', message: 'Registration created!', indicator: 'green'});
                load_registration(page);
            } else {
                frappe.msgprint({title: 'Error', message: r.message.message || 'Failed', indicator: 'red'});
            }
        }
    });
}

function submit_registration(name) {
    frappe.confirm('Submit this registration for approval?', function() {
        frappe.call({
            method: 'education.api.registration.submit_for_approval',
            args: {registration_name: name},
            freeze: true,
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.msgprint({title: 'Submitted', message: r.message.message, indicator: 'green'});
                    location.reload();
                }
            }
        });
    });
}
