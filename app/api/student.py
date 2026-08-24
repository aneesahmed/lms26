from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.academic import (
    Term, SchoolClass, ClassEnrollment, CourseSection, Course, Topic,
    ClassSession, ClassSessionLog, AttendanceRecord, Assessment, Score,
)
from app.models.identity import Person
from app.models.notification import Notification
from app.services.auth import require_role, CurrentPerson

router = APIRouter(prefix="/student", tags=["Student"])

ATTENDANCE_WEIGHTS = {
    "PRESENT": 1.0,
    "LATE": 1.0,
    "REMOTE": 1.0,
    "HALF_DAY": 0.5,
    "ABSENT": 0.0,
}
ASSIGNMENT_TYPES = {"ASSIGNMENT"}


def format_relative_day(d: date, t=None) -> str:
    today = date.today()
    if d == today:
        label = "Today"
    elif d == today + timedelta(days=1):
        label = "Tomorrow"
    elif today < d <= today + timedelta(days=6):
        label = d.strftime("%A")
    else:
        label = d.strftime("%b %d")
    if t:
        return f"{label}, {t.strftime('%I:%M %p').lstrip('0')}"
    return label


async def get_student_school_class(db: AsyncSession, student_id: int) -> SchoolClass:
    enrollment = (
        await db.execute(
            select(ClassEnrollment)
            .where(ClassEnrollment.student_id == student_id)
            .order_by(ClassEnrollment.enrolled_at.desc())
        )
    ).scalars().first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student is not enrolled in a class yet")

    school_class = (
        await db.execute(select(SchoolClass).where(SchoolClass.id == enrollment.school_class_id))
    ).scalars().first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Enrolled class no longer exists")
    return school_class


async def get_class_course_sections(db: AsyncSession, school_class_id: int):
    return (
        await db.execute(select(CourseSection).where(CourseSection.school_class_id == school_class_id))
    ).scalars().all()


async def compute_attendance_pct(db: AsyncSession, course_section_id: int, student_id: int):
    rows = (
        await db.execute(
            select(AttendanceRecord)
            .join(ClassSession, AttendanceRecord.class_session_id == ClassSession.id)
            .where(ClassSession.course_section_id == course_section_id, AttendanceRecord.student_id == student_id)
        )
    ).scalars().all()
    countable = [r for r in rows if r.status != "EXCUSED"]
    if not countable:
        return None
    total_weight = sum(ATTENDANCE_WEIGHTS.get(r.status, 0.0) for r in countable)
    return round(total_weight / len(countable) * 100)


async def compute_progress_pct(db: AsyncSession, course_section_id: int, student_id: int):
    rows = (
        await db.execute(
            select(Score, Assessment)
            .join(Assessment, Score.assessment_id == Assessment.id)
            .where(
                Assessment.course_section_id == course_section_id,
                Score.student_id == student_id,
                Score.status == "GRADED",
                Score.marks_obtained.is_not(None),
            )
        )
    ).all()
    if not rows:
        return None
    total_weight = sum(a.weight for _, a in rows)
    if total_weight == 0:
        return None
    weighted = sum((s.marks_obtained / a.max_score) * a.weight for s, a in rows if a.max_score)
    return round(weighted / total_weight * 100)


async def get_next_class_session(db: AsyncSession, course_section_id: int):
    today = date.today()
    return (
        await db.execute(
            select(ClassSession)
            .where(ClassSession.course_section_id == course_section_id, ClassSession.date >= today)
            .order_by(ClassSession.date.asc(), ClassSession.start_time.asc())
        )
    ).scalars().first()


async def build_subject_summary(db: AsyncSession, cs: CourseSection, student_id: int):
    course = (await db.execute(select(Course).where(Course.id == cs.course_id))).scalars().first()
    teacher = (
        await db.execute(select(Person).where(Person.id == cs.teacher_id))
    ).scalars().first() if cs.teacher_id else None
    next_session = await get_next_class_session(db, cs.id)

    return {
        "course_section_id": cs.id,
        "subject_name": course.name if course else "Unknown Subject",
        "teacher_name": f"{teacher.first_name} {teacher.last_name}" if teacher else "Unassigned",
        "progress_pct": await compute_progress_pct(db, cs.id, student_id),
        "attendance_pct": await compute_attendance_pct(db, cs.id, student_id),
        "next_class": format_relative_day(next_session.date, next_session.start_time) if next_session else None,
    }


