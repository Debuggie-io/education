frappe.pages['auto-scheduler'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Auto Schedule Generator',
        single_column: true
    });
    
    wrapper.auto_scheduler = new AutoScheduler(wrapper, page);
}

class AutoScheduler {
    constructor(wrapper, page) {
        this.wrapper = wrapper;
        this.page = page;
        this.is_running = false;
        
        this.setup_page();
        this.render();
        this.setup_realtime();
    }
    
    setup_page() {
        this.page.set_primary_action(__('Generate Schedule'), () => {
            this.run_scheduler();
        }, 'octicon octicon-zap');
        
        this.page.add_inner_button(__('Preview Only'), () => {
            this.run_scheduler(true);
        });
        
        this.page.add_inner_button(__('Clear Results'), () => {
            this.clear_results();
        });
    }
    
    render() {
        this.$container = $('<div class="auto-scheduler-container">').appendTo(this.page.body);
        
        this.$container.html(`
            <style>
                .auto-scheduler-container {
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .scheduler-card {
                    background: var(--card-bg);
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: var(--card-shadow);
                    /* IMPORTANT: Allow dropdowns to overflow */
                    overflow: visible !important;
                }
                
                .scheduler-card h4 {
                    margin-top: 0;
                    margin-bottom: 15px;
                    color: var(--heading-color);
                    border-bottom: 1px solid var(--border-color);
                    padding-bottom: 10px;
                }
                
                .form-grid {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    /* IMPORTANT: Allow dropdowns to overflow */
                    overflow: visible !important;
                }
                
                .form-group {
                    flex: 1 1 220px;
                    min-width: 220px;
                    max-width: 300px;
                    position: relative;
                    /* IMPORTANT: Allow dropdowns to overflow */
                    overflow: visible !important;
                }
                
                .form-group .frappe-control {
                    margin-bottom: 0;
                    /* IMPORTANT: Allow dropdowns to overflow */
                    overflow: visible !important;
                }
                
                .form-group .control-input-wrapper {
                    overflow: visible !important;
                }
                
                .form-group .control-input {
                    overflow: visible !important;
                }
                
                /* Fix awesomplete dropdown positioning */
                .form-group .awesomplete {
                    position: relative !important;
                    overflow: visible !important;
                }
                
                .form-group .awesomplete > ul {
                    position: absolute !important;
                    z-index: 9999 !important;
                    background: var(--card-bg) !important;
                    border: 1px solid var(--border-color) !important;
                    border-radius: 6px !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                    max-height: 300px !important;
                    overflow-y: auto !important;
                    min-width: 100% !important;
                }
                
                .form-group .awesomplete > ul > li {
                    padding: 8px 12px !important;
                    cursor: pointer !important;
                }
                
                .form-group .awesomplete > ul > li:hover,
                .form-group .awesomplete > ul > li[aria-selected="true"] {
                    background: var(--control-bg) !important;
                }
                
                /* Fix link-field dropdown */
                .form-group .link-field .frappe-control,
                .form-group .link-field {
                    overflow: visible !important;
                }
                
                .hidden {
                    display: none !important;
                }
                
                .progress-container {
                    display: none;
                    margin-top: 20px;
                }
                
                .progress-container.active {
                    display: block;
                }
                
                .progress-bar-wrapper {
                    background: var(--control-bg);
                    border-radius: 10px;
                    height: 20px;
                    overflow: hidden;
                    margin-bottom: 10px;
                }
                
                .progress-bar {
                    height: 100%;
                    background: linear-gradient(90deg, var(--primary) 0%, #28a745 100%);
                    border-radius: 10px;
                    transition: width 0.3s ease;
                    width: 0%;
                }
                
                .progress-message {
                    text-align: center;
                    color: var(--text-muted);
                    font-size: 13px;
                }
                
                .results-container {
                    display: none;
                }
                
                .results-container.active {
                    display: block;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .stat-box {
                    background: var(--control-bg);
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }
                
                .stat-box .stat-value {
                    font-size: 32px;
                    font-weight: 700;
                    color: var(--primary);
                }
                
                .stat-box .stat-label {
                    font-size: 12px;
                    color: var(--text-muted);
                    text-transform: uppercase;
                    margin-top: 5px;
                }
                
                .stat-box.success .stat-value { color: #28a745; }
                .stat-box.warning .stat-value { color: #ff9800; }
                .stat-box.danger .stat-value { color: #dc3545; }
                
                .preview-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                }
                
                .preview-table th,
                .preview-table td {
                    padding: 10px;
                    border: 1px solid var(--border-color);
                    text-align: left;
                }
                
                .preview-table th {
                    background: var(--control-bg);
                    font-weight: 600;
                }
                
                .preview-table tr:hover {
                    background: var(--control-bg);
                }
                
                .unscheduled-list {
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    border-radius: 8px;
                    padding: 15px;
                    margin-top: 15px;
                }
                
                .unscheduled-list h5 {
                    margin: 0 0 10px 0;
                    color: #856404;
                }
                
                .unscheduled-item {
                    padding: 5px 0;
                    border-bottom: 1px solid #ffeeba;
                    color: #856404;
                }
                
                .unscheduled-item:last-child {
                    border-bottom: none;
                }
                
                .action-buttons {
                    display: flex;
                    gap: 10px;
                    margin-top: 20px;
                }
                
                .schedule-preview {
                    max-height: 400px;
                    overflow-y: auto;
                }
            </style>
            
            <!-- Configuration Card -->
            <div class="scheduler-card">
                <h4><i class="fa fa-cog"></i> Configuration</h4>
                <div class="form-grid" id="config-form"></div>
            </div>
            
            <!-- Progress Card -->
            <div class="scheduler-card progress-container" id="progress-container">
                <h4><i class="fa fa-spinner fa-spin"></i> Generating Schedule...</h4>
                <div class="progress-bar-wrapper">
                    <div class="progress-bar" id="progress-bar"></div>
                </div>
                <div class="progress-message" id="progress-message">Initializing...</div>
            </div>
            
            <!-- Results Card -->
            <div class="scheduler-card results-container" id="results-container">
                <h4><i class="fa fa-check-circle"></i> Results</h4>
                <div class="stats-grid" id="stats-grid"></div>
                <div class="schedule-preview" id="schedule-preview"></div>
                <div id="unscheduled-container"></div>
                <div class="action-buttons" id="action-buttons"></div>
            </div>
        `);
        
        this.render_form();
    }
    
