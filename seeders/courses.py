"""Seeds Courses, CourseSections (subject taught to the demo class), and
their Topic (syllabus) lists. Depends on seeders.people having run.

Run directly: python -m seeders.courses
"""
import asyncio

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.identity import Person
from app.models.academic import Course, CourseSection, Topic
from seeders.common import ensure_tables, get_org, get_term, get_school_class, SUBJECT_COURSES

# name -> topic list (name, is_covered), age-appropriate for Class 1
TOPICS_BY_SUBJECT = {
    "Mathematics": [
        ("Counting 1-100", True), ("Addition up to 20", True),
        ("Subtraction up to 20", True), ("Shapes & Patterns", False),
        ("Simple Word Problems", False),
    ],
    "Islamiyat": [
        ("Kalima Tayyabah", True), ("Short Surahs", True),
        ("Wudu Steps", False), ("Good Manners (Akhlaq)", False),
    ],
    "Social Studies": [
        ("My Family", True), ("My School", True),
        ("Community Helpers", False), ("My Country Pakistan", False),
    ],
    "Science": [
        ("Living & Non-Living Things", True), ("Parts of a Plant", True),
        ("Our Five Senses", False), ("Animals & Their Homes", False),
    ],
    "Urdu": [
        ("Urdu Alphabets (Alif-Bay)", True), ("Simple Words", True),
        ("Reading Short Sentences", False), ("Poem Recitation", False),
    ],
    "English": [
        ("English Alphabets", True), ("Phonics Sounds", True),
        ("Simple Sentences", False), ("Rhymes & Stories", False),
    ],
}


async def seed_courses():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        org = await get_org(db)
        term = await get_term(db, org.id)
        school_class = await get_school_class(db, term.id)

        print(f"Seeding courses/sections for {school_class.grade_name} - {school_class.section_label}...")
        for name, code, teacher_email in SUBJECT_COURSES:
            course = (await db.execute(select(Course).where(Course.code == code))).scalars().first()
            if not course:
                course = Course(name=name, code=code, grade_level=school_class.grade_name)
                db.add(course)
                await db.commit()
                await db.refresh(course)

            cs = (
                await db.execute(
                    select(CourseSection).where(CourseSection.course_id == course.id, CourseSection.school_class_id == school_class.id)
                )
            ).scalars().first()
            if cs:
                continue

            teacher = (await db.execute(select(Person).where(Person.email == teacher_email))).scalars().first()
            if not teacher:
                raise RuntimeError(f"Teacher {teacher_email} not found - run `python -m seeders.people` first")

            cs = CourseSection(
                name="Section A", course_id=course.id, school_class_id=school_class.id,
                term_id=term.id, teacher_id=teacher.id, capacity=30,
            )
            db.add(cs)
            await db.commit()
            await db.refresh(cs)

            for i, (topic_name, is_covered) in enumerate(TOPICS_BY_SUBJECT.get(name, [])):
                db.add(Topic(course_section_id=cs.id, name=topic_name, is_covered=is_covered, sort_order=i))
            await db.commit()
            print(f"  {name} ({code}) -> {teacher.first_name} {teacher.last_name}")

        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_courses())
