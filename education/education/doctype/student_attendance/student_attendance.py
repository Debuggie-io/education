# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import formatdate, get_link_to_form, getdate, nowtime

from education.education.api import get_student_group_students


class StudentAttendance(Document):
    def validate(self):
        self.validate_mandatory()
        self.set_date()
        self.set_student_group()
        self.validate_student()
        self.validate_duplication()

    def set_date(self):
        if self.course_schedule:
            self.date = frappe.db.get_value(
                "Course Schedule", self.course_schedule, "schedule_date"
            )

    def validate_mandatory(self):
        """Validate mandatory fields based on attendance type"""
        attendance_type = getattr(self, 'attendance_type', None) or 'Class'
        
        if attendance_type == "Class":
            # For class attendance, require student_group or course_schedule
            if not (self.student_group or self.course_schedule):
                frappe.throw(
                    _("{0} or {1} is mandatory for Class Attendance").format(
                        frappe.bold("Student Group"), frappe.bold("Course Schedule")
                    ),
                    title=_("Mandatory Fields"),
                )
        elif attendance_type == "School Activity":
            # For activity attendance, require school_activity
            school_activity = getattr(self, 'school_activity', None)
            if not school_activity:
                frappe.throw(
                    _("{0} is mandatory for School Activity Attendance").format(
                        frappe.bold("School Activity")
                    ),
                    title=_("Mandatory Fields"),
                )

    def set_student_group(self):
        if self.course_schedule:
            self.student_group = frappe.db.get_value(
                "Course Schedule", self.course_schedule, "student_group"
            )

    def validate_student(self):
        if self.course_schedule:
            student_group = frappe.db.get_value(
                "Course Schedule", self.course_schedule, "student_group"
            )
            student_group_students = [
                d.student for d in get_student_group_students(student_group)
            ]
            if student_group and self.student not in student_group_students:
                student_group_doc = get_link_to_form("Student Group", student_group)
                frappe.throw(
                    _("Student {0} is not part of Student Group {1}").format(
                        frappe.bold(self.student), student_group_doc
                    )
                )

    def validate_duplication(self):
        """Check for duplicate attendance on same date for same event"""
        attendance_type = getattr(self, 'attendance_type', None) or 'Class'
        
        filters = {
            "student": self.student,
            "date": self.date,
            "docstatus": ("!=", 2),
            "name": ("!=", self.name)
        }
        
        if attendance_type == "Class":
            if self.course_schedule:
                filters["course_schedule"] = self.course_schedule
            elif self.student_group:
                filters["student_group"] = self.student_group
        else:
            school_activity = getattr(self, 'school_activity', None)
            if school_activity:
                filters["school_activity"] = school_activity
        
        existing = frappe.db.exists("Student Attendance", filters)
        
        if existing:
            frappe.throw(
                _("Attendance already recorded for {0} on {1}").format(
                    self.student, formatdate(self.date)
                ),
                title=_("Duplicate Attendance")
            )


def get_holiday_list(company=None):
    """Get holiday list - required by student_leave_application"""
    if not company:
        try:
            from erpnext import get_default_company
            company = get_default_company()
        except:
            pass
    
    if company:
        return frappe.db.get_value("Company", company, "default_holiday_list")
    
    # Fallback - get any holiday list
    holiday_list = frappe.db.get_value("Holiday List", filters={}, fieldname="name")
    return holiday_list
