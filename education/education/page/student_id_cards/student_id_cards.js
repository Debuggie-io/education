frappe.pages['student-id-cards'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Student ID Card Generator',
        single_column: true
    });
    
    setup_page(page);
}

function setup_page(page) {
    page.main.html(`
        <div class="id-card-container">
            <!-- Filters -->
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <strong><i class="fa fa-filter"></i> Select Students</strong>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <label class="font-weight-bold">Program</label>
                            <div id="program-wrapper"></div>
                        </div>
                        <div class="col-md-3">
                            <label class="font-weight-bold">Academic Year</label>
                            <div id="academic-year-wrapper"></div>
                        </div>
                        <div class="col-md-3">
                            <label class="font-weight-bold">Student Group</label>
                            <div id="student-group-wrapper"></div>
                        </div>
                        <div class="col-md-3">
                            <label class="font-weight-bold">Or Single Student</label>
                            <div id="student-wrapper"></div>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-md-12">
                            <button class="btn btn-primary" id="btn-generate">
                                <i class="fa fa-qrcode"></i> Generate ID Cards
                            </button>
                            <button class="btn btn-success ml-2" id="btn-print" style="display:none">
                                <i class="fa fa-print"></i> Print All
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ID Cards Preview -->
            <div id="cards-container" class="row"></div>
        </div>
        
        <style>
            .id-card-container { padding: 20px; }
            
            .id-card {
                width: 340px;
                height: 215px;
                border: 2px solid #0b4a6f;
                border-radius: 12px;
                background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
                padding: 15px;
                margin: 10px;
                position: relative;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                page-break-inside: avoid;
            }
            
            .id-card-header {
                background: #0b4a6f;
                color: white;
                margin: -15px -15px 10px -15px;
                padding: 8px 15px;
                border-radius: 10px 10px 0 0;
                text-align: center;
                font-size: 12px;
            }
            
            .id-card-header h4 {
                margin: 0;
                font-size: 14px;
                font-weight: bold;
            }
            
            .id-card-body {
                display: flex;
                gap: 15px;
            }
            
            .id-card-photo {
                width: 80px;
                height: 100px;
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                color: #999;
                overflow: hidden;
            }
            
            .id-card-photo img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .id-card-info {
                flex: 1;
                font-size: 11px;
            }
            
            .id-card-info .name {
                font-size: 14px;
                font-weight: bold;
                color: #0b4a6f;
                margin-bottom: 5px;
            }
            
            .id-card-info .detail {
                margin-bottom: 2px;
                color: #333;
            }
            
            .id-card-qr {
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 60px;
                height: 60px;
            }
            
            .id-card-footer {
                position: absolute;
                bottom: 5px;
                left: 15px;
                font-size: 9px;
                color: #666;
            }
            
            @media print {
                .card, .btn, .navbar, .sidebar { display: none !important; }
                .id-card-container { padding: 0; }
                .id-card { 
                    margin: 10px;
                    box-shadow: none;
                    border: 1px solid #000;
                }
            }
        </style>
    `);
    
    // Setup link fields
    setup_filters(page);
    
    // Generate button
    $('#btn-generate').on('click', function() {
        generate_cards(page);
    });
    
    // Print button
    $('#btn-print').on('click', function() {
        window.print();
    });
}

function setup_filters(page) {
    // Program filter
    page.program_field = frappe.ui.form.make_control({
        parent: $('#program-wrapper'),
        df: {
            fieldtype: 'Link',
            options: 'Program',
            fieldname: 'program',
            placeholder: 'Select Program'
        },
        render_input: true
    });
    page.program_field.refresh();
    
    // Academic Year filter
    page.academic_year_field = frappe.ui.form.make_control({
        parent: $('#academic-year-wrapper'),
        df: {
            fieldtype: 'Link',
            options: 'Academic Year',
            fieldname: 'academic_year',
            placeholder: 'Select Year'
        },
        render_input: true
    });
    page.academic_year_field.refresh();
    
    // Student Group filter
    page.student_group_field = frappe.ui.form.make_control({
        parent: $('#student-group-wrapper'),
        df: {
            fieldtype: 'Link',
            options: 'Student Group',
            fieldname: 'student_group',
            placeholder: 'Select Group'
        },
        render_input: true
    });
    page.student_group_field.refresh();
    
    // Single Student
    page.student_field = frappe.ui.form.make_control({
        parent: $('#student-wrapper'),
        df: {
            fieldtype: 'Link',
            options: 'Student',
            fieldname: 'student',
            placeholder: 'Select Student'
        },
        render_input: true
    });
    page.student_field.refresh();
}

function generate_cards(page) {
    var filters = {};
    
    var program = page.program_field.get_value();
    var academic_year = page.academic_year_field.get_value();
    var student_group = page.student_group_field.get_value();
    var student = page.student_field.get_value();
    
    frappe.call({
        method: 'education.api.attendance.get_students_for_id_cards',
        args: {
            program: program,
            academic_year: academic_year,
            student_group: student_group,
            student: student
        },
        freeze: true,
        freeze_message: 'Loading students...',
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                render_cards(r.message);
                $('#btn-print').show();
            } else {
                $('#cards-container').html('<div class="col-12 text-center text-muted py-5"><i class="fa fa-users fa-3x mb-3"></i><br>No students found</div>');
                $('#btn-print').hide();
            }
        }
    });
}

function render_cards(students) {
    var container = $('#cards-container');
    container.empty();
    
    students.forEach(function(s) {
        var initials = (s.first_name ? s.first_name[0] : '') + (s.last_name ? s.last_name[0] : '');
        var photoHtml = s.image 
            ? '<img src="' + s.image + '" alt="Photo">' 
            : initials.toUpperCase();
        
        var card = `
            <div class="col-auto">
                <div class="id-card">
                    <div class="id-card-header">
                        <h4>UNIVERSITY OF EASTERN AFRICA BARATON</h4>
                        <div>Student Identity Card</div>
                    </div>
                    <div class="id-card-body">
                        <div class="id-card-photo">${photoHtml}</div>
                        <div class="id-card-info">
                            <div class="name">${s.student_name}</div>
                            <div class="detail"><strong>ID:</strong> ${s.name}</div>
                            <div class="detail"><strong>Program:</strong> ${s.program || 'N/A'}</div>
                            <div class="detail"><strong>Email:</strong> ${s.email || 'N/A'}</div>
                        </div>
                    </div>
                    <div class="id-card-qr" id="qr-${s.name.replace(/[^a-zA-Z0-9]/g, '')}"></div>
                    <div class="id-card-footer">Valid for current academic year</div>
                </div>
            </div>
        `;
        container.append(card);
        
        // Generate QR code
        var qrId = 'qr-' + s.name.replace(/[^a-zA-Z0-9]/g, '');
        new QRCode(document.getElementById(qrId), {
            text: s.name,
            width: 60,
            height: 60,
            colorDark: "#0b4a6f",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.M
        });
    });
}
