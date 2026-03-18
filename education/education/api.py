# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import json

import frappe
from frappe import _
from frappe.email.doctype.email_group.email_group import add_subscribers
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate, today
from frappe.utils.dateutils import get_dates_from_timegrain


def get_course(program):
	"""Return list of courses for a particular program
	:param program: Program
	"""
	courses = frappe.db.sql(
		"""select course, course_name from `tabProgram Course` where parent=%s""",
		(program),
		as_dict=1,
	)
	return courses


@frappe.whitelist()
def enroll_student(source_name):
	"""Creates a Student Record and returns a Program Enrollment.

	:param source_name: Student Applicant.
	"""
	frappe.publish_realtime(
		"enroll_student_progress", {"progress": [1, 4]}, user=frappe.session.user
	)
	student = get_mapped_doc(
		"Student Applicant",
		source_name,
		{
			"Student Applicant": {
				"doctype": "Student",
				"field_map": {
					"name": "student_applicant",
				},
			}
		},
		ignore_permissions=True,
	)
	student.save()

	student_applicant = frappe.db.get_value(
		"Student Applicant",
		source_name,
		["student_category", "program", "academic_year", "academic_term"],
		as_dict=True,
	)
	program_enrollment = frappe.new_doc("Program Enrollment")
	program_enrollment.student = student.name
	program_enrollment.student_category = student_applicant.student_category
	program_enrollment.student_name = student.student_name
	program_enrollment.program = student_applicant.program
	program_enrollment.academic_year = student_applicant.academic_year
	program_enrollment.academic_term = student_applicant.academic_term
	program_enrollment.save()

	frappe.publish_realtime(
		"enroll_student_progress", {"progress": [2, 4]}, user=frappe.session.user
	)
	return program_enrollment


@frappe.whitelist()
def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
	"""Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if course_schedule:
		return frappe.get_list(
			"Student Attendance", filters={"course_schedule": course_schedule}
		)
	else:
		return frappe.get_list(
			"Student Attendance", filters={"student_group": student_group, "date": date}
		)


@frappe.whitelist()
def mark_attendance(
	students_present, students_absent, course_schedule=None, student_group=None, date=None
):
	"""Creates Multiple Attendance Records.

	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if student_group:
		academic_year = frappe.db.get_value("Student Group", student_group, "academic_year")
		if academic_year:
			year_start_date, year_end_date = frappe.db.get_value(
				"Academic Year", academic_year, ["year_start_date", "year_end_date"]
			)
			if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(
				year_end_date
			):
				frappe.throw(
					_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
				)

	present = json.loads(students_present)
	absent = json.loads(students_absent)

	for d in present:
		make_attendance_records(
			d["student"], d["student_name"], "Present", course_schedule, student_group, date
		)

	for d in absent:
		make_attendance_records(
			d["student"], d["student_name"], "Absent", course_schedule, student_group, date
		)

	frappe.db.commit()
	frappe.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(
	student, student_name, status, course_schedule=None, student_group=None, date=None
):
	"""Creates/Update Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent/Leave).
	"""
	student_attendance = frappe.get_doc(
		{
			"doctype": "Student Attendance",
			"student": student,
			"course_schedule": course_schedule,
			"student_group": student_group,
			"date": date,
		}
	)
	if not student_attendance:
		student_attendance = frappe.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.save()
	student_attendance.submit()


@frappe.whitelist()
def get_student_guardians(student):
	"""Returns List of Guardians of a Student.

	:param student: Student.
	"""
	guardians = frappe.get_all(
		"Student Guardian", fields=["guardian"], filters={"parent": student}
	)
	return guardians


@frappe.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	"""Returns List of student, student_name in Student Group.

	:param student_group: Student Group.
	"""
	if include_inactive:
		students = frappe.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group},
			order_by="group_roll_number",
		)
	else:
		students = frappe.get_all(
			"Student Group Student",
			fields=["student", "student_name"],
			filters={"parent": student_group, "active": 1},
			order_by="group_roll_number",
		)
	return students


@frappe.whitelist()
def get_fee_structure(program, academic_term=None):
	"""Returns Fee Structure.

	:param program: Program.
	:param academic_term: Academic Term.
	"""
	fee_structure = frappe.db.get_values(
		"Fee Structure",
		{"program": program, "academic_term": academic_term},
		"name",
		as_dict=True,
	)
	return fee_structure[0].name if fee_structure else None


@frappe.whitelist()
def get_fee_components(fee_structure):
	"""Returns Fee Components.

	:param fee_structure: Fee Structure.
	"""
	if fee_structure:
		fs = frappe.get_all(
			"Fee Component",
			fields=["fees_category", "description", "amount"],
			filters={"parent": fee_structure},
			order_by="idx",
		)
		return fs


@frappe.whitelist()
def get_fee_schedule(program, student_category=None):
	"""Returns Fee Schedule.

	:param program: Program.
	:param student_category: Student Category
	"""
	fs = frappe.get_all(
		"Program Fee",
		fields=["academic_term", "fee_schedule", "due_date", "amount"],
		filters={"parent": program, "student_category": student_category},
		order_by="idx",
	)
	return fs


@frappe.whitelist()
def collect_fees(fees, amt):
	paid_amount = flt(amt) + flt(frappe.db.get_value("Fees", fees, "paid_amount"))
	total_amount = flt(frappe.db.get_value("Fees", fees, "total_amount"))
	frappe.db.set_value("Fees", fees, "paid_amount", paid_amount)
	frappe.db.set_value("Fees", fees, "outstanding_amount", (total_amount - paid_amount))
	return paid_amount


