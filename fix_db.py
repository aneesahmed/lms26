import asyncio
from app.database import engine
from sqlalchemy import text

async def fix():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE course ADD COLUMN facility_type_needed VARCHAR DEFAULT 'REGULAR'"))
            print("Altered course table.")
        except Exception as e:
            print("Error altering course:", e)
            
        try:
            await conn.execute(text("DROP TABLE IF EXISTS resource_plan_assignment, resource_gap, resource_plan_run, section_plan, subject_req_template CASCADE"))
            print("Dropped new tables so they can be recreated.")
        except Exception as e:
            print("Error dropping tables:", e)

if __name__ == "__main__":
    asyncio.run(fix())
