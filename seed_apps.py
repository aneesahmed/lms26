import asyncio
from app.database import AsyncSessionLocal
from app.models.admission import AdmissionApplication
from app.models.identity import Person
from app.models.org import Org

async def seed():
    async with AsyncSessionLocal() as db:
        # Create some extra people specifically for these applications
        extra_people = [
            Person(first_name="Liam", last_name="Enquiry", email="liam@test.edu"),
            Person(first_name="Noah", last_name="Applied", email="noah@test.edu"),
            Person(first_name="Oliver", last_name="Tested", email="oliver@test.edu"),
            Person(first_name="Elijah", last_name="Interviewed", email="elijah@test.edu"),
            Person(first_name="James", last_name="Offered", email="james@test.edu"),
            Person(first_name="William", last_name="Accepted", email="william@test.edu"),
            Person(first_name="Benjamin", last_name="Rejected", email="benjamin@test.edu"),
            Person(first_name="Lucas", last_name="Withdrawn", email="lucas@test.edu"),
        ]
        db.add_all(extra_people)
        await db.commit()
        
        # Now create the applications for them
        db.add_all([
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[0].id, status='ENQUIRY'),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[1].id, status='APPLIED'),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[2].id, status='TESTED'),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[3].id, status='INTERVIEWED'),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[4].id, status='OFFERED'),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[5].id, status='ACCEPTED', is_locked=True),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[6].id, status='REJECTED', is_locked=True),
            AdmissionApplication(target_org_id=1, applicant_person_id=extra_people[7].id, status='WITHDRAWN'),
        ])
        await db.commit()
    print("8 new applications seeded with all different statuses!")

if __name__ == "__main__":
    asyncio.run(seed())