@frappe.whitelist()
def get_course_schedule_events(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions

	conditions = get_event_conditions("Course Schedule", filters)

	data = frappe.db.sql(
		"""select name, course, color,
			timestamp(schedule_date, from_time) as from_time,
			timestamp(schedule_date, to_time) as to_time,
			room, student_group, 0 as 'allDay'
		from `tabCourse Schedule`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(
			conditions=conditions
		),
		{"start": start, "end": end},
		as_dict=True,
		update={"allDay": 0},
	)

	return data


@frappe.whitelist()
def get_assessment_criteria(course):
	"""Returns Assessmemt Criteria and their Weightage from Course Master.

	:param Course: Course
	"""
	return frappe.get_all(
		"Course Assessment Criteria",
		fields=["assessment_criteria", "weightage"],
		filters={"parent": course},
		order_by="idx",
	)


@frappe.whitelist()
def get_assessment_students(assessment_plan, student_group):
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		result = get_result(student.student, assessment_plan)
		if result:
			student_result = {}
			for d in result.details:
				student_result.update({d.assessment_criteria: [cstr(d.score), d.grade]})
			student_result.update(
				{"total_score": [cstr(result.total_score), result.grade], "comment": result.comment}
			)
			student.update(
				{
					"assessment_details": student_result,
					"docstatus": result.docstatus,
					"name": result.name,
				}
			)
		else:
			student.update({"assessment_details": None})
	return student_list


@frappe.whitelist()
def get_assessment_details(assessment_plan):
	"""Returns Assessment Criteria  and Maximum Score from Assessment Plan Master.

	:param Assessment Plan: Assessment Plan
	"""
	return frappe.get_all(
		"Assessment Plan Criteria",
		fields=["assessment_criteria", "maximum_score", "docstatus"],
		filters={"parent": assessment_plan},
		order_by="idx",
	)


@frappe.whitelist()
def get_result(student, assessment_plan):
	"""Returns Submitted Result of given student for specified Assessment Plan

	:param Student: Student
	:param Assessment Plan: Assessment Plan
	"""
	results = frappe.get_all(
		"Assessment Result",
		filters={
			"student": student,
			"assessment_plan": assessment_plan,
			"docstatus": ("!=", 2),
		},
	)
	if results:
		return frappe.get_doc("Assessment Result", results[0])
	else:
		return None


@frappe.whitelist()
def get_grade(grading_scale, percentage):
	"""Returns Grade based on the Grading Scale and Score.

	:param Grading Scale: Grading Scale
	:param Percentage: Score Percentage Percentage
	"""
	grading_scale_intervals = {}
	if not hasattr(frappe.local, "grading_scale"):
		grading_scale = frappe.get_all(
			"Grading Scale Interval",
			fields=["grade_code", "threshold"],
			filters={"parent": grading_scale},
		)
		frappe.local.grading_scale = grading_scale
	for d in frappe.local.grading_scale:
		grading_scale_intervals.update({d.threshold: d.grade_code})
	intervals = sorted(grading_scale_intervals.keys(), key=float, reverse=True)
	for interval in intervals:
		if flt(percentage) >= interval:
			grade = grading_scale_intervals.get(interval)
			break
		else:
			grade = ""
	return grade


@frappe.whitelist()
def mark_assessment_result(assessment_plan, scores):
	student_score = json.loads(scores)
	assessment_details = []
	for criteria in student_score.get("assessment_details"):
		assessment_details.append(
			{
				"assessment_criteria": criteria,
				"score": flt(student_score["assessment_details"][criteria]),
			}
		)
	assessment_result = get_assessment_result_doc(
		student_score["student"], assessment_plan
	)
	assessment_result.update(
		{
			"student": student_score.get("student"),
			"assessment_plan": assessment_plan,
			"comment": student_score.get("comment"),
			"total_score": student_score.get("total_score"),
			"details": assessment_details,
		}
	)
	assessment_result.save()
	details = {}
	for d in assessment_result.details:
		details.update({d.assessment_criteria: d.grade})
	assessment_result_dict = {
		"name": assessment_result.name,
		"student": assessment_result.student,
		"total_score": assessment_result.total_score,
		"grade": assessment_result.grade,
		"details": details,
	}
	return assessment_result_dict


@frappe.whitelist()
def submit_assessment_results(assessment_plan, student_group):
	total_result = 0
	student_list = get_student_group_students(student_group)
	for i, student in enumerate(student_list):
		doc = get_result(student.student, assessment_plan)
		if doc and doc.docstatus == 0:
			total_result += 1
			doc.submit()
	return total_result


def get_assessment_result_doc(student, assessment_plan):
	assessment_result = frappe.get_all(
		"Assessment Result",
		filters={
			"student": student,
			"assessment_plan": assessment_plan,
			"docstatus": ("!=", 2),
		},
	)
	if assessment_result:
		doc = frappe.get_doc("Assessment Result", assessment_result[0])
		if doc.docstatus == 0:
			return doc
		elif doc.docstatus == 1:
			frappe.msgprint(_("Result already Submitted"))
			return None
	else:
		return frappe.new_doc("Assessment Result")


@frappe.whitelist()
def update_email_group(doctype, name):
	if not frappe.db.exists("Email Group", name):
		email_group = frappe.new_doc("Email Group")
		email_group.title = name
		email_group.save()
	email_list = []
	students = []
	if doctype == "Student Group":
		students = get_student_group_students(name)
	for stud in students:
		for guard in get_student_guardians(stud.student):
			email = frappe.db.get_value("Guardian", guard.guardian, "email_address")
			if email:
				email_list.append(email)
	add_subscribers(name, email_list)

@frappe.whitelist()
def get_current_enrollment(student, academic_year=None):
        # If academic_year is not passed, use today's date
        compare_date = getdate(academic_year) if academic_year else getdate(today())

        program_enrollment_list = frappe.db.sql(
                """
                SELECT
                        pe.name AS program_enrollment, pe.student_name, pe.program, pe.student_batch_name AS student_batch,
                        pe.student_category, pe.academic_term, pe.academic_year
                FROM
                        `tabProgram Enrollment` pe
                JOIN
                        `tabAcademic Year` ay ON pe.academic_year = ay.name
                WHERE
                        pe.student = %s
                        AND ay.year_end_date >= %s
                ORDER BY
                        pe.creation DESC
                """,
                (student, compare_date),
                as_dict=1,
        )

        # Fallback: If no current enrollment found, get the most recent submitted one
        if not program_enrollment_list:
                program_enrollment_list = frappe.db.sql(
                        """
                        SELECT
                                pe.name AS program_enrollment, pe.student_name, pe.program, pe.student_batch_name AS student_batch,
                                pe.student_category, pe.academic_term, pe.academic_year
                        FROM
                                `tabProgram Enrollment` pe
                        WHERE
                                pe.student = %s
                                AND pe.docstatus = 1
                        ORDER BY
                                pe.creation DESC
                        LIMIT 1
                        """,
                        (student,),
                        as_dict=1,
                )

        if program_enrollment_list:
                return program_enrollment_list[0]
        else:
                return None

@frappe.whitelist()
def get_instructors(student_group):
	return frappe.get_all(
		"Student Group Instructor", {"parent": student_group}, pluck="instructor"
	)


@frappe.whitelist()
def get_user_info():
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	current_user = frappe.db.get_list(
		"User",
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		filters={"name": frappe.session.user},
	)[0]
	current_user["session_user"] = True
	return current_user


@frappe.whitelist()
def get_student_info():
	email = frappe.session.user
	if email == "Administrator":
		return
	
	# Use ignore_permissions to bypass role restrictions
	student_list = frappe.db.get_list(
		"Student",
		fields=["*"],
		filters={"user": email},
		ignore_permissions=True
	)
	
	if not student_list:
		frappe.throw(
			f"No student record found linked to your account ({email}). Please contact the administrator.",
			title="Student Record Not Found"
		)
	
	student_info = student_list[0]

	current_program = get_current_enrollment(student_info.name)
	if current_program:
		student_groups = get_student_groups(student_info.name, current_program.program)
		student_info["student_groups"] = student_groups
		student_info["current_program"] = current_program
	return student_info


@frappe.whitelist()
def get_student_programs(student):
	# student = 'EDU-STU-2023-00043'
	programs = frappe.db.get_list(
		"Program Enrollment",
		fields=["program", "name"],
		filters={"docstatus": 1, "student": student},
	)
	return programs


def get_student_groups(student, program_name):
	# student = 'EDU-STU-2023-00043'

	student_group = frappe.qb.DocType("Student Group")
	student_group_students = frappe.qb.DocType("Student Group Student")

	student_group_query = (
		frappe.qb.from_(student_group)
		.inner_join(student_group_students)
		.on(student_group.name == student_group_students.parent)
		.select((student_group_students.parent).as_("label"))
		.where(student_group_students.student == student)
		.where(student_group.program == program_name)
		.run(as_dict=1)
	)

	return student_group_query


@frappe.whitelist()
def get_course_list_based_on_program(program_name):
	program = frappe.get_doc("Program", program_name)

	course_list = []

	for course in program.courses:
		course_list.append(course.course)
	return course_list


@frappe.whitelist()
def get_course_schedule_for_student(program_name, student_groups):
	student_groups = [sg.get("label") for sg in student_groups]

	schedule = frappe.db.get_list(
		"Course Schedule",
		fields=[
			"schedule_date",
			"room",
			"class_schedule_color",
			"course",
			"from_time",
			"to_time",
			"instructor",
			"title",
			"name",
		],
		filters={"program": program_name, "student_group": ["in", student_groups]},
		order_by="schedule_date asc",
	)
	return schedule


@frappe.whitelist()
def apply_leave(leave_data, program_name):
	attendance_based_on_course_schedule = frappe.db.get_single_value(
		"Education Settings", "attendance_based_on_course_schedule"
	)
	if attendance_based_on_course_schedule:
		apply_leave_based_on_course_schedule(leave_data, program_name)
	else:
		apply_leave_based_on_student_group(leave_data, program_name)


def apply_leave_based_on_course_schedule(leave_data, program_name):
	course_schedule_in_leave_period = frappe.db.get_list(
		"Course Schedule",
		fields=["name", "schedule_date"],
		filters={
			"program": program_name,
			"schedule_date": [
				"between",
				[leave_data.get("from_date"), leave_data.get("to_date")],
			],
		},
		order_by="schedule_date asc",
	)
	if not course_schedule_in_leave_period:
		frappe.throw(_("No classes found in the leave period"))
	for course_schedule in course_schedule_in_leave_period:
		# check if attendance record does not exist for the student on the course schedule
		if not frappe.db.exists(
			"Student Attendance",
			{"course_schedule": course_schedule.get("name"), "docstatus": 1},
		):
			make_attendance_records(
				leave_data.get("student"),
				leave_data.get("student_name"),
				"Leave",
				course_schedule.get("name"),
				None,
				course_schedule.get("schedule_date"),
			)


def apply_leave_based_on_student_group(leave_data, program_name):
	student_groups = get_student_groups(leave_data.get("student"), program_name)
	leave_dates = get_dates_from_timegrain(
		leave_data.get("from_date"), leave_data.get("to_date")
	)
	for student_group in student_groups:
		for leave_date in leave_dates:
			make_attendance_records(
				leave_data.get("student"),
				leave_data.get("student_name"),
				"Leave",
				None,
				student_group.get("label"),
				leave_date,
			)


@frappe.whitelist()
def get_student_invoices(student):
	student_sales_invoices = []

	sales_invoice_list = frappe.db.get_list(
		"Sales Invoice",
		filters={
			"student": student,
			"status": ["in", ["Paid", "Unpaid", "Overdue", "Partly Paid"]],
			"docstatus": 1,
		},
		fields=[
			"name",
			"status",
			"student",
			"due_date",
			"fee_schedule",
			"outstanding_amount",
			"currency",
			"grand_total",
		],
		order_by="status desc",
	)

	for si in sales_invoice_list:
		student_program_invoice_status = {}
		student_program_invoice_status["status"] = si.status
		student_program_invoice_status["program"] = get_program_from_fee_schedule(
			si.fee_schedule
		)
		symbol = get_currency_symbol(si.get("currency", "INR"))
		student_program_invoice_status["amount"] = symbol + " " + str(si.outstanding_amount)
		student_program_invoice_status["invoice"] = si.name
		if si.status == "Paid":
			student_program_invoice_status["amount"] = symbol + " " + str(si.grand_total)
			student_program_invoice_status[
				"payment_date"
			] = get_posting_date_from_payment_entry_against_sales_invoice(si.name)
			student_program_invoice_status["due_date"] = "-"
		else:
			student_program_invoice_status["due_date"] = si.due_date
			student_program_invoice_status["payment_date"] = "-"

		student_sales_invoices.append(student_program_invoice_status)

	print_format = get_fees_print_format() or "Standard"

	return {"invoices": student_sales_invoices, "print_format": print_format}


def get_currency_symbol(currency):
	return frappe.db.get_value("Currency", currency, "symbol") or currency


def get_posting_date_from_payment_entry_against_sales_invoice(sales_invoice):
	payment_entry = frappe.qb.DocType("Payment Entry")
	payment_entry_reference = frappe.qb.DocType("Payment Entry Reference")

	q = (
		frappe.qb.from_(payment_entry)
		.inner_join(payment_entry_reference)
		.on(payment_entry.name == payment_entry_reference.parent)
		.select(payment_entry.posting_date)
		.where(payment_entry_reference.reference_name == sales_invoice)
	).run(as_dict=1)

	if len(q) > 0:
		payment_date = q[0].get("posting_date")
		return payment_date


def get_fees_print_format():
	return frappe.db.get_value(
		"Property Setter",
		dict(property="default_print_format", doc_type="Sales Invoice"),
		"value",
	)


def get_program_from_fee_schedule(fee_schedule):

	program = frappe.db.get_value(
		"Fee Schedule", filters={"name": fee_schedule}, fieldname=["program"]
	)
	return program


@frappe.whitelist()
def get_school_abbr_logo():
	abbr = frappe.db.get_single_value(
		"Education Settings", "school_college_name_abbreviation"
	)
	logo = frappe.db.get_single_value("Education Settings", "school_college_logo")
	return {"name": abbr, "logo": logo}


@frappe.whitelist()
def get_student_attendance(student, student_group):
	return frappe.db.get_list(
		"Student Attendance",
		filters={"student": student, "student_group": student_group, "docstatus": 1},
		fields=["date", "status", "name"],
	)


# ============================================================
# UEAB Student Portal - New APIs
# ============================================================

# Graduation & Clearance APIs
@frappe.whitelist()
def get_graduation_status(student):
	"""Get student graduation eligibility and status.
	
	:param student: Student ID
	:returns: dict with graduation eligibility info
	"""
	enrollment = get_current_enrollment(student)
	if not enrollment:
		return {"eligible": False, "message": "No active enrollment found"}
	
	program = enrollment.get("program")
	program_doc = frappe.get_doc("Program", program)
	
	# Get completed courses
	completed_courses = frappe.db.get_list(
		"Assessment Result",
		filters={"student": student, "docstatus": 1},
		fields=["course"],
		distinct=True
	)
	completed_course_ids = [c.course for c in completed_courses]
	
	# Get required courses from program
	required_courses = [c.course for c in program_doc.courses]
	
	# Calculate completion
	total_required = len(required_courses)
	total_completed = len(set(completed_course_ids) & set(required_courses))
	completion_percentage = (total_completed / total_required * 100) if total_required > 0 else 0
	
	return {
		"student": student,
		"program": program,
		"total_required_courses": total_required,
		"completed_courses": total_completed,
		"completion_percentage": round(completion_percentage, 1),
		"eligible": completion_percentage >= 100,
		"status": "Eligible for Graduation" if completion_percentage >= 100 else "In Progress"
	}


@frappe.whitelist()
def get_clearance_status(student):
	"""Get clearance status by department.
	
	:param student: Student ID
	:returns: dict with clearance status per department
	"""
	# Check finance clearance
	outstanding_invoices = frappe.db.get_list(
		"Sales Invoice",
		filters={
			"student": student,
			"status": ["in", ["Unpaid", "Overdue", "Partly Paid"]],
			"docstatus": 1
		},
		fields=["name", "outstanding_amount"]
	)
	finance_cleared = len(outstanding_invoices) == 0
	finance_balance = sum(inv.outstanding_amount for inv in outstanding_invoices)
	
	# Check library clearance (placeholder - needs Library doctype)
	library_cleared = True
	library_pending = 0
	
	# Check hostel clearance (placeholder - needs Room Allocation doctype)
	hostel_cleared = True
	
	# Check academic clearance
	graduation_status = get_graduation_status(student)
	academic_cleared = graduation_status.get("completion_percentage", 0) >= 100
	
	departments = [
		{
			"department": "Finance",
			"cleared": finance_cleared,
			"pending_items": 0 if finance_cleared else len(outstanding_invoices),
			"details": f"Outstanding balance: {finance_balance}" if not finance_cleared else "All fees paid"
		},
		{
			"department": "Library",
			"cleared": library_cleared,
			"pending_items": library_pending,
			"details": "All books returned" if library_cleared else "Books pending return"
		},
		{
			"department": "Hostel",
			"cleared": hostel_cleared,
			"pending_items": 0,
			"details": "Room cleared" if hostel_cleared else "Room clearance pending"
		},
		{
			"department": "Academic",
			"cleared": academic_cleared,
			"pending_items": 0,
			"details": "All requirements met" if academic_cleared else "Course requirements pending"
		},
		{
			"department": "Student Affairs",
			"cleared": True,
			"pending_items": 0,
			"details": "No pending issues"
		}
	]
	
	total_departments = len(departments)
	cleared_departments = sum(1 for d in departments if d["cleared"])
	overall_progress = round(cleared_departments / total_departments * 100, 1)
	
	return {
		"student": student,
		"departments": departments,
		"overall_cleared": cleared_departments == total_departments,
		"overall_progress": overall_progress,
		"cleared_count": cleared_departments,
		"total_count": total_departments
	}


@frappe.whitelist()
def get_degree_audit(student, program=None):
	"""Get degree requirements vs completed courses.
	
	:param student: Student ID
	:param program: Program name (optional, uses current enrollment if not provided)
	:returns: dict with degree audit information
	"""
	if not program:
		enrollment = get_current_enrollment(student)
		if not enrollment:
			return {"error": "No active enrollment found"}
		program = enrollment.get("program")
	
	program_doc = frappe.get_doc("Program", program)
	
	# Get all required courses
	required_courses = []
	for course in program_doc.courses:
		course_doc = frappe.get_doc("Course", course.course)
		required_courses.append({
			"course": course.course,
			"course_name": course_doc.course_name,
			"required": course.required if hasattr(course, "required") else True
		})
	
	# Get completed courses with grades
	completed_results = frappe.db.get_list(
		"Assessment Result",
		filters={"student": student, "docstatus": 1},
		fields=["course", "total_score", "maximum_score", "grade"]
	)
	completed_map = {r.course: r for r in completed_results}
	
	# Build audit
	audit_items = []
	total_credits = 0
	earned_credits = 0
	
	for req in required_courses:
		completed = req["course"] in completed_map
		result = completed_map.get(req["course"], {})
		
		item = {
			"course": req["course"],
			"course_name": req["course_name"],
			"required": req["required"],
			"completed": completed,
			"grade": result.get("grade", "-"),
			"score": f"{result.get('total_score', '-')}/{result.get('maximum_score', '-')}" if completed else "-",
			"status": "Completed" if completed else "Pending"
		}
		audit_items.append(item)
		total_credits += 1
		if completed:
			earned_credits += 1
	
	return {
		"student": student,
		"program": program,
		"program_name": program_doc.program_name,
		"audit_items": audit_items,
		"total_requirements": total_credits,
		"completed_requirements": earned_credits,
		"completion_percentage": round(earned_credits / total_credits * 100, 1) if total_credits > 0 else 0
	}


# Residence/Housing APIs
@frappe.whitelist()
def get_student_room_allocation(student):
	"""Get current room assignment for a student.
	
	:param student: Student ID
	:returns: dict with room allocation details
	"""
	# Check if Room Allocation doctype exists
	if not frappe.db.exists("DocType", "Room Allocation"):
		return {
			"allocated": False,
			"message": "Room allocation system not configured"
		}
	
	allocation = frappe.db.get_list(
		"Room Allocation",
		filters={"student": student, "status": "Active"},
		fields=["name", "room", "building", "floor", "allocation_date", "expiry_date"],
		limit=1
	)
	
	if allocation:
		return {
			"allocated": True,
			"allocation": allocation[0]
		}
	
	return {
		"allocated": False,
		"message": "No active room allocation found"
	}


@frappe.whitelist()
def get_available_rooms():
	"""Get available rooms for housing application.
	
	:returns: list of available rooms
	"""
	if not frappe.db.exists("DocType", "Room"):
		return []
	
	rooms = frappe.db.get_list(
		"Room",
		filters={"status": "Available"},
		fields=["name", "room_number", "building", "floor", "capacity", "room_type", "amenities"]
	)
	
	return rooms


@frappe.whitelist()
def apply_for_housing(student, room_preference, academic_year=None):
	"""Submit housing application.
	
	:param student: Student ID
	:param room_preference: Preferred room or room type
	:param academic_year: Academic year (optional)
	:returns: dict with application status
	"""
	if not frappe.db.exists("DocType", "Housing Application"):
		return {
			"success": False,
			"message": "Housing application system not configured"
		}
	
	# Check for existing application
	existing = frappe.db.exists(
		"Housing Application",
		{"student": student, "status": ["in", ["Pending", "Approved"]]}
	)
	
	if existing:
		return {
			"success": False,
			"message": "You already have a pending or approved housing application"
		}
	
	# Create new application
	application = frappe.new_doc("Housing Application")
	application.student = student
	application.room_preference = room_preference
	application.academic_year = academic_year or frappe.defaults.get_defaults().get("academic_year")
	application.status = "Pending"
	application.application_date = today()
	application.save(ignore_permissions=True)
	
	return {
		"success": True,
		"application": application.name,
		"message": "Housing application submitted successfully"
	}


@frappe.whitelist()
def submit_maintenance_request(student, room, issue_type, description, priority="Medium"):
	"""Submit room maintenance request.
	
	:param student: Student ID
	:param room: Room number/ID
	:param issue_type: Type of issue
	:param description: Detailed description
	:param priority: Priority level (Low, Medium, High)
	:returns: dict with request status
	"""
	if not frappe.db.exists("DocType", "Maintenance Request"):
		return {
			"success": False,
			"message": "Maintenance request system not configured"
		}
	
	request = frappe.new_doc("Maintenance Request")
	request.student = student
	request.room = room
	request.issue_type = issue_type
	request.description = description
	request.priority = priority
	request.status = "Open"
	request.request_date = today()
	request.save(ignore_permissions=True)
	
	return {
		"success": True,
		"request": request.name,
		"message": "Maintenance request submitted successfully"
	}


# Student Governance APIs
@frappe.whitelist()
def get_student_council():
	"""Get current student council members.
	
	:returns: list of council members
	"""
	if not frappe.db.exists("DocType", "Student Council Member"):
		return []
	
	council = frappe.db.get_list(
		"Student Council Member",
		filters={"status": "Active"},
		fields=["name", "student", "position", "term_start", "term_end", "photo"],
		order_by="position"
	)
	
	# Enrich with student details
	for member in council:
		student_info = frappe.db.get_value(
			"Student",
			member.student,
			["student_name", "student_email_id"],
			as_dict=True
		)
		if student_info:
			member.update(student_info)
	
	return council


@frappe.whitelist()
def get_clubs_and_organizations():
	"""Get list of student clubs and organizations.
	
	:returns: list of clubs
	"""
	if not frappe.db.exists("DocType", "Student Club"):
		return []
	
	clubs = frappe.db.get_list(
		"Student Club",
		filters={"status": "Active"},
		fields=["name", "club_name", "description", "category", "meeting_schedule", "advisor", "logo"]
	)
	
	return clubs


@frappe.whitelist()
def get_student_events(limit=10):
	"""Get upcoming events.
	
	:param limit: Maximum number of events to return
	:returns: list of events
	"""
	if not frappe.db.exists("DocType", "Student Event"):
		return []
	
	events = frappe.db.get_list(
		"Student Event",
		filters={"event_date": [">=", today()], "status": "Scheduled"},
		fields=["name", "event_name", "event_date", "event_time", "venue", "description", "category", "organizer"],
		order_by="event_date asc",
		limit=limit
	)
	
	return events


@frappe.whitelist()
def submit_feedback(student, feedback_type, subject, message, is_anonymous=False):
	"""Submit student feedback or complaint.
	
	:param student: Student ID
	:param feedback_type: Type of feedback (Suggestion, Complaint, General)
	:param subject: Subject line
	:param message: Detailed message
	:param is_anonymous: Whether to submit anonymously
	:returns: dict with submission status
	"""
	if not frappe.db.exists("DocType", "Student Feedback"):
		return {
			"success": False,
			"message": "Feedback system not configured"
		}
	
	feedback = frappe.new_doc("Student Feedback")
	feedback.student = None if is_anonymous else student
	feedback.feedback_type = feedback_type
	feedback.subject = subject
	feedback.message = message
	feedback.is_anonymous = is_anonymous
	feedback.status = "Open"
	feedback.submission_date = today()
	feedback.save(ignore_permissions=True)
	
	return {
		"success": True,
		"feedback": feedback.name,
		"message": "Feedback submitted successfully"
	}


# Transcripts APIs
@frappe.whitelist()
def get_transcript_data(student):
	"""Get complete academic transcript data.
	
	:param student: Student ID
	:returns: dict with transcript information
	"""
	student_doc = frappe.get_doc("Student", student)
	
	# Get all program enrollments
	enrollments = frappe.db.get_list(
		"Program Enrollment",
		filters={"student": student, "docstatus": 1},
		fields=["name", "program", "academic_year", "academic_term", "student_batch_name"],
		order_by="creation"
	)
	
	transcript_data = {
		"student": student,
		"student_name": student_doc.student_name,
		"student_email": student_doc.student_email_id,
		"programs": []
	}
	
	for enrollment in enrollments:
		# Get assessment results for this program
		results = frappe.db.get_list(
			"Assessment Result",
			filters={
				"student": student,
				"program": enrollment.program,
				"docstatus": 1
			},
			fields=["course", "assessment_group", "total_score", "maximum_score", "grade", "academic_term"],
			order_by="course, assessment_group"
		)
		
		# Group by academic term
		term_results = {}
		for result in results:
			term = result.academic_term or "Unknown"
			if term not in term_results:
				term_results[term] = []
			term_results[term].append(result)
		
		program_data = {
			"program": enrollment.program,
			"academic_year": enrollment.academic_year,
			"batch": enrollment.student_batch_name,
			"terms": []
		}
		
		for term, term_courses in term_results.items():
			term_data = {
				"term": term,
				"courses": term_courses,
				"gpa": calculate_term_gpa(term_courses)
			}
			program_data["terms"].append(term_data)
		
		transcript_data["programs"].append(program_data)
	
	return transcript_data


def calculate_term_gpa(courses):
	"""Calculate GPA for a term's courses.
	
	:param courses: List of course results
	:returns: GPA value
	"""
	if not courses:
		return 0.0
	
	total_score = sum(c.get("total_score", 0) for c in courses)
	total_max = sum(c.get("maximum_score", 100) for c in courses)
	
	if total_max == 0:
		return 0.0
	
	percentage = (total_score / total_max) * 100
	
	# Convert percentage to GPA (4.0 scale)
	if percentage >= 90:
		return 4.0
	elif percentage >= 80:
		return 3.5
	elif percentage >= 70:
		return 3.0
	elif percentage >= 60:
		return 2.5
	elif percentage >= 50:
		return 2.0
	else:
		return 0.0


@frappe.whitelist()
def request_official_transcript(student, copies=1, delivery_method="Pickup"):
	"""Request official transcript document.
	
	:param student: Student ID
	:param copies: Number of copies requested
	:param delivery_method: Pickup or Mail
	:returns: dict with request status
	"""
	if not frappe.db.exists("DocType", "Transcript Request"):
		return {
			"success": False,
			"message": "Transcript request system not configured"
		}
	
	request = frappe.new_doc("Transcript Request")
	request.student = student
	request.copies = copies
	request.delivery_method = delivery_method
	request.status = "Pending"
	request.request_date = today()
	request.save(ignore_permissions=True)
	
	return {
		"success": True,
		"request": request.name,
		"message": "Transcript request submitted successfully"
	}


# Course Registration APIs
@frappe.whitelist()
def get_available_courses_for_registration(student, program=None, academic_term=None):
	"""Get courses available for registration.
	
	:param student: Student ID
	:param program: Program name (optional)
	:param academic_term: Academic term (optional)
	:returns: list of available courses
	"""
	if not program:
		enrollment = get_current_enrollment(student)
		if not enrollment:
			return []
		program = enrollment.get("program")
	
	program_doc = frappe.get_doc("Program", program)
	
	# Get already registered courses
	registered = frappe.db.get_list(
		"Course Enrollment",
		filters={"student": student, "program": program},
		fields=["course"],
		pluck="course"
	) if frappe.db.exists("DocType", "Course Enrollment") else []
	
	available_courses = []
	for course in program_doc.courses:
		if course.course not in registered:
			course_doc = frappe.get_doc("Course", course.course)
			available_courses.append({
				"course": course.course,
				"course_name": course_doc.course_name,
				"course_abbr": course_doc.course_abbr if hasattr(course_doc, "course_abbr") else "",
				"description": course_doc.description if hasattr(course_doc, "description") else ""
			})
	
	return available_courses


@frappe.whitelist()
def register_for_course(student, course, academic_term=None):
	"""Register student for a course.
	
	:param student: Student ID
	:param course: Course ID
	:param academic_term: Academic term (optional)
	:returns: dict with registration status
	"""
	enrollment = get_current_enrollment(student)
	if not enrollment:
		return {
			"success": False,
			"message": "No active enrollment found"
		}
	
	# Check if Course Enrollment doctype exists
	if not frappe.db.exists("DocType", "Course Enrollment"):
		return {
			"success": False,
			"message": "Course enrollment system not configured"
		}
	
	# Check if already registered
	existing = frappe.db.exists(
		"Course Enrollment",
		{"student": student, "course": course}
	)
	
	if existing:
		return {
			"success": False,
			"message": "Already registered for this course"
		}
	
	# Create enrollment
	course_enrollment = frappe.new_doc("Course Enrollment")
	course_enrollment.student = student
	course_enrollment.course = course
	course_enrollment.program = enrollment.get("program")
	course_enrollment.academic_term = academic_term or enrollment.get("academic_term")
	course_enrollment.enrollment_date = today()
	course_enrollment.save(ignore_permissions=True)
	
	return {
		"success": True,
		"enrollment": course_enrollment.name,
		"message": "Successfully registered for course"
	}


@frappe.whitelist()
def drop_course(student, course, academic_term=None):
	"""Drop a course registration.
	
	:param student: Student ID
	:param course: Course ID
	:param academic_term: Academic term (optional)
	:returns: dict with drop status
	"""
	if not frappe.db.exists("DocType", "Course Enrollment"):
		return {
			"success": False,
			"message": "Course enrollment system not configured"
		}
	
	enrollment = frappe.db.get_value(
		"Course Enrollment",
		{"student": student, "course": course},
		"name"
	)
	
	if not enrollment:
		return {
			"success": False,
			"message": "Not registered for this course"
		}
	
	frappe.delete_doc("Course Enrollment", enrollment, ignore_permissions=True)
	
	return {
		"success": True,
		"message": "Successfully dropped course"
	}


# Notifications APIs
@frappe.whitelist()
def get_student_notifications(student, limit=20):
	"""Get student notifications.
	
	:param student: Student ID
	:param limit: Maximum number of notifications
	:returns: list of notifications
	"""
	# Get student's email
	email = frappe.db.get_value("Student", student, "student_email_id")
	
	if not email:
		return []
	
	# Get notifications from Notification Log
	notifications = frappe.db.get_list(
		"Notification Log",
		filters={"for_user": email},
		fields=["name", "subject", "document_type", "document_name", "read", "creation"],
		order_by="creation desc",
		limit=limit
	)
	
	return notifications


@frappe.whitelist()
def mark_notification_read(notification_id):
	"""Mark notification as read.
	
	:param notification_id: Notification ID
	:returns: dict with status
	"""
	frappe.db.set_value("Notification Log", notification_id, "read", 1)
	
	return {
		"success": True,
		"message": "Notification marked as read"
	}


@frappe.whitelist()
def get_unread_notification_count(student):
	"""Get count of unread notifications.
	
	:param student: Student ID
	:returns: int count
	"""
	email = frappe.db.get_value("Student", student, "student_email_id")
	
	if not email:
		return 0
	
	count = frappe.db.count(
		"Notification Log",
		filters={"for_user": email, "read": 0}
	)
	
	return count


# Profile APIs
@frappe.whitelist()
def update_student_contact_info(student, email=None, phone=None, address=None):
	"""Update student contact information.
	
	:param student: Student ID
	:param email: New email address
	:param phone: New phone number
	:param address: New address
	:returns: dict with update status
	"""
	student_doc = frappe.get_doc("Student", student)
	
	if email:
		student_doc.student_email_id = email
	if phone:
		student_doc.student_mobile_number = phone
	if address:
		student_doc.address = address
	
	student_doc.save(ignore_permissions=True)
	
	return {
		"success": True,
		"message": "Contact information updated successfully"
	}


@frappe.whitelist()
def update_student_photo(student, photo):
	"""Update student profile photo.
	
	:param student: Student ID
	:param photo: Photo file path
	:returns: dict with update status
	"""
	frappe.db.set_value("Student", student, "image", photo)
	
	return {
		"success": True,
		"message": "Profile photo updated successfully"
	}


# Dashboard Stats API
@frappe.whitelist()
def get_student_dashboard_stats(student):
	"""Get dashboard statistics for a student.
	
	:param student: Student ID
	:returns: dict with dashboard stats
	"""
	enrollment = get_current_enrollment(student)
	
	# Get attendance stats
	if enrollment:
		attendance = frappe.db.get_list(
			"Student Attendance",
			filters={"student": student, "docstatus": 1},
			fields=["status"]
		)
		total_classes = len(attendance)
		present_classes = len([a for a in attendance if a.status == "Present"])
		attendance_percentage = round(present_classes / total_classes * 100, 1) if total_classes > 0 else 0
	else:
		attendance_percentage = 0
	
	# Get fee balance
	outstanding_invoices = frappe.db.get_list(
		"Sales Invoice",
		filters={
			"student": student,
			"status": ["in", ["Unpaid", "Overdue", "Partly Paid"]],
			"docstatus": 1
		},
		fields=["outstanding_amount", "currency"]
	)
	fee_balance = sum(inv.outstanding_amount for inv in outstanding_invoices)
	currency = outstanding_invoices[0].currency if outstanding_invoices else "KES"
	currency_symbol = get_currency_symbol(currency)
	
	# Get GPA (simplified calculation)
	results = frappe.db.get_list(
		"Assessment Result",
		filters={"student": student, "docstatus": 1},
		fields=["total_score", "maximum_score"]
	)
	if results:
		total_score = sum(r.total_score for r in results)
		total_max = sum(r.maximum_score for r in results)
		percentage = (total_score / total_max * 100) if total_max > 0 else 0
		# Convert to 4.0 scale
		if percentage >= 90:
			gpa = 4.0
		elif percentage >= 80:
			gpa = 3.5
		elif percentage >= 70:
			gpa = 3.0
		elif percentage >= 60:
			gpa = 2.5
		elif percentage >= 50:
			gpa = 2.0
		else:
			gpa = 0.0
	else:
		gpa = 0.0
	
	# Get unread notifications count
	notification_count = get_unread_notification_count(student)
	
	return {
		"gpa": gpa,
		"attendance_percentage": attendance_percentage,
		"fee_balance": f"{currency_symbol} {fee_balance:,.2f}",
		"unread_notifications": notification_count,
		"program": enrollment.get("program") if enrollment else None,
		"academic_year": enrollment.get("academic_year") if enrollment else None,
		"academic_term": enrollment.get("academic_term") if enrollment else None
	}


# Upcoming Classes API
@frappe.whitelist()
def get_upcoming_classes(student, limit=5):
	"""Get upcoming classes for a student.
	
	:param student: Student ID
	:param limit: Maximum number of classes to return
	:returns: list of upcoming classes
	"""
	enrollment = get_current_enrollment(student)
	if not enrollment:
		return []
	
	student_groups = get_student_groups(student, enrollment.get("program"))
	student_group_names = [sg.get("label") for sg in student_groups]
	
	schedule = frappe.db.get_list(
		"Course Schedule",
		filters={
			"program": enrollment.get("program"),
			"student_group": ["in", student_group_names],
			"schedule_date": [">=", today()]
		},
		fields=["schedule_date", "room", "course", "from_time", "to_time", "instructor", "title", "name"],
		order_by="schedule_date asc, from_time asc",
		limit=limit
	)
	
	return schedule
