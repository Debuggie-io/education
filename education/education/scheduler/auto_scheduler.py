"""
UEAB Timetable Auto-Scheduler
"""

import frappe
from frappe.utils import today, add_months
from datetime import timedelta
import random
from collections import defaultdict


def safe_int(val, default=0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return default
        try:
            return int(float(val))
        except:
            return default
    return default


class TimetableScheduler:
    def __init__(self, academic_term, timetable_for="Entire University", 
                 school=None, department=None, program=None):
        self.academic_term = academic_term
        self.timetable_for = timetable_for
        self.school = school
        self.department = department
        self.program = program
        
        # Get academic year from term
        self.academic_year = None
        self.term_start = None
        self.term_end = None
        if academic_term:
            term_data = frappe.db.get_value("Academic Term", academic_term, 
                ["academic_year", "term_start_date", "term_end_date"], as_dict=True)
            if term_data:
                self.academic_year = term_data.get("academic_year")
                self.term_start = term_data.get("term_start_date")
                self.term_end = term_data.get("term_end_date")
        
        self.courses = []
        self.rooms = []
        self.labs = []
        self.instructors = []
        self.time_slots = []
        self.regular_slots = []
        self.lab_slots = []
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        self.room_schedule = defaultdict(list)
        self.instructor_schedule = defaultdict(list)
        self.course_schedule = defaultdict(list)
        self.reserved_times = []
        
        self.scheduled_entries = []
        self.unscheduled_courses = []
        self.stats = {"total_courses": 0, "scheduled": 0, "unscheduled": 0, "iterations": 0}
    
    def load_resources(self):
        self._progress(5, "Loading courses...")
        self._load_courses()
        
        self._progress(15, f"Found {len(self.courses)} courses")
        self._load_rooms()
        
        self._progress(25, f"Found {len(self.rooms)} rooms, {len(self.labs)} labs")
        self._load_instructors()
        
        self._progress(35, f"Found {len(self.instructors)} instructors")
        self._load_time_slots()
        self._load_reserved_times()
        
        self.stats["total_courses"] = len(self.courses)
        self._progress(40, f"Ready: {len(self.courses)} courses, {len(self.rooms)} rooms")
    
    def _progress(self, pct, msg):
        frappe.publish_realtime("scheduler_progress", {"progress": pct, "message": msg})
    
    def _load_courses(self):
        filters = {}
        if self.school:
            depts = frappe.get_all("Department", filters={"parent_department": self.school}, pluck="name")
            depts.append(self.school)
            filters["department"] = ["in", depts]
        if self.department:
            filters["department"] = self.department
        
        self.courses = frappe.get_all("Course", filters=filters,
            fields=["name", "course_name", "course_code", "department", "credit_hours", "contact_hours", "is_lab_course"])
        self.courses = [c for c in self.courses if safe_int(c.get("credit_hours")) > 0]
    
    def _load_rooms(self):
        all_rooms = frappe.get_all("Room",
            fields=["name", "room_number", "seating_capacity", "building", "is_lab", "lab_type"])
        
        for r in all_rooms:
            r["seating_capacity"] = safe_int(r.get("seating_capacity"), 30)
            if r.get("is_lab"):
                self.labs.append(r)
            else:
                self.rooms.append(r)
        
        self.rooms.sort(key=lambda x: x["seating_capacity"], reverse=True)
        self.labs.sort(key=lambda x: x["seating_capacity"], reverse=True)
    
    def _load_instructors(self):
        filters = {"department": self.department} if self.department else {}
        self.instructors = frappe.get_all("Instructor", filters=filters or None,
            fields=["name", "instructor_name", "department"])
        if not self.instructors:
            self.instructors = frappe.get_all("Instructor", fields=["name", "instructor_name", "department"])
        
        for inst in self.instructors:
            inst["available_slots"] = None
    
    def _load_time_slots(self):
        self.time_slots = frappe.get_all("Time Slot", filters={"is_active": 1},
            fields=["name", "start_time", "end_time", "duration_minutes", "slot_type"],
            order_by="start_time")
        
        for s in self.time_slots:
            s["duration_minutes"] = safe_int(s.get("duration_minutes"), 60)
        
        self.regular_slots = [s for s in self.time_slots if s.get("slot_type") == "Regular"]
        self.lab_slots = [s for s in self.time_slots if "Lab" in (s.get("slot_type") or "")]
        
        if not self.regular_slots:
            self.regular_slots = self.time_slots
        if not self.lab_slots:
            self.lab_slots = self.regular_slots
    
    def _load_reserved_times(self):
        try:
            reserved = frappe.get_all("University Reserved Time",
                filters={"is_active": 1, "is_recurring": 1},
                fields=["start_time", "end_time", "monday", "tuesday", "wednesday", "thursday", "friday"])
            for r in reserved:
                for day in self.days:
                    if r.get(day.lower()):
                        self.reserved_times.append({"day": day, "start": r.start_time, "end": r.end_time})
        except:
            pass
    
    def _time_mins(self, t):
        if t is None:
            return 0
        if isinstance(t, timedelta):
            return int(t.total_seconds() / 60)
        if isinstance(t, str):
            try:
                p = t.split(":")
                return int(p[0]) * 60 + int(p[1])
            except:
                return 0
        return 0
    
    def _is_reserved(self, day, slot_name):
        slot = next((s for s in self.time_slots if s.name == slot_name), None)
        if not slot:
            return False
        ss, se = self._time_mins(slot.get("start_time")), self._time_mins(slot.get("end_time"))
        for r in self.reserved_times:
            if r["day"] == day:
                rs, re = self._time_mins(r.get("start")), self._time_mins(r.get("end"))
                if ss < re and se > rs:
                    return True
        return False
    
    def _room_free(self, room, day, slot):
        return (day, slot) not in self.room_schedule[room["name"]]
    
    def _instr_free(self, instr, day, slot):
        if (day, slot) in self.instructor_schedule[instr["name"]]:
            return False
        if instr.get("available_slots") is not None:
            return (day, slot) in instr["available_slots"]
        return True
    
    def _get_rooms(self, course, students=30):
        students = safe_int(students, 30)
        if course.get("is_lab_course") and self.labs:
            ok = [r for r in self.labs if r["seating_capacity"] >= students]
            return ok if ok else self.labs[:5]
        ok = [r for r in self.rooms if r["seating_capacity"] >= students]
        return ok if ok else self.rooms[:10]
    
    def _get_instructors(self, course):
        if course.get("preferred_instructor"):
            p = next((i for i in self.instructors if i.name == course["preferred_instructor"]), None)
            if p:
                return [p]
        if course.get("department"):
            di = [i for i in self.instructors if i.get("department") == course["department"]]
            if di:
                return di
        return self.instructors
    
    def _get_slots(self, course):
        return self.lab_slots if course.get("is_lab_course") else self.regular_slots
    
    def _sessions(self, course):
        h = safe_int(course.get("contact_hours") or course.get("credit_hours"), 3)
        return min(max(h, 1), 3)
    
    def _schedule(self, course):
        sessions = self._sessions(course)
        sections = safe_int(course.get("sections"), 1)
        rooms = self._get_rooms(course)
        instructors = self._get_instructors(course)
        slots = self._get_slots(course)
        
        if not rooms or not instructors or not slots:
            self.unscheduled_courses.append({"course": course.get("course_code") or course["name"], "reason": "No resources"})
            return False
        
        scheduled = 0
        days_used = []
        days = self.days.copy()
        random.shuffle(days)
        
        for _ in range(sections):
            sec_done = 0
            for day in days:
                if sec_done >= sessions:
                    break
                if day in days_used and sessions <= 5:
                    continue
                for slot in slots:
                    if sec_done >= sessions:
                        break
                    if self._is_reserved(day, slot.name):
                        continue
                    for room in rooms:
                        if not self._room_free(room, day, slot.name):
                            continue
                        for instr in instructors:
                            if not self._instr_free(instr, day, slot.name):
                                continue
                            
                            self.scheduled_entries.append({
                                "course": course["name"],
                                "course_code": course.get("course_code", ""),
                                "day": day,
                                "time_slot": slot.name,
                                "start_time": slot.get("start_time"),
                                "end_time": slot.get("end_time"),
                                "duration_minutes": safe_int(slot.get("duration_minutes"), 60),
                                "room": room["name"],
                                "instructor": instr["name"],
                                "class_type": "Lab" if course.get("is_lab_course") else "Lecture",
                                "is_lab_session": 1 if course.get("is_lab_course") else 0
                            })
                            
                            self.room_schedule[room["name"]].append((day, slot.name))
                            self.instructor_schedule[instr["name"]].append((day, slot.name))
                            self.course_schedule[course["name"]].append((day, slot.name))
                            
                            sec_done += 1
                            scheduled += 1
                            days_used.append(day)
                            break
                        else:
                            continue
                        break
        
        needed = sessions * sections
        if scheduled < needed:
            self.unscheduled_courses.append({
                "course": course.get("course_code") or course["name"],
                "reason": f"{scheduled}/{needed} scheduled"
            })
            return False
        return True
    
    def run(self, max_iter=3):
        self._progress(0, "Starting...")
        self.load_resources()
        
        if not self.courses:
            return {"success": False, "message": "No courses", "entries": [], "unscheduled": [], "stats": self.stats}
        if not self.rooms:
            return {"success": False, "message": "No rooms", "entries": [], "unscheduled": [], "stats": self.stats}
        if not self.instructors:
            return {"success": False, "message": "No instructors", "entries": [], "unscheduled": [], "stats": self.stats}
        if not self.time_slots:
            return {"success": False, "message": "No time slots", "entries": [], "unscheduled": [], "stats": self.stats}
        
        self._progress(45, "Scheduling...")
        self.courses.sort(key=lambda c: (-1 if c.get("is_lab_course") else 0, safe_int(c.get("credit_hours"), 3)), reverse=True)
        
        for it in range(max_iter):
            self.stats["iterations"] = it + 1
            for i, course in enumerate(self.courses):
                existing = len(self.course_schedule.get(course["name"], []))
                needed = self._sessions(course) * safe_int(course.get("sections"), 1)
                if existing >= needed:
                    continue
                self._schedule(course)
                self._progress(45 + int((i / len(self.courses)) * 50), f"Scheduling {course.get('course_code', course['name'])}")
        
        self._progress(95, "Done")
        self.stats["scheduled"] = len(self.scheduled_entries)
        self.stats["unscheduled"] = len(self.unscheduled_courses)
        
        return {"success": True, "message": f"{len(self.scheduled_entries)} entries", "entries": self.scheduled_entries,
                "unscheduled": self.unscheduled_courses, "stats": self.stats}
    
    def save(self):
        if not self.scheduled_entries:
            return {"success": False, "message": "Nothing to save"}
        
        # Get dates - use term dates or defaults
        effective_from = self.term_start or today()
        effective_to = self.term_end or add_months(today(), 4)
        
        # Create timetable with all required fields
        tt_data = {
            "doctype": "Timetable",
            "title": f"Auto - {self.academic_term}",
            "academic_term": self.academic_term,
            "academic_year": self.academic_year,
            "effective_from": effective_from,
            "effective_to": effective_to,
            "timetable_for": self.timetable_for,
            "status": "Draft",
            "generation_method": "Auto-Scheduled"
        }
        
        # Add optional fields if set
        if self.school:
            tt_data["school"] = self.school
        if self.department:
            tt_data["department"] = self.department
        if self.program:
            tt_data["program"] = self.program
        
        tt = frappe.get_doc(tt_data)
        tt.insert(ignore_permissions=True)
        
        created = 0
        errors = []
        for e in self.scheduled_entries:
            try:
                frappe.get_doc({
                    "doctype": "Timetable Entry",
                    "timetable": tt.name,
                    "academic_term": self.academic_term,
                    "course": e["course"],
                    "day": e["day"],
                    "time_slot": e["time_slot"],
                    "start_time": e.get("start_time"),
                    "end_time": e.get("end_time"),
                    "duration_minutes": e.get("duration_minutes", 60),
                    "room": e["room"],
                    "instructor": e["instructor"],
                    "class_type": e.get("class_type", "Lecture"),
                    "is_lab_session": e.get("is_lab_session", 0),
                    "status": "Draft",
                    "is_recurring": 1
                }).insert(ignore_permissions=True)
                created += 1
            except Exception as ex:
                errors.append(str(ex))
        
        frappe.db.commit()
        return {"success": True, "timetable": tt.name, "created": created, "errors": errors}


@frappe.whitelist()
def auto_schedule(academic_term, timetable_for="Entire University", school=None, department=None, program=None, save=True):
    frappe.only_for(["System Manager", "Education Manager", "Academics User"])
    s = TimetableScheduler(academic_term, timetable_for, school, department, program)
    result = s.run()
    if save and result["success"] and result.get("entries"):
        result["save_result"] = s.save()
    frappe.publish_realtime("scheduler_progress", {"progress": 100, "message": "Complete!", "result": result})
    return result


@frappe.whitelist()
def preview_schedule(academic_term, timetable_for="Entire University", school=None, department=None, program=None):
    return auto_schedule(academic_term, timetable_for, school, department, program, save=False)
