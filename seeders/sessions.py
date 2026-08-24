"""Seeds ClassSessions for every real school day of the term so far (skips
weekends and CalendarDay holidays), AttendanceRecords for the demo student,
and ClassSessionLog rows (daily classwork/homework) that also mark which
Topic each session covered. Depends on seeders.people, seeders.calendar,
and seeders.courses having run.

Run directly: python -m seeders.sessions
"""
import asyncio
from datetime import date, time, timedelta

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models.academic import CalendarDay, Topic, ClassSession, ClassSessionLog, AttendanceRecord
from seeders.common import ensure_tables, get_org, get_term, get_school_class, get_student, get_course_sections

# A few deterministic absences/lates per subject so attendance isn't a flat
# 100% - indices are safe regardless of exactly how many school days have
# elapsed so far this term.
ABSENCE_PATTERN = {
    "Mathematics": {4: "LATE"},
    "Islamiyat": {2: "ABSENT", 6: "LATE"},
    "Social Studies": {},
    "Science": {1: "ABSENT", 5: "ABSENT"},
    "Urdu": {},
    "English": {8: "LATE"},
}

HOMEWORK_TEMPLATES = {
    "Mathematics": "Practice worksheet: today's counting/addition exercises",
    "Islamiyat": "Revise today's surah/dua at home with a parent",
    "Social Studies": "Draw a picture about today's topic",
    "Science": "Observe and note one example of today's topic at home",
    "Urdu": "Write today's words 3 times each",
    "English": "Read today's phonics sounds aloud at home",
}


def attendance_status(subject_name: str, day_index: int) -> str:
    return ABSENCE_PATTERN.get(subject_name, {}).get(day_index, "PRESENT")


async def compute_school_days(db, org_id: int, start: date, end: date) -> tuple[list[date], int]:
    holiday_dates = {
        r.date for r in (
            await db.execute(select(CalendarDay).where(CalendarDay.org_id == org_id, CalendarDay.day_type == "HOLIDAY"))
        ).scalars().all()
    }
    days = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5 and cursor not in holiday_dates:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days, len(holiday_dates)


async def seed_sessions():
    await ensure_tables()

    async with AsyncSessionLocal() as db:
        org = await get_org(db)
        term = await get_term(db, org.id)
        school_class = await get_school_class(db, term.id)
        student = await get_student(db)
        course_sections = await get_course_sections(db, school_class.id)

        today = date.today()
        school_days, holiday_count = await compute_school_days(db, org.id, term.start_date, today)
        print(f"{len(school_days)} school day(s) elapsed so far this term ({holiday_count} holiday(s) excluded)")

        for cs, subject_name in course_sections:
            existing_sessions = (
                await db.execute(select(ClassSession).where(ClassSession.course_section_id == cs.id))
            ).scalars().all()

            if len(existing_sessions) < len(school_days):
                created_sessions = list(existing_sessions)
                for i, session_date in enumerate(school_days[len(existing_sessions):], start=len(existing_sessions)):
                    session = ClassSession(
                        course_section_id=cs.id, date=session_date,
                        start_time=time(9, 0), end_time=time(9, 45),
                    )
                    db.add(session)
                    await db.commit()
                    await db.refresh(session)
                    db.add(AttendanceRecord(
                        class_session_id=session.id, student_id=student.id,
                        status=attendance_status(subject_name, i), recorded_by=cs.teacher_id,
                    ))
                    created_sessions.append(session)
                await db.commit()
                sessions = created_sessions
            else:
                sessions = existing_sessions

            # ClassSessionLog + topic-coverage linking (only if not already done)
            if not sessions:
                continue
            existing_log = (
                await db.execute(select(ClassSessionLog).where(ClassSessionLog.class_session_id == sessions[0].id))
            ).scalars().first()
            if existing_log:
                continue

            covered_topics = (
                await db.execute(
                    select(Topic).where(Topic.course_section_id == cs.id, Topic.is_covered.is_(True)).order_by(Topic.sort_order.asc())
                )
            ).scalars().all()

            for i, session in enumerate(sessions):
                topic_for_day = covered_topics[i] if i < len(covered_topics) else None
                classwork = f"Covered: {topic_for_day.name}" if topic_for_day else "Review and practice activities"
                homework = HOMEWORK_TEMPLATES.get(subject_name) if i % 3 == 2 else None
                db.add(ClassSessionLog(
                    class_session_id=session.id, classwork=classwork, homework=homework, recorded_by=cs.teacher_id,
                ))
                if topic_for_day:
                    topic_for_day.covered_in_session_id = session.id
            await db.commit()
            print(f"  {subject_name}: {len(sessions)} session(s) logged")

        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_sessions())