    render_form() {
        const me = this;
        const $form = this.$container.find('#config-form');
        
        // Academic Term field
        let $academicTermGroup = $('<div class="form-group">').appendTo($form);
        this.academic_term_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Link',
                fieldname: 'academic_term',
                label: 'Academic Term',
                options: 'Academic Term',
                reqd: 1
            },
            parent: $academicTermGroup,
            render_input: true
        });
        this.academic_term_field.refresh();
        
        // Timetable For field
        let $timetableForGroup = $('<div class="form-group">').appendTo($form);
        this.timetable_for_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Select',
                fieldname: 'timetable_for',
                label: 'Timetable For',
                options: 'Entire University\nSchool\nDepartment\nProgram',
                default: 'Entire University',
                change: function() {
                    me.toggle_scope_fields();
                }
            },
            parent: $timetableForGroup,
            render_input: true
        });
        this.timetable_for_field.refresh();
        this.timetable_for_field.set_value('Entire University');
        
        // School field
        this.$schoolGroup = $('<div class="form-group hidden">').appendTo($form);
        this.school_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Link',
                fieldname: 'school',
                label: 'School',
                options: 'Department',
                get_query: function() {
                    return {
                        filters: { 'is_group': 1 }
                    };
                },
                change: function() {
                    if (me.department_field) {
                        me.department_field.set_value('');
                    }
                    if (me.program_field) {
                        me.program_field.set_value('');
                    }
                }
            },
            parent: this.$schoolGroup,
            render_input: true
        });
        this.school_field.refresh();
        
        // Department field
        this.$departmentGroup = $('<div class="form-group hidden">').appendTo($form);
        this.department_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Link',
                fieldname: 'department',
                label: 'Department',
                options: 'Department',
                get_query: function() {
                    let filters = { 'is_group': 0 };
                    let school = me.school_field.get_value();
                    if (school) {
                        filters['parent_department'] = school;
                    }
                    return { filters: filters };
                },
                change: function() {
                    if (me.program_field) {
                        me.program_field.set_value('');
                    }
                }
            },
            parent: this.$departmentGroup,
            render_input: true
        });
        this.department_field.refresh();
        
        // Program field
        this.$programGroup = $('<div class="form-group hidden">').appendTo($form);
        this.program_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Link',
                fieldname: 'program',
                label: 'Program',
                options: 'Program',
                get_query: function() {
                    let filters = {};
                    let department = me.department_field.get_value();
                    if (department) {
                        filters['department'] = department;
                    }
                    return { filters: filters };
                }
            },
            parent: this.$programGroup,
            render_input: true
        });
        this.program_field.refresh();
        
        // Set current academic term
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Academic Term',
                filters: {},
                fields: ['name'],
                order_by: 'term_start_date desc',
                limit: 1
            },
            callback: (r) => {
                if (r.message && r.message.length) {
                    this.academic_term_field.set_value(r.message[0].name);
                }
            }
        });
    }
    
    toggle_scope_fields() {
        const scope = this.timetable_for_field.get_value();
        
        // Hide all scope fields first
        this.$schoolGroup.addClass('hidden');
        this.$departmentGroup.addClass('hidden');
        this.$programGroup.addClass('hidden');
        
        // Clear values when hiding
        switch(scope) {
            case 'Entire University':
                this.school_field.set_value('');
                this.department_field.set_value('');
                this.program_field.set_value('');
                break;
            case 'School':
                this.$schoolGroup.removeClass('hidden');
                this.department_field.set_value('');
                this.program_field.set_value('');
                break;
            case 'Department':
                this.$schoolGroup.removeClass('hidden');
                this.$departmentGroup.removeClass('hidden');
                this.program_field.set_value('');
                break;
            case 'Program':
                this.$schoolGroup.removeClass('hidden');
                this.$departmentGroup.removeClass('hidden');
                this.$programGroup.removeClass('hidden');
                break;
        }
    }
    
    setup_realtime() {
        frappe.realtime.on('scheduler_progress', (data) => {
            this.update_progress(data.progress, data.message);
            if (data.result) {
                this.show_results(data.result);
            }
        });
    }
    
    run_scheduler(preview_only = false) {
        if (this.is_running) {
            frappe.msgprint(__('Scheduler is already running'));
            return;
        }
        
        const academic_term = this.academic_term_field.get_value();
        if (!academic_term) {
            frappe.msgprint(__('Please select an Academic Term'));
            return;
        }
        
        const scope = this.timetable_for_field.get_value() || 'Entire University';
        
        // Validate scope-specific fields
        if (scope === 'School' && !this.school_field.get_value()) {
            frappe.msgprint(__('Please select a School'));
            return;
        }
        if ((scope === 'Department' || scope === 'Program') && !this.department_field.get_value()) {
            frappe.msgprint(__('Please select a Department'));
            return;
        }
        if (scope === 'Program' && !this.program_field.get_value()) {
            frappe.msgprint(__('Please select a Program'));
            return;
        }
        
        this.is_running = true;
        this.show_progress();
        
        const method = preview_only ? 
            'education.education.scheduler.auto_scheduler.preview_schedule' :
            'education.education.scheduler.auto_scheduler.auto_schedule';
        
        frappe.call({
            method: method,
            args: {
                academic_term: academic_term,
                timetable_for: scope,
                school: this.school_field.get_value() || null,
                department: this.department_field.get_value() || null,
                program: this.program_field.get_value() || null,
                save: !preview_only
            },
            callback: (r) => {
                this.is_running = false;
                if (r.message) {
                    this.show_results(r.message, preview_only);
                } else {
                    this.hide_progress();
                    frappe.msgprint(__('No results returned from scheduler'));
                }
            },
            error: (e) => {
                this.is_running = false;
                this.hide_progress();
                frappe.msgprint(__('Error running scheduler: ') + (e.message || 'Unknown error'));
            }
        });
    }
    
    show_progress() {
        this.$container.find('#progress-container').addClass('active');
        this.$container.find('#results-container').removeClass('active');
        this.update_progress(0, 'Starting...');
    }
    
    hide_progress() {
        this.$container.find('#progress-container').removeClass('active');
    }
    
    update_progress(progress, message) {
        this.$container.find('#progress-bar').css('width', progress + '%');
        this.$container.find('#progress-message').text(message);
    }
    
    show_results(result, preview_only = false) {
        this.hide_progress();
        this.$container.find('#results-container').addClass('active');
        
        const stats = result.stats || {};
        const entries = result.entries || [];
        const unscheduled = result.unscheduled || [];
        
        // Render stats
        this.$container.find('#stats-grid').html(`
            <div class="stat-box">
                <div class="stat-value">${stats.total_courses || 0}</div>
                <div class="stat-label">Total Courses</div>
            </div>
            <div class="stat-box success">
                <div class="stat-value">${entries.length}</div>
                <div class="stat-label">Entries Created</div>
            </div>
            <div class="stat-box ${unscheduled.length ? 'warning' : 'success'}">
                <div class="stat-value">${unscheduled.length}</div>
                <div class="stat-label">Unscheduled</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">${stats.iterations || 1}</div>
                <div class="stat-label">Iterations</div>
            </div>
        `);
        
        // Render preview table
        if (entries.length) {
            const dayOrder = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7};
            entries.sort((a, b) => {
                const dayDiff = (dayOrder[a.day] || 8) - (dayOrder[b.day] || 8);
                if (dayDiff !== 0) return dayDiff;
                return (a.start_time || '').toString().localeCompare((b.start_time || '').toString());
            });
            
            let tableHtml = `
                <table class="preview-table">
                    <thead>
                        <tr>
                            <th>Course</th>
                            <th>Day</th>
                            <th>Time</th>
                            <th>Room</th>
                            <th>Instructor</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            entries.slice(0, 50).forEach(entry => {
                tableHtml += `
                    <tr>
                        <td><strong>${entry.course_code || ''}</strong> ${entry.course || ''}</td>
                        <td>${entry.day || ''}</td>
                        <td>${this.format_time(entry.start_time)} - ${this.format_time(entry.end_time)}</td>
                        <td>${entry.room || ''}</td>
                        <td>${entry.instructor || ''}</td>
                        <td>${entry.class_type || 'Lecture'}</td>
                    </tr>
                `;
            });
            
            if (entries.length > 50) {
                tableHtml += `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);">... and ${entries.length - 50} more entries</td></tr>`;
            }
            
            tableHtml += '</tbody></table>';
            this.$container.find('#schedule-preview').html(tableHtml);
        } else {
            this.$container.find('#schedule-preview').html(`
                <div style="text-align:center;padding:40px;color:var(--text-muted);">
                    <i class="fa fa-calendar-times-o" style="font-size:48px;margin-bottom:15px;"></i>
                    <p>No entries were generated. Check that courses have credit hours and resources are available.</p>
                </div>
            `);
        }
        
        // Render unscheduled courses
        if (unscheduled.length) {
            let html = `<div class="unscheduled-list"><h5><i class="fa fa-exclamation-triangle"></i> Unscheduled Courses (${unscheduled.length})</h5>`;
            unscheduled.forEach(item => {
                html += `<div class="unscheduled-item"><strong>${item.course}</strong>: ${item.reason}</div>`;
            });
            html += '</div>';
            this.$container.find('#unscheduled-container').html(html);
        } else {
            this.$container.find('#unscheduled-container').html('');
        }
        
        // Render action buttons
        let actionsHtml = '';
        if (result.save_result && result.save_result.timetable) {
            actionsHtml = `
                <a class="btn btn-success btn-sm" href="/app/timetable/${result.save_result.timetable}">
                    <i class="fa fa-external-link"></i> View Timetable
                </a>
                <a class="btn btn-default btn-sm" href="/app/timetable-entry?timetable=${result.save_result.timetable}">
                    <i class="fa fa-list"></i> View All Entries (${result.save_result.created})
                </a>
            `;
        } else if (preview_only && entries.length) {
            actionsHtml = `
                <div style="padding:15px;background:var(--control-bg);border-radius:8px;color:var(--text-muted);">
                    <i class="fa fa-info-circle"></i> This is a preview. Click <strong>"Generate Schedule"</strong> to save these ${entries.length} entries.
                </div>
            `;
        }
        this.$container.find('#action-buttons').html(actionsHtml);
    }
    
    format_time(time) {
        if (!time) return '';
        if (typeof time === 'number') {
            const hours = Math.floor(time / 3600);
            const mins = Math.floor((time % 3600) / 60);
            return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
        }
        if (typeof time === 'string') {
            const parts = time.split(':');
            if (parts.length >= 2) {
                return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`;
            }
        }
        return String(time);
    }
    
    clear_results() {
        this.$container.find('#results-container').removeClass('active');
        this.$container.find('#progress-container').removeClass('active');
    }
}
