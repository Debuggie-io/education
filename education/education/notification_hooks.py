
# Notification Hooks for Timetabling System

import frappe
from frappe import _

def send_timetable_notification(doc, method):
    """
    Send notifications when timetable entries are created or modified
    This is called via hooks
    """
    if doc.doctype != "Timetable Entry":
        return
    
    # Get affected users (students enrolled in the course, instructor)
    recipients = get_notification_recipients(doc)
    
    if not recipients:
        return
    
    # Determine notification type
    if method == "after_insert":
        subject = f"New Class Scheduled: {doc.course}"
        template = "new_class"
    elif method == "on_update":
        subject = f"Schedule Updated: {doc.course}"
        template = "class_updated"
    else:
        return
    
    # Queue the notification
    for recipient in recipients:
        try:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                template=template,
                args={
                    "doc": doc,
                    "course": doc.course,
                    "day": doc.day,
                    "time": f"{doc.start_time} - {doc.end_time}",
                    "room": doc.room,
                    "instructor": doc.instructor
                },
                delayed=True
            )
        except Exception as e:
            frappe.log_error(f"Failed to send notification to {recipient}: {str(e)}")


def get_notification_recipients(doc):
    """Get list of users who should receive notifications for this timetable entry"""
    recipients = []
    
    # Add instructor's email
    if doc.instructor:
        instructor_email = frappe.db.get_value("Instructor", doc.instructor, "user")
        if instructor_email:
            recipients.append(instructor_email)
    
    # Add students enrolled in the course
    # This requires Course Enrollment records
    enrolled_students = frappe.get_all("Course Enrollment",
        filters={"course": doc.course},
        fields=["student"]
    )
    
    for enrollment in enrolled_students:
        student_email = frappe.db.get_value("Student", enrollment.student, "user")
        if student_email:
            recipients.append(student_email)
    
    return list(set(recipients))  # Remove duplicates


def notify_instructor_assignment(doc, method):
    """Notify instructor when assigned to a class"""
    if doc.doctype != "Timetable Entry" or not doc.instructor:
        return
    
    instructor_user = frappe.db.get_value("Instructor", doc.instructor, "user")
    if not instructor_user:
        return
    
    # Create a system notification
    notification = frappe.get_doc({
        "doctype": "Notification Log",
        "subject": f"You have been assigned to teach {doc.course}",
        "email_content": f"""
            <p>You have been assigned to teach the following class:</p>
            <ul>
                <li><strong>Course:</strong> {doc.course}</li>
                <li><strong>Day:</strong> {doc.day}</li>
                <li><strong>Time:</strong> {doc.start_time} - {doc.end_time}</li>
                <li><strong>Room:</strong> {doc.room}</li>
            </ul>
        """,
        "for_user": instructor_user,
        "type": "Alert",
        "document_type": "Timetable Entry",
        "document_name": doc.name
    })
    notification.insert(ignore_permissions=True)


def on_timetable_submit(doc, method):
    """Actions when a timetable is submitted"""
    if doc.doctype != "Timetable" or doc.docstatus != 1:
        return
    
    # Notify all relevant HODs
    hods = frappe.get_all("Department",
        filters={"is_active": 1},
        fields=["head_of_department"]
    )
    
    for hod in hods:
        if hod.head_of_department:
            hod_user = frappe.db.get_value("Employee", hod.head_of_department, "user_id")
            if hod_user:
                frappe.sendmail(
                    recipients=[hod_user],
                    subject=f"Timetable Published: {doc.title}",
                    message=f"""
                        <p>The timetable <strong>{doc.title}</strong> has been published.</p>
                        <p>Academic Term: {doc.academic_term}</p>
                        <p>Please review the schedule for your department.</p>
                    """,
                    delayed=True
                )