async def build_subject_summaries_batch(db: AsyncSession, course_sections: list[CourseSection], student_id: int):
    """Same output as calling build_subject_summary() per section, but as a
    handful of batched queries instead of ~5 per subject - the overview
    endpoint was doing 30+ sequential round trips for a 6-subject class."""
    if not course_sections:
        return []

    section_ids = [cs.id for cs in course_sections]
    course_ids = [cs.course_id for cs in course_sections]
    teacher_ids = [cs.teacher_id for cs in course_sections if cs.teacher_id]

    courses_by_id = {
        c.id: c for c in (await db.execute(select(Course).where(Course.id.in_(course_ids)))).scalars().all()
    }
    teachers_by_id = {
        p.id: p for p in (await db.execute(select(Person).where(Person.id.in_(teacher_ids)))).scalars().all()
    } if teacher_ids else {}

    attendance_by_section: dict[int, list] = {sid: [] for sid in section_ids}
    for record, section_id in (
        await db.execute(
            select(AttendanceRecord, ClassSession.course_section_id)
            .join(ClassSession, AttendanceRecord.class_session_id == ClassSession.id)
            .where(ClassSession.course_section_id.in_(section_ids), AttendanceRecord.student_id == student_id)
        )
    ).all():
        attendance_by_section[section_id].append(record)

    graded_by_section: dict[int, list] = {sid: [] for sid in section_ids}
    for score, assessment in (
        await db.execute(
            select(Score, Assessment)
            .join(Assessment, Score.assessment_id == Assessment.id)
            .where(
                Assessment.course_section_id.in_(section_ids),
                Score.student_id == student_id,
                Score.status == "GRADED",
                Score.marks_obtained.is_not(None),
            )
        )
    ).all():
        graded_by_section[assessment.course_section_id].append((score, assessment))

    today = date.today()
    next_session_by_section: dict[int, ClassSession] = {}
    for session in (
        await db.execute(
            select(ClassSession)
            .where(ClassSession.course_section_id.in_(section_ids), ClassSession.date >= today)
            .order_by(ClassSession.course_section_id.asc(), ClassSession.date.asc(), ClassSession.start_time.asc())
        )
    ).scalars().all():
        next_session_by_section.setdefault(session.course_section_id, session)

    def attendance_pct_for(records):
        countable = [r for r in records if r.status != "EXCUSED"]
        if not countable:
            return None
        total_weight = sum(ATTENDANCE_WEIGHTS.get(r.status, 0.0) for r in countable)
        return round(total_weight / len(countable) * 100)

    def progress_pct_for(score_assessment_pairs):
        if not score_assessment_pairs:
            return None
        total_weight = sum(a.weight for _, a in score_assessment_pairs)
        if total_weight == 0:
            return None
        weighted = sum((s.marks_obtained / a.max_score) * a.weight for s, a in score_assessment_pairs if a.max_score)
        return round(weighted / total_weight * 100)

    summaries = []
    for cs in course_sections:
        course = courses_by_id.get(cs.course_id)
        teacher = teachers_by_id.get(cs.teacher_id)
        next_session = next_session_by_section.get(cs.id)
        summaries.append({
            "course_section_id": cs.id,
            "subject_name": course.name if course else "Unknown Subject",
            "teacher_name": f"{teacher.first_name} {teacher.last_name}" if teacher else "Unassigned",
            "progress_pct": progress_pct_for(graded_by_section[cs.id]),
            "attendance_pct": attendance_pct_for(attendance_by_section[cs.id]),
            "next_class": format_relative_day(next_session.date, next_session.start_time) if next_session else None,
        })
    return summaries


@router.get("/me/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current: CurrentPerson = Depends(require_role("STUDENT")),
):
    school_class = await get_student_school_class(db, current.id)
    course_sections = await get_class_course_sections(db, school_class.id)

    subjects = await build_subject_summaries_batch(db, course_sections, current.id)

    attendance_values = [s["attendance_pct"] for s in subjects if s["attendance_pct"] is not None]
    overall_attendance = round(sum(attendance_values) / len(attendance_values)) if attendance_values else None

    progress_values = [s["progress_pct"] for s in subjects if s["progress_pct"] is not None]
    overall_progress = round(sum(progress_values) / len(progress_values)) if progress_values else None

    today = date.today()
    horizon = today + timedelta(days=14)
    look_back = today - timedelta(days=7)  # catches still-open overdue items too
    section_ids = [cs.id for cs in course_sections]
    upcoming = []
    if section_ids:
        assessments = (
            await db.execute(
                select(Assessment)
                .where(
                    Assessment.course_section_id.in_(section_ids),
                    Assessment.due_date.is_not(None),
                    Assessment.due_date >= look_back,
                    Assessment.due_date <= horizon,
                )
                .order_by(Assessment.due_date.asc())
            )
        ).scalars().all()
        scores_by_assessment = {
            s.assessment_id: s
            for s in (await db.execute(select(Score).where(Score.student_id == current.id))).scalars().all()
        }
        subject_name_by_section = {s["course_section_id"]: s["subject_name"] for s in subjects}
        for a in assessments:
            score = scores_by_assessment.get(a.id)
            status = score.status if score else "PENDING"
            if status == "PENDING" and a.due_date < today:
                status = "OVERDUE"
            # Once an item is graded/submitted it's done - drop it from the
            # forward-looking list unless it's today's, so the coach card
            # only ever flags things that still need action.
            if status in ("GRADED", "SUBMITTED") and a.due_date < today:
                continue
            upcoming.append({
                "assessment_id": a.id,
                "title": a.title,
                "type": a.type,
                "subject_name": subject_name_by_section.get(a.course_section_id, "Unknown"),
                "due_date": a.due_date.isoformat(),
                "day_label": format_relative_day(a.due_date),
                "status": status,
            })

    return {
        "student": {
            "person_id": current.id,
            "full_name": f"{current.first_name} {current.last_name}",
            "class_label": f"{school_class.grade_name} - {school_class.section_label}",
        },
        "overall_attendance_pct": overall_attendance,
        "overall_progress_pct": overall_progress,
        "subjects": sorted(subjects, key=lambda s: (s["progress_pct"] is None, -(s["progress_pct"] or 0))),
        "upcoming": upcoming,
    }


