"""Seeds a few demo Notifications for the student's bell dropdown. Depends
on seeders.people and seeders.courses.

Run directly: python -m seeders.notifications
"""
import asyncio

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.notification import Notification
from seeders.common import ensure_tables, get_org, get_term, get_school_class, get_student, get_course_sections


async def seed_notifications():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        org = await get_org(db)
        term = await get_term(db, org.id)
        school_class = await get_school_class(db, term.id)
        student = await get_student(db)
        course_sections = await get_course_sections(db, school_class.id)
        by_name = {name: cs for cs, name in course_sections}

        existing = (await db.execute(select(Notification).where(Notification.person_id == student.id))).scalars().first()
        if existing:
            print("Notifications already seeded, skipping.")
            return

        print("Seeding notifications...")
        db.add_all([
            Notification(
                person_id=student.id, type="GRADE_POSTED", title="New grade posted",
                body="Islamiyat - Surah Memorization: 9/10",
                related_course_section_id=by_name["Islamiyat"].id,
            ),
            Notification(
                person_id=student.id, type="ABSENCE", title="Absence recorded",
                body="You were marked absent for Science",
                related_course_section_id=by_name["Science"].id,
            ),
            Notification(
                person_id=student.id, type="DEADLINE", title="Deadline approaching",
                body="Social Studies - Community Helpers Project due in 2 days",
                related_course_section_id=by_name["Social Studies"].id,
            ),
        ])
        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_notifications())
