"""Seeds the Org, Term, Admin, Teachers, SchoolClass, and Student
+ enrollment. Everything else (courses, calendar, sessions, assessments,
notifications) looks these up rather than creating its own - this is the
one module that must run first against a fresh database.

Run directly: python -m seeders.people
"""
import asyncio

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.org import Org
from app.models.academic import Term, SchoolClass, ClassEnrollment
from seeders.common import (
    ensure_tables, get_or_create_person, DEV_PASSWORD,
    ORG_NAME, TERM_NAME, TERM_START, TERM_END,
    CLASS_GRADE_NAME, CLASS_SECTION_LABEL,
    STUDENT_FIRST_NAME, STUDENT_LAST_NAME, STUDENT_EMAIL, TEACHERS,
)


async def seed_people():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        print("Seeding org, term, admin, teachers, class, and student...")

        org = (await db.execute(select(Org).where(Org.type == "SCHOOL"))).scalars().first()
        if not org:
            org = Org(type="SCHOOL", name=ORG_NAME)
            db.add(org)
            await db.commit()
            await db.refresh(org)

        term = (await db.execute(select(Term).where(Term.name == TERM_NAME, Term.org_id == org.id))).scalars().first()
        if not term:
            term = Term(name=TERM_NAME, start_date=TERM_START, end_date=TERM_END, org_id=org.id)
            db.add(term)
            await db.commit()
            await db.refresh(term)
        elif term.start_date != TERM_START or term.end_date != TERM_END:
            term.start_date = TERM_START
            term.end_date = TERM_END
            await db.commit()

        await get_or_create_person(db, "Alice", "Admin", "admin@brainiacs.edu", "ADMIN", org.id)

        teacher_persons = {}
        for first, last, email, _subject in TEACHERS:
            teacher_persons[email] = await get_or_create_person(db, first, last, email, "TEACHER", org.id)

        school_class = (
            await db.execute(
                select(SchoolClass).where(
                    SchoolClass.grade_name == CLASS_GRADE_NAME,
                    SchoolClass.section_label == CLASS_SECTION_LABEL,
                    SchoolClass.term_id == term.id,
                )
            )
        ).scalars().first()
        if not school_class:
            homeroom_teacher = teacher_persons[TEACHERS[0][2]]
            school_class = SchoolClass(
                grade_name=CLASS_GRADE_NAME, section_label=CLASS_SECTION_LABEL, term_id=term.id, org_id=org.id,
                homeroom_teacher_id=homeroom_teacher.id, enrollment_mode="RESTRICTED",
            )
            db.add(school_class)
            await db.commit()
            await db.refresh(school_class)

        student = await get_or_create_person(db, STUDENT_FIRST_NAME, STUDENT_LAST_NAME, STUDENT_EMAIL, "STUDENT", org.id)
        enrollment = (
            await db.execute(select(ClassEnrollment).where(ClassEnrollment.student_id == student.id))
        ).scalars().first()
        if not enrollment:
            db.add(ClassEnrollment(student_id=student.id, school_class_id=school_class.id))
            await db.commit()

        print(f"  Org: {org.name} (id={org.id})")
        print(f"  Term: {term.name} {term.start_date} - {term.end_date}")
        print(f"  Class: {school_class.grade_name} - {school_class.section_label}")
        print(f"  Student: {student.first_name} {student.last_name} <{student.email}> / {DEV_PASSWORD}")
        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_people())
