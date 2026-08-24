import asyncio
from app.database import AsyncSessionLocal
from app.models.identity import Person, RoleAssignment
from app.models.org import Org

async def seed_more_staff():
    async with AsyncSessionLocal() as db:
        print("Seeding Additional Staff...")
        
        staff_data = [
            ("Emily", "Science", "emily.sci@test.edu", "Biology Teacher"),
            ("Mark", "Math", "mark.m@test.edu", "Math Teacher"),
            ("Julia", "History", "julia.h@test.edu", "History Teacher"),
            ("Tom", "Assistant", "tom.ta@test.edu", "Teaching Assistant"),
            ("Gary", "Support", "gary.s@test.edu", "Support Staff"),
            ("Rachel", "PE", "rachel.pe@test.edu", "PE Teacher"),
            ("Coach", "Carter", "coach.c@test.edu", "Head Coach"),
            ("Mike", "Lab", "mike.lab@test.edu", "Lab Assistant"),
            ("Lisa", "Coord", "lisa.c@test.edu", "Academic Coordinator"),
            ("Robert", "Manager", "robert.m@test.edu", "Senior Manager")
        ]
        
        for fname, lname, email, role in staff_data:
            p = Person(first_name=fname, last_name=lname, email=email)
            db.add(p)
            await db.commit()
            await db.refresh(p)
            
            ra = RoleAssignment(person_id=p.id, org_id=1, role=role)
            db.add(ra)
            
        await db.commit()
        print("Additional staff seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_more_staff())
