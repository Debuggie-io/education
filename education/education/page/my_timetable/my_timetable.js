frappe.pages['my-timetable'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'My Timetable',
        single_column: true
    });
    
    wrapper.page = page;
    page.is_loading = false;
    page.current_view = 'week';
    
    setup_filters(page);
    setup_view_toggle(page);
    
    // Initial load
    setTimeout(function() {
        load_timetable(page);
    }, 100);
}

function setup_filters(page) {
    page.add_field({
        fieldname: 'academic_year',
        label: __('Academic Year'),
        fieldtype: 'Link',
        options: 'Academic Year',
        change: function() {
            if (!page.is_loading) {
                page.fields_dict.academic_term.set_value('');
            }
        }
    });
    
    page.add_field({
        fieldname: 'academic_term',
        label: __('Academic Term'),
        fieldtype: 'Link',
        options: 'Academic Term',
        get_query: function() {
            var year = page.fields_dict.academic_year.get_value();
            return year ? { filters: { 'academic_year': year } } : {};
        },
        change: function() {
            if (!page.is_loading) {
                load_timetable(page);
            }
        }
    });
    
    page.set_secondary_action(__('Refresh'), function() {
        load_timetable(page);
    });
}

function setup_view_toggle(page) {
    page.add_inner_button(__('Week View'), function() {
        page.current_view = 'week';
        render_timetable(page, page.timetable_data);
    }, __('View'));
    
    page.add_inner_button(__('List View'), function() {
        page.current_view = 'list';
        render_timetable(page, page.timetable_data);
    }, __('View'));
    
    page.add_inner_button(__('Day View'), function() {
        page.current_view = 'day';
        render_timetable(page, page.timetable_data);
    }, __('View'));
    
    page.add_inner_button(__('Print'), function() {
        print_timetable(page);
    });
}

function load_timetable(page) {
    if (page.is_loading) return;
    page.is_loading = true;
    
    var term = page.fields_dict.academic_term ? page.fields_dict.academic_term.get_value() : '';
    
    page.main.html(`
        <div class="text-center" style="padding: 60px;">
            <i class="fa fa-spinner fa-spin fa-3x text-muted"></i>
            <p class="text-muted mt-3">Loading your timetable...</p>
        </div>
    `);
    
    frappe.call({
        method: 'education.api.timetable.get_my_timetable',
        args: { academic_term: term || '' },
        callback: function(r) {
            page.is_loading = false;
            if (r.message) {
                page.timetable_data = r.message;
                
                // Set filters without triggering change
                if (!term && r.message.academic_term) {
                    page.is_loading = true;
                    frappe.db.get_value('Academic Term', r.message.academic_term, 'academic_year', function(data) {
                        if (data && data.academic_year && page.fields_dict.academic_year) {
                            page.fields_dict.academic_year.set_value(data.academic_year);
                        }
                        if (page.fields_dict.academic_term) {
                            page.fields_dict.academic_term.set_value(r.message.academic_term);
                        }
                        page.is_loading = false;
                    });
                }
                
                render_timetable(page, r.message);
            }
        },
        error: function() {
            page.is_loading = false;
            page.main.html(`
                <div class="text-center text-danger" style="padding: 60px;">
                    <i class="fa fa-exclamation-triangle fa-3x"></i>
                    <p class="mt-3">Error loading timetable</p>
                </div>
            `);
        }
    });
}

function render_timetable(page, data) {
    if (!data || !data.success) {
        page.main.html(`
            <div class="text-center" style="padding: 60px;">
                <i class="fa fa-calendar-o fa-3x text-muted"></i>
                <h4 class="text-muted mt-3">No Timetable Found</h4>
                <p class="text-muted">${data ? data.message : 'Your timetable will appear here once classes are scheduled.'}</p>
            </div>
        `);
        return;
    }
    
    if (page.current_view === 'list') {
        render_list_view(page, data);
    } else if (page.current_view === 'day') {
        render_day_view(page, data);
    } else {
        render_week_view(page, data);
    }
}

