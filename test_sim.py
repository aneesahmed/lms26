import asyncio
from app.database import AsyncSessionLocal
from app.models.academic import Term, Course, SubjectRequirementTemplate, SectionPlan, ResourcePlanRun, ResourcePlanAssignment, ResourceGap
from app.models.identity import Person, RoleAssignment
from app.models.asset import Asset
from app.models.org import Org
from sqlalchemy.future import select
import math

async def test_sim():
    async with AsyncSessionLocal() as db:
        term_id = 5
        grade_level = "Grade 10"
        
        stmt = select(SectionPlan).where(SectionPlan.term_id == term_id, SectionPlan.grade_level == grade_level)
        section_plan = (await db.execute(stmt)).scalars().first()
        
        num_sections = math.ceil(section_plan.estimated_enrollment / section_plan.max_section_size)
        print("Num sections:", num_sections)
        
        run = ResourcePlanRun(term_id=term_id, grade_level=grade_level, status="SIMULATED")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        print("Run created")
        
        courses = (await db.execute(select(Course).where(Course.grade_level == grade_level))).scalars().all()
        for course in courses:
            print("Course:", course.name)
            template = (await db.execute(select(SubjectRequirementTemplate).where(SubjectRequirementTemplate.course_id == course.id))).scalars().first()
            if not template:
                continue
                
            expected_role = f"{course.name.split(' ')[0]} Teacher" 
            stmt = select(Person).join(RoleAssignment, RoleAssignment.person_id == Person.id).where(RoleAssignment.role == expected_role)
            available_teachers = (await db.execute(stmt)).scalars().all()
            print("Found teachers:", available_teachers)
            
            teachers_needed = template.count_per_section * num_sections
            teachers_have = len(available_teachers)
            
            for i in range(num_sections):
                section_name = f"Section {chr(65+i)}"
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
                
if __name__ == "__main__":
    asyncio.run(test_sim())
