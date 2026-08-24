import asyncio
from app.database import engine, Base

# Import ALL models so Base knows about them
from app.models.org import Org
from app.models.identity import Person, RoleAssignment
from app.models.admission import AdmissionApplication
from app.models.academic import Term, Course, SubjectRequirementTemplate, SectionPlan, ResourcePlanRun, ResourcePlanAssignment, ResourceGap, ClassSession, LessonPlan
from app.models.asset import Asset, AssetMaintenance
from app.models.staff import JobApplication

async def nuke_db():
    async with engine.begin() as conn:
        print("Wiping all tables from Neon DB...")
        # use cascade on dropping tables in postgres
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(__import__('sqlalchemy').text(f"DROP TABLE IF EXISTS {table.name} CASCADE"))
        print("Recreating all tables in Neon DB...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database nuked.")

if __name__ == "__main__":
    asyncio.run(nuke_db())
