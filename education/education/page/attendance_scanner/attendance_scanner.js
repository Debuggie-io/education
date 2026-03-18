frappe.pages['attendance-scanner'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Attendance Scanner',
        single_column: true
    });
    
    page.scanned_count = 0;
    setup_page(page);
}

function get_current_meal() {
    var hour = new Date().getHours();
    if (hour >= 4 && hour < 11) {
        return { meal: 'Breakfast', icon: '🌅', color: '#ff9800' };
    } else if (hour >= 11 && hour < 16) {
        return { meal: 'Lunch', icon: '☀️', color: '#4caf50' };
    } else if (hour >= 16 && hour < 22) {
        return { meal: 'Supper', icon: '🌙', color: '#3f51b5' };
    } else {
        return { meal: null, icon: '🚫', color: '#9e9e9e' };
    }
}

function get_meal_time_range() {
    var meal = get_current_meal();
    if (meal.meal === 'Breakfast') return '4:00 AM - 10:59 AM';
    if (meal.meal === 'Lunch') return '11:00 AM - 3:59 PM';
    if (meal.meal === 'Supper') return '4:00 PM - 9:59 PM';
    return 'No meal service at this time';
}

function setup_page(page) {
    var currentMeal = get_current_meal();
    
    var html = `
        <div class="scanner-container">
            <!-- Settings Section -->
            <div class="settings-card">
                <div class="settings-header">
                    <i class="fa fa-cog"></i> Scanner Settings
                </div>
                <div class="settings-body">
                    <div class="settings-row">
                        <div class="setting-item">
                            <label>Attendance Type *</label>
                            <select id="attendance-type" class="form-control">
                                <option value="Class">Class Attendance</option>
                                <option value="School Activity">School Activity</option>
                                <option value="Meals">Meals</option>
                                <option value="Room Check">Room Check</option>
                            </select>
                        </div>
                        
                        <!-- Class Fields -->
                        <div class="setting-item" id="class-fields">
                            <label>Student Group *</label>
                            <div id="student-group-wrapper"></div>
                        </div>
                        
                        <!-- Activity Fields -->
                        <div class="setting-item" id="activity-fields" style="display:none">
                            <label>School Activity *</label>
                            <div id="school-activity-wrapper"></div>
                        </div>
                        
                        <!-- Meal Fields -->
                        <div class="setting-item" id="meal-fields" style="display:none">
                            <label>Current Meal</label>
                            <div class="meal-display">
                                <span class="meal-icon">${currentMeal.icon}</span>
                                <span class="meal-name" id="current-meal-name">${currentMeal.meal || 'No meal time'}</span>
                            </div>
                        </div>
                        
                        <!-- Room Check Fields -->
                        <div class="setting-item" id="room-check-fields" style="display:none">
                            <label>Room Check Schedule *</label>
                            <div id="room-check-wrapper"></div>
                        </div>
                        
                        <div class="setting-item">
                            <label>Date</label>
                            <input type="date" id="attendance-date" class="form-control" value="${frappe.datetime.get_today()}">
                        </div>
                        <div class="setting-item">
                            <label>Status</label>
                            <select id="attendance-status" class="form-control">
                                <option value="Present">Present</option>
                                <option value="Late">Late</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Context Banner (Meal/Room Check) -->
            <div class="context-banner" id="context-banner" style="display:none">
                <div class="banner-content">
                    <span class="banner-icon" id="banner-icon">${currentMeal.icon}</span>
                    <div class="banner-text">
                        <span class="banner-title" id="banner-title"></span>
                        <span class="banner-subtitle" id="banner-subtitle"></span>
                    </div>
                </div>
            </div>
            
            <!-- NFC Scanner Section -->
            <div class="scanner-card" id="scanner-card">
                <div class="scanner-header">
                    <div class="scanner-title">
                        <i class="fa fa-wifi"></i> NFC Scanner
                    </div>
                    <div class="scan-counter">
                        <span class="count-number" id="scan-count-num">0</span>
                        <span class="count-label">scanned today</span>
                    </div>
                </div>
                
                <div class="nfc-area" id="nfc-area">
                    <div class="nfc-icon-wrapper">
                        <div class="nfc-icon" id="nfc-icon">
                            <i class="fa fa-wifi"></i>
                        </div>
                    </div>
                    <div class="nfc-message">
                        <div class="nfc-title" id="nfc-title">Checking NFC...</div>
                        <div class="nfc-subtitle" id="nfc-subtitle">Please wait</div>
                    </div>
                </div>
                
                <div class="scan-result" id="scan-result" style="display:none">
                    <div class="result-icon" id="result-icon">
                        <i class="fa fa-check"></i>
                    </div>
                    <div class="result-info">
                        <div class="result-name" id="result-name"></div>
                        <div class="result-detail" id="result-detail"></div>
                    </div>
                </div>
            </div>
            
            <!-- Today's Attendance -->
            <div id="today-attendance-section">
                <div class="section-title">
                    <i class="fa fa-users"></i> Today's Attendance
                    <span class="section-count" id="today-count">0</span>
                </div>
                <div class="students-grid" id="students-grid">
                    <div class="empty-state">
                        <i class="fa fa-id-card"></i>
                        <p>No attendance recorded yet. Start scanning!</p>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            .scanner-container { padding: 20px; max-width: 100%; }
            
            .settings-card {
                background: var(--card-bg, #fff);
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                overflow: visible;
            }
            .settings-header {
                background: #0b4a6f;
                color: white;
                padding: 12px 20px;
                font-weight: 600;
                border-radius: 10px 10px 0 0;
            }
            .settings-body { padding: 20px; overflow: visible; }
            .settings-row { display: flex; gap: 20px; flex-wrap: wrap; overflow: visible; }
            .setting-item { flex: 1; min-width: 180px; position: relative; overflow: visible; }
            .setting-item label {
                font-weight: 600; margin-bottom: 5px; display: block;
                font-size: 12px; color: var(--text-muted, #555);
            }
            .setting-item .frappe-control, .setting-item .form-group { margin-bottom: 0 !important; overflow: visible !important; }
            .setting-item .awesomplete { overflow: visible !important; }
            .setting-item .awesomplete > ul {
                z-index: 9999 !important; max-height: 250px !important; overflow-y: auto !important;
                background: var(--card-bg, #fff) !important; border: 1px solid var(--border-color, #ddd) !important;
                border-radius: 6px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }
            .setting-item .form-control {
                background: var(--control-bg, #fff) !important;
                color: var(--text-color, #333) !important;
                border-color: var(--border-color, #ddd) !important;
            }
            
            .meal-display {
                display: flex; align-items: center; gap: 10px; padding: 8px 12px;
                background: var(--control-bg, #f8f9fa); border: 1px solid var(--border-color, #ddd);
                border-radius: 6px; font-weight: 600;
            }
            .meal-icon { font-size: 20px; }
            .meal-name { color: var(--text-color, #333); }
            
            .context-banner {
                border-radius: 10px; padding: 15px 20px; margin-bottom: 20px; color: white;
            }
            .context-banner.breakfast { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
            .context-banner.lunch { background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); }
            .context-banner.supper { background: linear-gradient(135deg, #3f51b5 0%, #303f9f 100%); }
            .context-banner.room-check { background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); }
            .context-banner.no-meal { background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%); }
            .banner-content { display: flex; align-items: center; gap: 15px; }
            .banner-icon { font-size: 36px; }
            .banner-title { font-size: 20px; font-weight: 700; display: block; }
            .banner-subtitle { font-size: 14px; opacity: 0.9; }
            
            .scanner-card {
                border-radius: 10px; padding: 25px; margin-bottom: 20px; color: white;
                transition: background 0.3s ease;
            }
            .scanner-card.listening { background: linear-gradient(135deg, #0b4a6f 0%, #1565c0 100%); }
            .scanner-card.not-supported { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); }
            .scanner-card.success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
            .scanner-card.error { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); }
            
            .scanner-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            .scanner-title { font-size: 18px; font-weight: 600; }
            .scan-counter { text-align: right; }
            .count-number { font-size: 32px; font-weight: bold; display: block; line-height: 1; }
            .count-label { font-size: 12px; opacity: 0.9; }
            
            .nfc-area { display: flex; flex-direction: column; align-items: center; padding: 40px 20px; text-align: center; }
            .nfc-icon-wrapper { margin-bottom: 20px; }
            .nfc-icon {
                width: 100px; height: 100px; background: rgba(255,255,255,0.2); border-radius: 50%;
                display: flex; align-items: center; justify-content: center; font-size: 48px;
            }
            .scanner-card.listening .nfc-icon { animation: pulse 2s infinite; }
            @keyframes pulse {
                0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255,255,255,0.4); }
                50% { transform: scale(1.05); box-shadow: 0 0 0 20px rgba(255,255,255,0); }
            }
            .nfc-title { font-size: 24px; font-weight: 700; margin-bottom: 8px; }
            .nfc-subtitle { font-size: 16px; opacity: 0.9; }
            
            .scan-result {
                margin-top: 20px; padding: 20px; background: rgba(255,255,255,0.2);
                border-radius: 10px; display: flex; align-items: center; gap: 20px;
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .result-icon {
                width: 60px; height: 60px; background: rgba(255,255,255,0.3); border-radius: 50%;
                display: flex; align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0;
            }
            .result-name { font-size: 22px; font-weight: 700; }
            .result-detail { font-size: 14px; opacity: 0.9; }
            
            .section-title {
                font-size: 16px; font-weight: 600; color: var(--text-color, #333);
                margin-bottom: 15px; display: flex; align-items: center; gap: 10px;
            }
            .section-count { background: #0b4a6f; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
            
            .student-card {
                background: var(--card-bg, #fff); border-radius: 10px; padding: 15px 20px;
                display: flex; align-items: center; gap: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 10px; border-left: 4px solid #28a745;
            }
            .student-card.late { border-left-color: #ffc107; }
            .student-photo {
                width: 50px; height: 50px; border-radius: 50%; background: var(--bg-color, #e9ecef);
                display: flex; align-items: center; justify-content: center; font-weight: bold;
                color: var(--text-muted, #6c757d); flex-shrink: 0;
            }
            .student-info { flex: 1; }
            .student-name { font-weight: 600; color: var(--text-color, #333); }
            .student-id { font-size: 12px; color: var(--text-muted, #666); font-family: monospace; }
            .student-room { font-size: 11px; color: var(--text-muted, #999); }
            .student-time { font-size: 12px; color: var(--text-muted, #999); }
            .status-badge { padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: 600; }
            .status-badge.present { background: #d4edda; color: #155724; }
            .status-badge.late { background: #fff3cd; color: #856404; }
            
            .empty-state { text-align: center; padding: 50px; color: var(--text-muted, #999); }
            .empty-state i { font-size: 48px; margin-bottom: 15px; }
            
            @media (max-width: 768px) {
                .settings-row { flex-direction: column; }
                .nfc-icon { width: 80px; height: 80px; font-size: 36px; }
                .nfc-title { font-size: 20px; }
            }
        </style>
    `;
    
    page.main.html(html);
    setup_link_fields(page);
    setup_handlers(page);
    setup_nfc(page);
    load_today_attendance(page);
    setInterval(update_context_display, 60000);
}

