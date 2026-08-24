import asyncio
from app.database import engine, Base, AsyncSessionLocal
from app.models.org import Org
from app.models.identity import Person, RoleAssignment
from app.models.admission import AdmissionApplication

async def seed():
    async with engine.begin() as conn:
        print("Recreating all tables to ensure clean state...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        print("Seeding data...")
        
        # 1. Create a School
        school = Org(type="SCHOOL", name="Brainiacs Main Campus")
        db.add(school)
        await db.commit()
        await db.refresh(school)
        
        # 2. Create Admin Staff
        admin = Person(first_name="Alice", last_name="Admin", email="admin@brainiacs.edu")
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        db.add(RoleAssignment(person_id=admin.id, org_id=school.id, role="ADMIN"))
        
        # 3. Create Teacher
        teacher = Person(first_name="Bob", last_name="Teacher", email="bob@brainiacs.edu")
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        db.add(RoleAssignment(person_id=teacher.id, org_id=school.id, role="TEACHER"))
        
        # 4. Create 5 Students
        students_data = [
            ("Charlie", "Student", "charlie@student.edu"),
            ("Diana", "Student", "diana@student.edu"),
            ("Evan", "Student", "evan@student.edu"),
            ("Fiona", "Student", "fiona@student.edu"),
            ("George", "Student", "george@student.edu"),
        ]
        
        for fname, lname, email in students_data:
            student = Person(first_name=fname, last_name=lname, email=email)
            db.add(student)
            await db.commit()
            await db.refresh(student)
            db.add(RoleAssignment(person_id=student.id, org_id=school.id, role="STUDENT"))
            
            # Optionally, we can also give them an AdmissionApplication in 'ACCEPTED' state 
            # to match their enrolled student status, or leave it as is.
            
        await db.commit()
        print("Successfully seeded 1 Admin, 1 Teacher, and 5 Students!")

if __name__ == "__main__":
    asyncio.run(seed())
