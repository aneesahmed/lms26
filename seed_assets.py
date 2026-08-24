import asyncio
from app.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.org import Org

async def seed_assets():
    async with AsyncSessionLocal() as db:
        print("Seeding Assets...")

        # 1. ROOT ASSETS
        main_block = Asset(name="Main Academic Block", type="BUILDING", org_id=1)
        tech_center = Asset(name="Technology Center", type="BUILDING", org_id=1)
        sports_field = Asset(name="Main Sports Field", type="GROUND", org_id=1)
        basketball_court = Asset(name="Basketball Court", type="GROUND", org_id=1)
        
        db.add_all([main_block, tech_center, sports_field, basketball_court])
        await db.commit()
        await db.refresh(main_block)
        await db.refresh(tech_center)

        # 2. FLOORS
        mb_ground = Asset(name="Ground Floor", type="FLOOR", parent_id=main_block.id, org_id=1)
        mb_first = Asset(name="First Floor", type="FLOOR", parent_id=main_block.id, org_id=1)
        tc_first = Asset(name="First Floor", type="FLOOR", parent_id=tech_center.id, org_id=1)
        
        db.add_all([mb_ground, mb_first, tc_first])
        await db.commit()
        await db.refresh(mb_ground)
        await db.refresh(mb_first)
        await db.refresh(tc_first)

        # 3. ROOMS AND LABS
        room_101 = Asset(name="Room 101", type="CLASSROOM", parent_id=mb_ground.id, capacity=30, org_id=1)
        room_102 = Asset(name="Room 102", type="CLASSROOM", parent_id=mb_ground.id, capacity=30, org_id=1)
        bio_lab = Asset(name="Biology Lab", type="CLASSROOM", parent_id=mb_ground.id, capacity=25, org_id=1)
        
        physics_lab = Asset(name="Physics Lab", type="CLASSROOM", parent_id=mb_first.id, capacity=25, org_id=1)
        chem_lab = Asset(name="Chemistry Lab", type="CLASSROOM", parent_id=mb_first.id, capacity=25, org_id=1)
        
        cs_lab_a = Asset(name="Computer Science Lab A", type="CLASSROOM", parent_id=tc_first.id, capacity=40, org_id=1)
        cs_lab_b = Asset(name="Computer Science Lab B", type="CLASSROOM", parent_id=tc_first.id, capacity=40, org_id=1)
        
        db.add_all([room_101, room_102, bio_lab, physics_lab, chem_lab, cs_lab_a, cs_lab_b])
        await db.commit()
        await db.refresh(room_101)
        await db.refresh(bio_lab)
        await db.refresh(chem_lab)
        await db.refresh(cs_lab_a)

        # 4. EQUIPMENT
        led_1 = Asset(name="75-inch Smart LED", type="EQUIPMENT", parent_id=room_101.id, org_id=1)
        proj_1 = Asset(name="Epson 4K Projector", type="EQUIPMENT", parent_id=cs_lab_a.id, org_id=1)
        microscope = Asset(name="Digital Microscope Set", type="EQUIPMENT", parent_id=bio_lab.id, org_id=1)
        fume_hood = Asset(name="Safety Fume Hood", type="EQUIPMENT", parent_id=chem_lab.id, org_id=1)
        
        db.add_all([led_1, proj_1, microscope, fume_hood])
        await db.commit()
        
        print("Successfully seeded all physical assets!")

if __name__ == "__main__":
    asyncio.run(seed_assets())