function setup_link_fields(page) {
    page.student_group_field = frappe.ui.form.make_control({
        parent: $('#student-group-wrapper'),
        df: { fieldtype: 'Link', options: 'Student Group', fieldname: 'student_group', placeholder: 'Select Student Group' },
        render_input: true
    });
    page.student_group_field.refresh();
    
    page.school_activity_field = frappe.ui.form.make_control({
        parent: $('#school-activity-wrapper'),
        df: {
            fieldtype: 'Link', options: 'School Activity', fieldname: 'school_activity', placeholder: 'Select Activity',
            get_query: function() { return { filters: { 'activity_date': $('#attendance-date').val(), 'status': ['in', ['Upcoming', 'Ongoing']] } }; }
        },
        render_input: true
    });
    page.school_activity_field.refresh();
    
    page.room_check_field = frappe.ui.form.make_control({
        parent: $('#room-check-wrapper'),
        df: {
            fieldtype: 'Link', options: 'Room Check Schedule', fieldname: 'room_check_schedule', placeholder: 'Select Room Check',
            get_query: function() { return { filters: { 'check_date': $('#attendance-date').val(), 'status': ['in', ['Scheduled', 'In Progress']] } }; }
        },
        render_input: true
    });
    page.room_check_field.refresh();
}

function setup_handlers(page) {
    $('#attendance-type').on('change', function() {
        var type = $(this).val();
        
        $('#class-fields, #activity-fields, #meal-fields, #room-check-fields').hide();
        $('#context-banner').hide().removeClass('breakfast lunch supper room-check no-meal');
        
        if (type === 'Class') {
            $('#class-fields').show();
        } else if (type === 'School Activity') {
            $('#activity-fields').show();
        } else if (type === 'Meals') {
            $('#meal-fields').show();
            update_meal_banner();
        } else if (type === 'Room Check') {
            $('#room-check-fields').show();
            update_room_check_banner();
        }
        
        load_today_attendance(page);
    });
    
    $('#attendance-date, #attendance-status').on('change', function() {
        load_today_attendance(page);
    });
}