@router.get("/me/subjects/{course_section_id}")
async def get_subject_detail(
    course_section_id: int,
    db: AsyncSession = Depends(get_db),
    current: CurrentPerson = Depends(require_role("STUDENT")),
):
    school_class = await get_student_school_class(db, current.id)
    cs = (
        await db.execute(
            select(CourseSection).where(
                CourseSection.id == course_section_id,
                CourseSection.school_class_id == school_class.id,
            )
        )
    ).scalars().first()
    if not cs:
        raise HTTPException(status_code=404, detail="Subject not found for this student")

    summary = await build_subject_summary(db, cs, current.id)

    topics = (
        await db.execute(
            select(Topic).where(Topic.course_section_id == cs.id).order_by(Topic.sort_order.asc())
        )
    ).scalars().all()

    attendance_rows = (
        await db.execute(
            select(AttendanceRecord, ClassSession)
            .join(ClassSession, AttendanceRecord.class_session_id == ClassSession.id)
            .where(ClassSession.course_section_id == cs.id, AttendanceRecord.student_id == current.id)
            .order_by(ClassSession.date.asc())
        )
    ).all()

    assessment_rows = (
        await db.execute(
            select(Assessment).where(Assessment.course_section_id == cs.id).order_by(Assessment.due_date.asc())
        )
    ).scalars().all()
    scores_by_assessment = {
        s.assessment_id: s
        for s in (
            await db.execute(select(Score).where(Score.student_id == current.id))
        ).scalars().all()
    }

    def serialize_assessment(a):
        score = scores_by_assessment.get(a.id)
        return {
            "assessment_id": a.id,
            "title": a.title,
            "type": a.type,
            "due_date": a.due_date.isoformat() if a.due_date else None,
            "status": score.status if score else "PENDING",
            "score": f"{score.marks_obtained}/{a.max_score}" if score and score.marks_obtained is not None else None,
        }

    all_assessments = [serialize_assessment(a) for a in assessment_rows]

    coverage_pct = round(100 * sum(1 for t in topics if t.is_covered) / len(topics)) if topics else None

    activity_rows = (
        await db.execute(
            select(ClassSessionLog, ClassSession)
            .join(ClassSession, ClassSessionLog.class_session_id == ClassSession.id)
            .where(ClassSession.course_section_id == cs.id)
            .order_by(ClassSession.date.desc())
            .limit(10)
        )
    ).all()

    return {
        **summary,
        "coverage_pct": coverage_pct,
        "content": [
            {"name": t.name, "is_covered": t.is_covered} for t in topics
        ],
        "attendance": [
            {"date": cs_.date.isoformat(), "status": ar.status}
            for ar, cs_ in attendance_rows
        ],
        "recent_activity": [
            {
                "date": session.date.isoformat(),
                "classwork": log.classwork,
                "homework": log.homework,
                "notes": log.notes,
            }
            for log, session in activity_rows
        ],
        "assignments": [a for a in all_assessments if a["type"] in ASSIGNMENT_TYPES],
        "assessments": [a for a in all_assessments if a["type"] not in ASSIGNMENT_TYPES],
        "important_dates": [a for a in all_assessments if a["due_date"]],
    }


@router.get("/me/notifications")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current: CurrentPerson = Depends(require_role("STUDENT")),
):
    rows = (
        await db.execute(
            select(Notification)
            .where(Notification.person_id == current.id)
            .order_by(Notification.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in rows
    ]


@router.post("/me/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current: CurrentPerson = Depends(require_role("STUDENT")),
):
    notification = (
        await db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.person_id == current.id
            )
        )
    ).scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    await db.commit()
    return {"message": "Notification marked as read"}
