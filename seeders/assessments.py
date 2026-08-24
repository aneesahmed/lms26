"""Seeds Assessments (quizzes/assignments/exams) and the demo student's
Scores, and links each past assessment to the ClassSession nearest its due
date (so "was a quiz given today" is answerable from ClassSession alone).
Depends on seeders.people, seeders.courses, and seeders.sessions.

Run directly: python -m seeders.assessments
"""
import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.academic import ClassSession, Assessment, Score
from seeders.common import ensure_tables, get_org, get_term, get_school_class, get_student, get_course_sections


def build_assessment_plan(term_start: date, today: date):
    def past(n: int) -> date:
        """n days before today, clamped so it never falls before the term
        actually started."""
        return max(term_start, today - timedelta(days=n))

    return {
        "Mathematics": [
            ("Counting Quiz", "QUIZ", 10, past(9), "GRADED", 9),
            ("Addition Worksheet", "ASSIGNMENT", 10, past(5), "GRADED", 8),
            ("Subtraction Worksheet", "ASSIGNMENT", 10, today + timedelta(days=1), "PENDING", None),
            ("Shapes Quiz", "QUIZ", 10, today + timedelta(days=3), "PENDING", None),
            ("Term Test", "EXAM", 50, today + timedelta(days=22), "PENDING", None),
        ],
        "Islamiyat": [
            ("Kalima Recitation Test", "QUIZ", 10, past(8), "GRADED", 10),
            ("Surah Memorization", "ASSIGNMENT", 10, past(2), "GRADED", 9),
            ("Wudu Steps Worksheet", "ASSIGNMENT", 10, past(1), "OVERDUE", None),
            ("Manners Quiz", "QUIZ", 10, today, "PENDING", None),
            ("Surah Yaseen Practice", "ASSIGNMENT", 10, today + timedelta(days=1), "PENDING", None),
        ],
        "Social Studies": [
            ("My Family Worksheet", "ASSIGNMENT", 10, past(4), "GRADED", 9),
            ("Community Helpers Project", "PROJECT", 20, today + timedelta(days=2), "PENDING", None),
            ("My School Quiz", "QUIZ", 10, today + timedelta(days=5), "PENDING", None),
        ],
        "Science": [
            ("Living Things Quiz", "QUIZ", 10, past(7), "GRADED", 7),
            ("Plant Parts Worksheet", "ASSIGNMENT", 10, today, "OVERDUE", None),
            ("Five Senses Activity", "ASSIGNMENT", 10, today + timedelta(days=4), "PENDING", None),
            ("Term Test", "EXAM", 50, today + timedelta(days=15), "PENDING", None),
        ],
        "Urdu": [
            ("Huroof-e-Tahaji Test", "QUIZ", 10, past(6), "GRADED", 9),
            ("Word Writing Practice", "ASSIGNMENT", 10, today + timedelta(days=6), "PENDING", None),
        ],
        "English": [
            ("Alphabet Test", "QUIZ", 10, past(3), "GRADED", 10),
            ("Phonics Worksheet", "ASSIGNMENT", 10, today + timedelta(days=8), "PENDING", None),
        ],
    }


async def nearest_session_id(db, course_section_id: int, target_date: date):
    sessions = (
        await db.execute(select(ClassSession).where(ClassSession.course_section_id == course_section_id))
    ).scalars().all()
    past_or_same = [s for s in sessions if s.date <= target_date]
    if not past_or_same:
        return None
    return max(past_or_same, key=lambda s: s.date).id


async def seed_assessments():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        org = await get_org(db)
        term = await get_term(db, org.id)
        school_class = await get_school_class(db, term.id)
        student = await get_student(db)
        course_sections = await get_course_sections(db, school_class.id)

        today = date.today()
        assessment_plan = build_assessment_plan(term.start_date, today)

        print("Seeding assessments and scores...")
        for cs, subject_name in course_sections:
            existing = (
                await db.execute(select(Assessment).where(Assessment.course_section_id == cs.id))
            ).scalars().first()
            if existing:
                continue

            for title, a_type, max_score, due_date, status, marks in assessment_plan.get(subject_name, []):
                session_id = await nearest_session_id(db, cs.id, due_date) if due_date <= today else None
                assessment = Assessment(
                    course_section_id=cs.id, title=title, type=a_type,
                    max_score=max_score, weight=1.0, due_date=due_date,
                    assigned_class_session_id=session_id,
                )
                db.add(assessment)
                await db.commit()
                await db.refresh(assessment)
                if status != "PENDING" or marks is not None:
                    db.add(Score(
                        assessment_id=assessment.id, student_id=student.id,
                        marks_obtained=marks, status=status,
                        recorded_at=datetime.utcnow() if status == "GRADED" else None,
                    ))
            await db.commit()
            print(f"  {subject_name}: {len(assessment_plan.get(subject_name, []))} assessment(s)")

        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_assessments())