function update_meal_banner() {
    var meal = get_current_meal();
    var banner = $('#context-banner');
    banner.removeClass('breakfast lunch supper room-check no-meal');
    
    $('#banner-icon').text(meal.icon);
    $('#banner-title').text(meal.meal || 'Outside Meal Hours');
    $('#banner-subtitle').text(get_meal_time_range());
    $('#current-meal-name').text(meal.meal || 'No meal time');
    
    if (meal.meal === 'Breakfast') banner.addClass('breakfast');
    else if (meal.meal === 'Lunch') banner.addClass('lunch');
    else if (meal.meal === 'Supper') banner.addClass('supper');
    else banner.addClass('no-meal');
    
    banner.show();
}

function update_room_check_banner() {
    var banner = $('#context-banner');
    banner.removeClass('breakfast lunch supper no-meal').addClass('room-check');
    $('#banner-icon').text('🏠');
    $('#banner-title').text('Room Check');
    $('#banner-subtitle').text('Scanning students in their rooms');
    banner.show();
}

function update_context_display() {
    var type = $('#attendance-type').val();
    if (type === 'Meals') update_meal_banner();
}

function setup_nfc(page) {
    var card = $('#scanner-card');
    
    if ('NDEFReader' in window) {
        card.addClass('listening');
        $('#nfc-title').text('Ready to Scan');
        $('#nfc-subtitle').text('Hold student ID card near the device');
        
        const ndef = new NDEFReader();
        ndef.scan().then(() => {
            $('#nfc-title').text('Listening for NFC');
            $('#nfc-subtitle').text('Hold student ID card near the device');
            
            ndef.onreading = event => {
                const decoder = new TextDecoder();
                for (const record of event.message.records) {
                    if (record.recordType === "text") {
                        process_scan(page, decoder.decode(record.data));
                    }
                }
            };
            ndef.onreadingerror = () => show_temp_error(page, 'Read Error', 'Could not read the card. Try again.');
        }).catch(error => show_nfc_not_supported(card, 'NFC permission denied or unavailable'));
    } else {
        show_nfc_not_supported(card, 'This device does not support NFC');
    }
}

