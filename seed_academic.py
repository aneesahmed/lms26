import asyncio
from app.database import AsyncSessionLocal
from app.models.academic import Term, Course, CourseSection
from app.models.identity import Person
from app.models.asset import Asset
from app.models.org import Org
from app.models.asset import Asset
from sqlalchemy.future import select
from datetime import date

async def seed_academic():
    async with AsyncSessionLocal() as db:
        print("Seeding Academic Data...")

        # 1. Terms
        fall_term = Term(name="Fall 2026", start_date=date(2026, 8, 25), end_date=date(2026, 12, 15), org_id=1)
        spring_term = Term(name="Spring 2027", start_date=date(2027, 1, 10), end_date=date(2027, 5, 20), org_id=1)
        db.add_all([fall_term, spring_term])
        await db.commit()
        await db.refresh(fall_term)
        
        # 2. Courses
        bio_course = Course(name="Biology 101", code="BIO-101", grade_level="Grade 10", description="Introduction to Biology")
        math_course = Course(name="Algebra II", code="MTH-201", grade_level="Grade 10", description="Advanced Algebra")
        hist_course = Course(name="World History", code="HIS-101", grade_level="Grade 9", description="History of the world")
        db.add_all([bio_course, math_course, hist_course])
        await db.commit()
        await db.refresh(bio_course)
        await db.refresh(math_course)
        await db.refresh(hist_course)
        
        # 3. Find Teachers and Rooms
        emily = (await db.execute(select(Person).where(Person.email == "emily.sci@test.edu"))).scalars().first()
        mark = (await db.execute(select(Person).where(Person.email == "mark.m@test.edu"))).scalars().first()
        
        bio_lab = (await db.execute(select(Asset).where(Asset.name == "Biology Lab"))).scalars().first()
        room_101 = (await db.execute(select(Asset).where(Asset.name == "Room 101"))).scalars().first()

        # 4. Sections
        if emily and bio_lab:
            db.add(CourseSection(name="Section A", course_id=bio_course.id, term_id=fall_term.id, teacher_id=emily.id, classroom_id=bio_lab.id, capacity=25))
            
        if mark and room_101:
            db.add(CourseSection(name="Section A", course_id=math_course.id, term_id=fall_term.id, teacher_id=mark.id, classroom_id=room_101.id, capacity=30))
            db.add(CourseSection(name="Section B", course_id=math_course.id, term_id=fall_term.id, teacher_id=mark.id, classroom_id=room_101.id, capacity=30))
            
        await db.commit()
        print("Academic Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_academic())
