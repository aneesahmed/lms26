"""Shared constants and lookup helpers for the Student Panel seed scripts.

Each seeders/*.py module owns one area (people, calendar, courses, sessions,
assessments, notifications) and is independently runnable - if only, say,
the assessment data needs to change, run `python -m seeders.assessments`
without touching or re-running anything else. Modules that depend on
another area's data (e.g. assessments needs CourseSections to exist) look
that data up themselves via the getters below rather than requiring it to
be passed in, so run order only matters the first time a fresh DB is
seeded (see seed_student_panel.py), not on every subsequent targeted rerun.
"""
from datetime import date

from sqlalchemy import text
from sqlalchemy.future import select

from app.database import AsyncSessionLocal, engine
from app.models.org import Org
from app.models.identity import Person, RoleAssignment
from app.models.admission import AdmissionApplication  # noqa: F401 - completes Base.metadata
from app.models.asset import Asset  # noqa: F401 - registers "asset" table for academic.py's FKs
from app.models.staff import JobApplication  # noqa: F401 - completes Base.metadata
from app.models.academic import (
    Term, Course, SubjectRequirementTemplate, SectionPlan,  # noqa: F401 - completes Base.metadata
    ResourcePlanRun, ResourcePlanAssignment, ResourceGap,  # noqa: F401
    SchoolClass, ClassEnrollment, CourseSection, Topic, CalendarDay,
    ClassSession, ClassSessionLog, AttendanceRecord, Assessment, Score,
)
from app.models.notification import Notification  # noqa: F401 - completes Base.metadata
from app.services.auth import hash_password

DEV_PASSWORD = "Passw0rd!"

ORG_NAME = "Brainiacs Main Campus"
TERM_NAME = "Fall 2026"
TERM_START = date(2026, 8, 11)
TERM_END = date(2026, 12, 15)

CLASS_GRADE_NAME = "Class 1"
CLASS_SECTION_LABEL = "A"

STUDENT_FIRST_NAME = "Danyal"
STUDENT_LAST_NAME = "Ahmed"
STUDENT_EMAIL = "danyal.ahmed@brainiacs.edu"

TEACHERS = [
    # first, last, email, subject taught (for readability only)
    ("Farhan", "Iqbal", "farhan.iqbal@brainiacs.edu", "Mathematics"),
    ("Abdul", "Rehman", "abdul.rehman@brainiacs.edu", "Islamiyat"),
    ("Sara", "Bukhari", "sara.bukhari@brainiacs.edu", "Social Studies"),
    ("Omar", "Sheikh", "omar.sheikh@brainiacs.edu", "Science"),
    ("Ayesha", "Malik", "ayesha.malik@brainiacs.edu", "Urdu"),
    ("Hamza", "Tariq", "hamza.tariq@brainiacs.edu", "English"),
]

SUBJECT_COURSES = [
    # name, code, teacher_email
    ("Mathematics", "MTH-1A", "farhan.iqbal@brainiacs.edu"),
    ("Islamiyat", "ISL-1A", "abdul.rehman@brainiacs.edu"),
    ("Social Studies", "SST-1A", "sara.bukhari@brainiacs.edu"),
    ("Science", "SCI-1A", "omar.sheikh@brainiacs.edu"),
    ("Urdu", "URD-1A", "ayesha.malik@brainiacs.edu"),
    ("English", "ENG-1A", "hamza.tariq@brainiacs.edu"),
]


async def ensure_tables():
    """Schema is managed by Alembic migrations now, not create_all - this
    just checks migrations have actually been applied, so a forgotten
    `alembic upgrade head` fails with a clear message instead of a
    confusing "table does not exist" error deep in a seeder."""
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT to_regclass('public.alembic_version')"))
        if result.scalar() is None:
            raise RuntimeError(
                "Database has no Alembic migration history. Run `alembic upgrade head` first."
            )


async def get_or_create_person(db, first_name, last_name, email, role, org_id, password=DEV_PASSWORD):
    person = (await db.execute(select(Person).where(Person.email == email))).scalars().first()
    if not person:
        person = Person(first_name=first_name, last_name=last_name, email=email)
        db.add(person)
        await db.commit()
        await db.refresh(person)
    if not person.password_hash:
        person.password_hash = hash_password(password)
        await db.commit()

    existing_role = (
        await db.execute(select(RoleAssignment).where(RoleAssignment.person_id == person.id, RoleAssignment.role == role))
    ).scalars().first()
    if not existing_role:
        db.add(RoleAssignment(person_id=person.id, org_id=org_id, role=role))
        await db.commit()

    return person


async def get_org(db) -> Org:
    org = (await db.execute(select(Org).where(Org.type == "SCHOOL"))).scalars().first()
    if not org:
        raise RuntimeError("No SCHOOL Org found - run `python -m seeders.people` first")
    return org


async def get_term(db, org_id: int) -> Term:
    term = (await db.execute(select(Term).where(Term.name == TERM_NAME, Term.org_id == org_id))).scalars().first()
    if not term:
        raise RuntimeError("No term found - run `python -m seeders.people` first")
    return term


async def get_school_class(db, term_id: int) -> SchoolClass:
    school_class = (
        await db.execute(
            select(SchoolClass).where(
                SchoolClass.grade_name == CLASS_GRADE_NAME,
                SchoolClass.section_label == CLASS_SECTION_LABEL,
                SchoolClass.term_id == term_id,
            )
        )
    ).scalars().first()
    if not school_class:
        raise RuntimeError("No SchoolClass found - run `python -m seeders.people` first")
    return school_class


async def get_student(db) -> Person:
    student = (await db.execute(select(Person).where(Person.email == STUDENT_EMAIL))).scalars().first()
    if not student:
        raise RuntimeError("No student found - run `python -m seeders.people` first")
    return student


async def get_course_sections(db, school_class_id: int) -> list[tuple[CourseSection, str]]:
    """Returns [(CourseSection, subject_name), ...] for the demo class, in
    SUBJECT_COURSES order. Raises if courses/sections haven't been seeded yet."""
    result = []
    for name, code, _teacher_email in SUBJECT_COURSES:
        course = (await db.execute(select(Course).where(Course.code == code))).scalars().first()
        if not course:
            raise RuntimeError(f"Course {code} not found - run `python -m seeders.courses` first")
        cs = (
            await db.execute(
                select(CourseSection).where(CourseSection.course_id == course.id, CourseSection.school_class_id == school_class_id)
            )
        ).scalars().first()
        if not cs:
            raise RuntimeError(f"CourseSection for {code} not found - run `python -m seeders.courses` first")
        result.append((cs, name))
    return result
