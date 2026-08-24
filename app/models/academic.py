from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Boolean, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Base structures
class Term(Base):
    __tablename__ = "term"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) 
    start_date = Column(Date)
    end_date = Column(Date)
    org_id = Column(Integer, ForeignKey("org.id"))

class Course(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    grade_level = Column(String) 
    facility_type_needed = Column(String, default="REGULAR")

# Part A: Resource Planning
class SubjectRequirementTemplate(Base):
    __tablename__ = "subject_req_template"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"))
    version = Column(String, default="v1")
    role_needed = Column(String) # SUBJECT_TEACHER | LAB_INCHARGE | TA | SUPPORT_STAFF
    count_per_section = Column(Integer, default=1)
    allocation_mode_hint = Column(String, default="DEDICATED") # DEDICATED | SHARED
    room_type_needed = Column(String) # Defaults to Course.facility_type_needed
    equipment_needed = Column(JSON, nullable=True) # e.g., ["PROJECTOR", "MICROSCOPE"]
    periods_per_week = Column(Integer, default=5)

class SectionPlan(Base):
    __tablename__ = "section_plan"
    id = Column(Integer, primary_key=True, index=True)
    grade_level = Column(String) # e.g. "Grade 9"
    term_id = Column(Integer, ForeignKey("term.id"))
    estimated_enrollment = Column(Integer)
    max_section_size = Column(Integer, default=30)
    computed_section_count = Column(Integer)
    status = Column(String, default="DRAFT") # DRAFT | LOCKED

class ResourcePlanRun(Base):
    __tablename__ = "resource_plan_run"
    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, ForeignKey("term.id"))
    grade_level = Column(String)
    status = Column(String, default="DRAFT") # DRAFT | SIMULATED | PUBLISHED

class ResourcePlanAssignment(Base):
    __tablename__ = "resource_plan_assignment"
    id = Column(Integer, primary_key=True, index=True)
    plan_run_id = Column(Integer, ForeignKey("resource_plan_run.id"))
    target_type = Column(String) # CLASS | COURSE_OFFERING | PROGRAM
    target_id = Column(String) # e.g. "Section A"
    course_id = Column(Integer, ForeignKey("course.id"), nullable=True)
    role = Column(String) # CLASS_TEACHER | SUBJECT_TEACHER | TA ...
    resource_id = Column(Integer, ForeignKey("person.id"), nullable=True) # The teacher/staff
    room_resource_id = Column(Integer, ForeignKey("asset.id"), nullable=True) # The room
    equipment_resource_ids = Column(JSON, nullable=True)
    status = Column(String, default="PROPOSED") # PROPOSED | CONFIRMED | GAP

class ResourceGap(Base):
    __tablename__ = "resource_gap"
    id = Column(Integer, primary_key=True, index=True)
    plan_run_id = Column(Integer, ForeignKey("resource_plan_run.id"))
    role_needed = Column(String, nullable=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=True)
    count_short = Column(Integer)
    room_type_needed = Column(String, nullable=True)
    status = Column(String, default="OPEN") # OPEN | HIRING_INITIATED | PROCUREMENT_INITIATED | RESOLVED

# Part B: Classes, Enrollment, Schedule, Attendance, Assessment

class SchoolClass(Base):
    """A homeroom cohort, e.g. 'Grade 9 - A'."""
    __tablename__ = "school_class"
    id = Column(Integer, primary_key=True, index=True)
    grade_name = Column(String)  # e.g. "Grade 9"
    section_label = Column(String)  # e.g. "A"
    term_id = Column(Integer, ForeignKey("term.id"))
    org_id = Column(Integer, ForeignKey("org.id"))
    homeroom_teacher_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    # RESTRICTED: student takes every subject tied to their class/section (only mode implemented).
    # ELECTIVE: reserved for a future per-course enrollment flow.
    enrollment_mode = Column(String, default="RESTRICTED")

class ClassEnrollment(Base):
    """Admin-assigned: a student joining a SchoolClass. In RESTRICTED mode this
    single row is what grants the student every CourseSection under that class."""
    __tablename__ = "class_enrollment"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("person.id"))
    school_class_id = Column(Integer, ForeignKey("school_class.id"))
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

