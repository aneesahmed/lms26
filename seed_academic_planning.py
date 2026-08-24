import asyncio
from app.database import AsyncSessionLocal, engine, Base
from app.models.academic import Term, Course, SubjectRequirementTemplate, SectionPlan
from app.models.org import Org
from datetime import date

async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding Resource Planning Base Data...")

        # 1. Terms
        fall = Term(name="Fall 2026", start_date=date(2026, 8, 25), end_date=date(2026, 12, 15), org_id=1)
        db.add(fall)
        await db.commit()
        await db.refresh(fall)
        
        # 2. Courses
        bio = Course(name="Biology 102", code="BIO-102", grade_level="Grade 10", facility_type_needed="LAB")
        math = Course(name="Math 102", code="MTH-102", grade_level="Grade 10", facility_type_needed="REGULAR")
        db.add_all([bio, math])
        await db.commit()
        await db.refresh(bio)
        await db.refresh(math)
        
        # 3. Subject Requirement Templates
        db.add(SubjectRequirementTemplate(
            course_id=bio.id, 
            role_needed="SUBJECT_TEACHER", 
            room_type_needed="LAB",
            equipment_needed=["MICROSCOPE"]
        ))
        db.add(SubjectRequirementTemplate(
            course_id=math.id, 
            role_needed="SUBJECT_TEACHER", 
            room_type_needed="REGULAR"
        ))
        await db.commit()
        
        # 4. Section Plan (We estimate 90 students, max 30 per class -> should result in 3 sections)
        db.add(SectionPlan(
            grade_level="Grade 10",
            term_id=fall.id,
            estimated_enrollment=90,
            max_section_size=30
        ))
        await db.commit()
        print("Base planning data seeded! Ready to run simulation.")

if __name__ == "__main__":
    asyncio.run(seed())
