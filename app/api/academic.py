from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel
from datetime import date
from typing import Optional
import math

from app.database import get_db
from app.models.academic import (
    Term, Course, SubjectRequirementTemplate,
    SectionPlan, ResourcePlanRun, ResourcePlanAssignment, ResourceGap,
    CalendarDay,
)
from app.models.identity import Person, RoleAssignment
from app.models.asset import Asset
from app.services.auth import require_role
from app.services.calendar_sync import fetch_google_holidays

router = APIRouter(prefix="/academic", tags=["Academic"])


@router.get("/calendar")
async def get_calendar(
    org_id: int,
    start: date,
    end: date,
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(CalendarDay)
            .where(CalendarDay.org_id == org_id, CalendarDay.date >= start, CalendarDay.date <= end)
            .order_by(CalendarDay.date.asc())
        )
    ).scalars().all()
    return [
        {"date": r.date.isoformat(), "day_type": r.day_type, "label": r.label, "source": r.source}
        for r in rows
    ]


@router.post("/calendar/sync-holidays")
async def sync_holidays(
    org_id: int,
    start: date,
    end: date,
    country_code: str = "pk",
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    holidays = fetch_google_holidays(country_code, start, end)
    created = 0
    for holiday_date, label in holidays:
        existing = (
            await db.execute(
                select(CalendarDay).where(CalendarDay.org_id == org_id, CalendarDay.date == holiday_date)
            )
        ).scalars().first()
        if existing:
            existing.day_type = "HOLIDAY"
            existing.label = label
            existing.source = "GOOGLE_SYNC"
        else:
            db.add(CalendarDay(org_id=org_id, date=holiday_date, day_type="HOLIDAY", label=label, source="GOOGLE_SYNC"))
            created += 1
    await db.commit()
    return {"message": f"Synced {len(holidays)} holidays, {created} new", "holidays": [
        {"date": d.isoformat(), "label": l} for d, l in holidays
    ]}

# Endpoints to create/fetch the templates and plans

@router.get("/templates")
async def get_templates(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SubjectRequirementTemplate))
    return res.scalars().all()

@router.get("/section_plans")
async def get_section_plans(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SectionPlan))
    return res.scalars().all()

@router.post("/simulate_run/{term_id}/{grade_level}")
async def simulate_plan_run(
    term_id: int,
    grade_level: str,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    # 1. Get the SectionPlan for this grade & term
    stmt = select(SectionPlan).where(SectionPlan.term_id == term_id, SectionPlan.grade_level == grade_level)
    section_plan = (await db.execute(stmt)).scalars().first()
    
    if not section_plan:
        raise HTTPException(status_code=404, detail="No SectionPlan found for this term and grade.")
        
    # Calculate required sections
    num_sections = math.ceil(section_plan.estimated_enrollment / section_plan.max_section_size)
    section_plan.computed_section_count = num_sections
    await db.commit()
    
    # 2. Create a ResourcePlanRun
    run = ResourcePlanRun(term_id=term_id, grade_level=grade_level, status="SIMULATED")
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # 3. Get all courses for this grade
    courses = (await db.execute(select(Course).where(Course.grade_level == grade_level))).scalars().all()
    
    # 4. Generate Assignments and Gaps
    for course in courses:
        # Get requirement template
        template = (await db.execute(select(SubjectRequirementTemplate).where(SubjectRequirementTemplate.course_id == course.id))).scalars().first()
        if not template:
            continue
            
        # Count available teachers for this course based on roles (mock logic: check RoleAssignment)
        # e.g., if Biology 101, look for "Biology Teacher"
        expected_role = f"{course.name.split(' ')[0]} Teacher" 
        stmt = select(Person).join(RoleAssignment, RoleAssignment.person_id == Person.id).where(RoleAssignment.role == expected_role)
        available_teachers = (await db.execute(stmt)).scalars().all()
        
        teachers_needed = template.count_per_section * num_sections
        teachers_have = len(available_teachers)
        
        # Assign available teachers to sections
        for i in range(num_sections):
            section_name = f"Section {chr(65+i)}" # Section A, B, C...
            
            teacher_id = available_teachers[i].id if i < teachers_have else None
            status = "PROPOSED" if teacher_id else "GAP"
            
            assignment = ResourcePlanAssignment(
                plan_run_id=run.id,
                target_type="CLASS",
                target_id=section_name,
                course_id=course.id,
                role=template.role_needed,
                resource_id=teacher_id,
                status=status
            )
            db.add(assignment)
            
        # If we have a gap, create a ResourceGap
        if teachers_have < teachers_needed:
            gap = ResourceGap(
                plan_run_id=run.id,
                role_needed=template.role_needed,
                course_id=course.id,
                count_short=teachers_needed - teachers_have,
                status="OPEN"
            )
            db.add(gap)
            
    await db.commit()
    return {"message": "Simulation complete", "plan_run_id": run.id, "computed_sections": num_sections}

@router.get("/run/{run_id}/results")
async def get_run_results(run_id: int, db: AsyncSession = Depends(get_db)):
    assignments = (await db.execute(select(ResourcePlanAssignment).where(ResourcePlanAssignment.plan_run_id == run_id))).scalars().all()
    gaps = (await db.execute(select(ResourceGap).where(ResourceGap.plan_run_id == run_id))).scalars().all()
    
    # Hydrate assignment names for UI
    results = []
    for a in assignments:
        course = (await db.execute(select(Course).where(Course.id == a.course_id))).scalars().first()
        teacher = (await db.execute(select(Person).where(Person.id == a.resource_id))).scalars().first() if a.resource_id else None
        results.append({
            "section": a.target_id,
            "course": course.name if course else "Unknown",
            "role": a.role,
            "teacher": f"{teacher.first_name} {teacher.last_name}" if teacher else "None",
            "status": a.status
        })
        
    gap_results = []
    for g in gaps:
        course = (await db.execute(select(Course).where(Course.id == g.course_id))).scalars().first()
        gap_results.append({
            "course": course.name if course else "Unknown",
            "role_needed": g.role_needed,
            "count_short": g.count_short,
            "status": g.status
        })
        
    return {"assignments": results, "gaps": gap_results}