class CourseSection(Base):
    """One subject taught to one class/section - carries its own teacher,
    room and schedule, independent of any other section of the same Course."""
    __tablename__ = "course_section"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # e.g. "Section A"
    course_id = Column(Integer, ForeignKey("course.id"))
    school_class_id = Column(Integer, ForeignKey("school_class.id"), nullable=True)
    term_id = Column(Integer, ForeignKey("term.id"))
    teacher_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    classroom_id = Column(Integer, ForeignKey("asset.id"), nullable=True)
    capacity = Column(Integer, nullable=True)

class Topic(Base):
    """A syllabus item for a CourseSection - backs the student dashboard's
    'Content' tab. is_covered is a cached convenience flag; covered_in_session_id
    (set once a ClassSessionLog marks it taught) records exactly which class
    day covered it, which is what course-pacing/coverage tracking reads."""
    __tablename__ = "topic"
    id = Column(Integer, primary_key=True, index=True)
    course_section_id = Column(Integer, ForeignKey("course_section.id"))
    name = Column(String)
    is_covered = Column(Boolean, default=False)
    covered_in_session_id = Column(Integer, ForeignKey("class_session.id"), nullable=True)
    sort_order = Column(Integer, default=0)

class CalendarDay(Base):
    """Marks a single date as a school day or a holiday for an Org, so
    ClassSession generation and attendance tracking know which days are
    real class days. Regional public holidays can be bulk-loaded from an
    external calendar feed (see app/services/calendar_sync.py); source
    distinguishes those from manually-entered days (e.g. an admin-declared
    closure)."""
    __tablename__ = "calendar_day"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("org.id"))
    date = Column(Date, index=True)
    day_type = Column(String)  # SCHOOL_DAY | HOLIDAY | WEEKEND
    label = Column(String, nullable=True)  # e.g. "Independence Day"
    source = Column(String, default="MANUAL")  # MANUAL | GOOGLE_SYNC

class ClassSession(Base):
    """A concrete scheduled meeting of a CourseSection."""
    __tablename__ = "class_session"
    id = Column(Integer, primary_key=True, index=True)
    course_section_id = Column(Integer, ForeignKey("course_section.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)

class AttendanceRecord(Base):
    """One record per session, per student."""
    __tablename__ = "attendance_record"
    id = Column(Integer, primary_key=True, index=True)
    class_session_id = Column(Integer, ForeignKey("class_session.id"))
    student_id = Column(Integer, ForeignKey("person.id"))
    status = Column(String)  # PRESENT | ABSENT | LATE | EXCUSED | HALF_DAY | REMOTE
    recorded_by = Column(Integer, ForeignKey("person.id"), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class ClassSessionLog(Base):
    """What actually happened in one ClassSession - the daily activity log a
    teacher fills in: what was taught, classwork done, homework/house work
    assigned, and free-form notes. One row per ClassSession (1:1). This is
    the record that individual student performance (via linked Assessment/
    Score) and overall course-pacing (via Topic.covered_in_session_id) both
    read from."""
    __tablename__ = "class_session_log"
    id = Column(Integer, primary_key=True, index=True)
    class_session_id = Column(Integer, ForeignKey("class_session.id"), unique=True)
    classwork = Column(String, nullable=True)  # what was done in class
    homework = Column(String, nullable=True)  # house work assigned, free-text summary
    notes = Column(String, nullable=True)
    recorded_by = Column(Integer, ForeignKey("person.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Assessment(Base):
    """A quiz/assignment/project/exam definition for a CourseSection.
    assigned_class_session_id (nullable - not every assessment is tied to a
    specific day, e.g. a term exam) links it to the ClassSession it was
    handed out or administered in, so "was a quiz taken today" and "what
    homework came out of today's class" are both just a query on that FK."""
    __tablename__ = "assessment"
    id = Column(Integer, primary_key=True, index=True)
    course_section_id = Column(Integer, ForeignKey("course_section.id"))
    assigned_class_session_id = Column(Integer, ForeignKey("class_session.id"), nullable=True)
    title = Column(String)
    type = Column(String)  # ASSIGNMENT | QUIZ | PROJECT | PARTICIPATION | EXAM
    max_score = Column(Integer, default=100)
    weight = Column(Float, default=1.0)
    due_date = Column(Date, nullable=True)

class Score(Base):
    """A student's result on an Assessment."""
    __tablename__ = "score"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessment.id"))
    student_id = Column(Integer, ForeignKey("person.id"))
    marks_obtained = Column(Integer, nullable=True)
    status = Column(String, default="PENDING")  # PENDING | SUBMITTED | GRADED | OVERDUE
    recorded_at = Column(DateTime(timezone=True), nullable=True)