function show_nfc_not_supported(card, message) {
    card.removeClass('listening success').addClass('not-supported');
    $('#nfc-icon').html('<i class="fa fa-times"></i>');
    $('#nfc-title').text('NFC Not Supported');
    $('#nfc-subtitle').text(message);
}

function process_scan(page, scanned_value) {
    var attendance_type = $('#attendance-type').val();
    var date = $('#attendance-date').val();
    var status = $('#attendance-status').val();
    var student_group = page.student_group_field ? page.student_group_field.get_value() : null;
    var school_activity = page.school_activity_field ? page.school_activity_field.get_value() : null;
    var room_check_schedule = page.room_check_field ? page.room_check_field.get_value() : null;
    var meal_type = null;
    
    if (attendance_type === 'Class' && !student_group) {
        show_temp_error(page, 'Select Student Group', 'Please select a student group first');
        return;
    }
    if (attendance_type === 'School Activity' && !school_activity) {
        show_temp_error(page, 'Select Activity', 'Please select a school activity first');
        return;
    }
    if (attendance_type === 'Meals') {
        var currentMeal = get_current_meal();
        if (!currentMeal.meal) {
            show_temp_error(page, 'Outside Meal Hours', 'Meal scanning is not available at this time');
            return;
        }
        meal_type = currentMeal.meal;
    }
    if (attendance_type === 'Room Check' && !room_check_schedule) {
        show_temp_error(page, 'Select Room Check', 'Please select a room check schedule first');
        return;
    }
    
    frappe.call({
        method: 'education.api.attendance.scan_and_save_attendance',
        args: {
            scan_value: scanned_value,
            attendance_type: attendance_type,
            date: date,
            status: status,
            student_group: student_group,
            school_activity: school_activity,
            meal_type: meal_type,
            room_check_schedule: room_check_schedule
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                var extraInfo = '';
                if (attendance_type === 'Meals') extraInfo = ' | ' + meal_type;
                if (attendance_type === 'Room Check' && r.message.hostel_room) extraInfo = ' | Room: ' + r.message.hostel_room;
                
                show_success(page, r.message.student, status, r.message.check_in_time, r.message.already_exists, extraInfo);
                page.scanned_count++;
                $('#scan-count-num').text(page.scanned_count);
                load_today_attendance(page);
                playSound(true);
            } else {
                show_temp_error(page, 'Not Found', r.message ? r.message.message : 'Student not found');
                playSound(false);
            }
        },
        error: function() {
            show_temp_error(page, 'Error', 'Failed to process scan');
            playSound(false);
        }
    });
}