function render_week_view(page, data) {
    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    var entries = data.entries || [];
    var time_slots = data.time_slots || [];
    
    // Group entries
    var grid = {};
    entries.forEach(function(e) {
        var key = e.time_slot + '_' + e.day;
        if (!grid[key]) grid[key] = [];
        grid[key].push(e);
    });
    
    var html = `
        <div class="timetable-wrapper">
            <div class="timetable-info">
                <h4>${data.academic_term || 'Timetable'}</h4>
                <div class="stats">
                    <span class="badge badge-primary">${data.total_hours || 0} Hrs/Week</span>
                    <span class="badge badge-secondary">${data.courses_count || 0} Courses</span>
                    <span class="badge badge-info">${data.user_type || ''}: ${data.user_name || ''}</span>
                </div>
            </div>
            
            <table class="table table-bordered tt-table">
                <thead class="thead-light">
                    <tr>
                        <th style="width:90px">Time</th>
                        ${days.map(d => '<th>' + d + '</th>').join('')}
                    </tr>
                </thead>
                <tbody>
    `;
    
    time_slots.forEach(function(slot) {
        html += `<tr><td class="time-cell">${fmt_time(slot.start_time)}<br><small>to</small><br>${fmt_time(slot.end_time)}</td>`;
        
        days.forEach(function(day) {
            var key = slot.name + '_' + day;
            var cell = grid[key] || [];
            
            if (cell.length) {
                html += '<td class="has-class">';
                cell.forEach(function(e) {
                    html += `
                        <div class="class-block" style="background:${get_color(e.course)}">
                            <strong>${e.course_code || ''}</strong>
                            <div>${e.course_name || e.course}</div>
                            <small><i class="fa fa-map-marker"></i> ${e.room_number || e.room || ''}</small>
                            <small><i class="fa fa-user"></i> ${e.instructor_name || ''}</small>
                        </div>
                    `;
                });
                html += '</td>';
            } else {
                html += '<td></td>';
            }
        });
        html += '</tr>';
    });
    
    html += `
                </tbody>
            </table>
        </div>
        <style>
            .timetable-wrapper { padding: 15px; }
            .timetable-info { margin-bottom: 15px; }
            .timetable-info h4 { margin: 0; }
            .timetable-info .stats { margin-top: 8px; }
            .timetable-info .badge { margin-right: 5px; }
            .tt-table { font-size: 12px; }
            .tt-table th { text-align: center; }
            .time-cell { text-align: center; vertical-align: middle; font-size: 11px; background: #f9f9f9; }
            .has-class { padding: 3px !important; background: #f0f7ff; }
            .class-block {
                padding: 6px 8px;
                border-radius: 4px;
                color: #fff;
                margin: 2px;
                font-size: 11px;
            }
            .class-block strong { display: block; font-size: 12px; }
            .class-block small { display: block; margin-top: 2px; opacity: 0.9; }
        </style>
    `;
    
    page.main.html(html);
}

function render_list_view(page, data) {
    var entries = data.entries || [];
    var days_order = {Monday:1, Tuesday:2, Wednesday:3, Thursday:4, Friday:5, Saturday:6, Sunday:7};
    
    entries.sort(function(a,b) {
        return (days_order[a.day]||9) - (days_order[b.day]||9) || (a.start_time||'').localeCompare(b.start_time||'');
    });
    
    var html = `
        <div style="padding:15px">
            <h4>Timetable - List View</h4>
            <p class="text-muted">${data.academic_term || ''}</p>
            <table class="table table-striped">
                <thead><tr><th>Day</th><th>Time</th><th>Course</th><th>Room</th><th>Instructor</th></tr></thead>
                <tbody>
    `;
    
    if (entries.length === 0) {
        html += '<tr><td colspan="5" class="text-center text-muted">No entries</td></tr>';
    } else {
        entries.forEach(function(e) {
            html += `
                <tr>
                    <td><strong>${e.day}</strong></td>
                    <td>${fmt_time(e.start_time)} - ${fmt_time(e.end_time)}</td>
                    <td><strong>${e.course_code||''}</strong> ${e.course_name||e.course}</td>
                    <td>${e.room_number||e.room||'-'}</td>
                    <td>${e.instructor_name||'-'}</td>
                </tr>
            `;
        });
    }
    
    html += '</tbody></table></div>';
    page.main.html(html);
}

function render_day_view(page, data) {
    var entries = data.entries || [];
    var today = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date().getDay()];
    var todays = entries.filter(function(e){ return e.day === today; });
    
    todays.sort(function(a,b) { return (a.start_time||'').localeCompare(b.start_time||''); });
    
    var html = `
        <div style="padding:15px;max-width:600px">
            <h4>Today - ${today}</h4>
            <p class="text-muted">${data.academic_term || ''}</p>
    `;
    
    if (todays.length === 0) {
        html += '<div class="alert alert-info"><i class="fa fa-coffee"></i> No classes today!</div>';
    } else {
        todays.forEach(function(e) {
            html += `
                <div class="card mb-2">
                    <div class="card-body" style="padding:12px">
                        <h5 class="card-title mb-1">${e.course_code||''} - ${e.course_name||e.course}</h5>
                        <p class="mb-1"><i class="fa fa-clock-o"></i> ${fmt_time(e.start_time)} - ${fmt_time(e.end_time)}</p>
                        <p class="mb-0 text-muted"><i class="fa fa-map-marker"></i> ${e.room_number||e.room||'TBA'} | <i class="fa fa-user"></i> ${e.instructor_name||''}</p>
                    </div>
                </div>
            `;
        });
    }
    
    html += '</div>';
    page.main.html(html);
}

function fmt_time(t) {
    if (!t) return '';
    var parts = String(t).split(':');
    var h = parseInt(parts[0]) || 0;
    var m = parts[1] || '00';
    var ap = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return h + ':' + m + ' ' + ap;
}

function get_color(name) {
    var colors = ['#3498db','#2ecc71','#e74c3c','#9b59b6','#f39c12','#1abc9c','#e67e22','#34495e'];
    var hash = 0;
    for (var i = 0; i < (name||'').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
}

function print_timetable(page) {
    window.print();
}

frappe.pages['my-timetable'].on_page_show = function(wrapper) {
    // Don't auto-reload on page show to prevent loops
}
