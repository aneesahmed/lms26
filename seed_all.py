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
        print("Seeding baseline data...")
        
        # 1. Create a School
        school = Org(type="SCHOOL", name="Brainiacs Main Campus")
        db.add(school)
        await db.commit()
        await db.refresh(school)
        
        # 2. Create Admin Staff
        admin = Person(first_name="Alice", last_name="Admin", email="admin@brainiacs.edu")
        db.add(admin)
        
        # 3. Create Teacher
        teacher = Person(first_name="Bob", last_name="Teacher", email="bob@brainiacs.edu")
        db.add(teacher)
        
        await db.commit()
        await db.refresh(admin)
        await db.refresh(teacher)
        db.add(RoleAssignment(person_id=admin.id, org_id=school.id, role="ADMIN"))
        db.add(RoleAssignment(person_id=teacher.id, org_id=school.id, role="TEACHER"))
        await db.commit()
        
        # 4. Create applicants for testing states
        extra_people = [
            Person(first_name="Liam", last_name="Enquiry", email="liam@test.edu"),
            Person(first_name="Noah", last_name="Applied", email="noah@test.edu"),
            Person(first_name="Oliver", last_name="Tested", email="oliver@test.edu"),
            Person(first_name="Elijah", last_name="Interviewed", email="elijah@test.edu"),
            Person(first_name="James", last_name="Offered", email="james@test.edu"),
            Person(first_name="William", last_name="Accepted", email="william@test.edu"),
            Person(first_name="Benjamin", last_name="Rejected", email="benjamin@test.edu"),
            Person(first_name="Lucas", last_name="Withdrawn", email="lucas@test.edu"),
            Person(first_name="Evan", last_name="Student", email="evan@test.edu") # Form submission test user
        ]
        db.add_all(extra_people)
        await db.commit()
        
        # Now create the applications for them
        db.add_all([
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[0].id, status='ENQUIRY'),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[1].id, status='APPLIED'),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[2].id, status='TESTED'),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[3].id, status='INTERVIEWED'),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[4].id, status='OFFERED'),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[5].id, status='ACCEPTED', is_locked=True),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[6].id, status='REJECTED', is_locked=True),
            AdmissionApplication(target_org_id=school.id, applicant_person_id=extra_people[7].id, status='WITHDRAWN'),
        ])
        await db.commit()
    print("Database wiped and cleanly seeded with all roles and applications!")

if __name__ == "__main__":
    asyncio.run(seed())