function show_success(page, student, status, time, already_exists, extraInfo) {
    var card = $('#scanner-card');
    card.removeClass('listening not-supported error').addClass('success');
    $('#nfc-area').hide();
    $('#result-icon').html('<i class="fa fa-check"></i>');
    $('#result-name').text(student.student_name);
    $('#result-detail').html(student.name + ' | ' + (student.program || 'No program') + (extraInfo || '') + ' | ' + time +
        (already_exists ? ' <span style="opacity:0.7">(Already recorded)</span>' : ''));
    $('#scan-result').show();
    
    setTimeout(function() {
        card.removeClass('success').addClass('listening');
        $('#scan-result').hide();
        $('#nfc-area').show();
    }, 3000);
}

function show_temp_error(page, title, message) {
    var card = $('#scanner-card');
    var wasListening = card.hasClass('listening');
    card.removeClass('listening success').addClass('error');
    $('#nfc-area').hide();
    $('#result-icon').html('<i class="fa fa-times"></i>');
    $('#result-name').text(title);
    $('#result-detail').text(message);
    $('#scan-result').show();
    
    setTimeout(function() {
        card.removeClass('error');
        if (wasListening) card.addClass('listening');
        $('#scan-result').hide();
        $('#nfc-area').show();
    }, 3000);
}

function load_today_attendance(page) {
    var attendance_type = $('#attendance-type').val();
    var date = $('#attendance-date').val();
    var student_group = page.student_group_field ? page.student_group_field.get_value() : null;
    var school_activity = page.school_activity_field ? page.school_activity_field.get_value() : null;
    var room_check_schedule = page.room_check_field ? page.room_check_field.get_value() : null;
    var meal_type = (attendance_type === 'Meals') ? get_current_meal().meal : null;
    
    frappe.call({
        method: 'education.api.attendance.get_attendance_list',
        args: {
            date: date,
            attendance_type: attendance_type,
            student_group: student_group,
            school_activity: school_activity,
            meal_type: meal_type,
            room_check_schedule: room_check_schedule
        },
        callback: function(r) {
            var grid = $('#students-grid');
            grid.empty();
            
            if (r.message && r.message.length > 0) {
                page.scanned_count = r.message.length;
                $('#scan-count-num').text(page.scanned_count);
                $('#today-count').text(r.message.length);
                
                r.message.forEach(function(att) {
                    var initials = att.student_name ? att.student_name.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase() : '?';
                    var statusClass = att.status === 'Present' ? 'present' : 'late';
                    var cardClass = att.status === 'Present' ? '' : 'late';
                    var roomInfo = att.hostel_room ? '<div class="student-room">Room: ' + att.hostel_room + '</div>' : '';
                    
                    grid.append(
                        '<div class="student-card ' + cardClass + '">' +
                            '<div class="student-photo">' + initials + '</div>' +
                            '<div class="student-info">' +
                                '<div class="student-name">' + (att.student_name || att.student) + '</div>' +
                                '<div class="student-id">' + att.student + '</div>' +
                                roomInfo +
                            '</div>' +
                            '<div class="student-time">' + (att.check_in_time || '') + '</div>' +
                            '<span class="status-badge ' + statusClass + '">' + att.status + '</span>' +
                        '</div>'
                    );
                });
            } else {
                page.scanned_count = 0;
                $('#scan-count-num').text('0');
                $('#today-count').text('0');
                grid.html('<div class="empty-state"><i class="fa fa-id-card"></i><p>No attendance recorded yet. Start scanning!</p></div>');
            }
        }
    });
}

function playSound(success) {
    try {
        var audio = new Audio(success ? 
            'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJuvsLCvq6WYhXJlZGp0hZSeoaGgnpqUi4B1bWxyfYqXoKOjoJ6ak46Ef3p5fYaMlJyjpKSjoJ2Xj4iDgIGFi5KZn6KioaCdmZONh4OBg4iNk5qfoaGgnpuWkIqFgoKFio+Wm5+hoaCempWPioWCg4aLkJabnqCfnpyYk46JhYOEh4yRlpudnp6dnJiUj4qGhIWHi5CUmZudnZ2cmZWRjYmGhYaJjZGVmJubm5qZlpKOioeFhouOkpWYmpqamZeUkY2JhoaIi46SlZiZmpmYlpOPjImHh4mLjpGUl5mZmJeVko+MiYeHiYuOkZSXmJiYlpSRjouJh4iKjI+SlZeYmJeWlJGOi4mIiIqMj5KVl5eXlpWTkI2KiIiJi42QkpWXl5eWlJKPjYqJiImLjZCSlZaXlpWUko+NiomIiYuNkJKVlpaWlZOSj42KiYiJi42PkpSWlpaVlJKPjYuJiYmLjY+Sk5WWlZWUkpCOi4qJiYqMjpCSk5WVlZSSkI6Mi4qJiouNjpGTlJSUk5KQjo2LioqKi42OkZOUlJSTkpCOjIuKioqLjY6RkpOTk5KRj42Mi4qKiouNjpCSkpOTkpGPjoyLi4qKi4yOkJGSk5KSkY+OjIuLiouLjI6PkZKSkpGQj46MjIuLi4uMjo+RkpKSkZCPjo2MjIuLi4yNj5CRkpKRkI+OjYyLi4uLjI2Oj5CRkZGQj46NjIyLi4uMjY6PkJGRkJCPjo2MjIuLi4yNjo+QkZGQj46OjYyMi4uLjI2Ojo+Qj4+Ojo2NjYyMjIyMjY2Ojo+Pj46OjY2NjYyMjIyMjI2Njo6Ojo6OjY2NjYyMjIyMjIyNjY2Ojo6OjY2NjY2MjIyMjIyMjY2Njo6OjY2NjY2NjIyMjIyMjIyNjY2NjY2NjY2NjYyM' :
            'data:audio/wav;base64,UklGRl9vT19teleRmAAAAFdBVkVmbXQgEAABAAEARKwAAIhYAQACABAAZGF0YUJPVIGFioqIhoN/e3Z0cnFycnN0d3qAhYqNjY2MiYaBfnp3dHJxcHBxc3Z6foKGiYuLioiFgn56d3RycXBwcXN2eX2Bg4aIiYmIhoN/fHl2dHJxcHFyc3Z5fH+ChYeIiIeGg4B9endzc3JxcXJzdHd6fX+DhYeHh4aEgX57eHZzc3FxcnN0dXd6fH6Ag4SFhYSDgX98endzc3JycnN0dXZ4e32AgYOEhISDgX99e3h2dXRzcnJzdHV2eHt9f4GCg4ODgoF/fXp4dnV0c3N0dHV2eHp8fn+BgoODgoGAfnx6eHd1dHR0dHV2d3l7fX5/gYKCgoGAfn17eXh2dXV1dXZ2d3h6fH1/gIGBgYGAfn18e3p5eHd3d3d3eHl6e31+f3+AgIB/fn18e3p5eXh4eHh4eHl6e3x9fn9/f39/fn18fHt6eXl5eHh4eXl6e3x9fn5/f39/fn59fHt7enp5eXl5eXl6ent8fX5+fn5+fn59fXx7e3p6eXl5eXl5ent7fHx9fX5+fn5+fX19fHx7e3t6e3t7e3t7fHx8fX19fX19fX19fXx8fHt8fHx8fHx8fHx8fX19fX19fX19fX18fHx8fHx8fHx8fHx8fX19fX19fX19fXx8fHx8fHx8fHx8fHx8fX19fX19fX18'
        );
        audio.volume = 0.5;
        audio.play();
    } catch(e) {}
}
