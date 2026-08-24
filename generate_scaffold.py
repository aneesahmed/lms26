import os

files = {
    "requirements.txt": """fastapi
uvicorn
sqlalchemy
asyncpg
pydantic
python-dotenv
""",
    "app/__init__.py": "",
    "app/database.py": """import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# We expect the user to provide this in an .env file or environment variable.
# Example Neon connection string: postgresql+asyncpg://user:password@ep-withered-snow-123456.us-east-2.aws.neon.tech/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/lms")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
""",
    "app/models/__init__.py": "",
    "app/models/org.py": """from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Org(Base):
    __tablename__ = "org"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("org.id"), nullable=True)
    type = Column(String, index=True) # ORGANIZATION, SCHOOL, BRANCH
    name = Column(String)
""",
    "app/models/identity.py": """from sqlalchemy import Column, Integer, String
from app.database import Base

class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
""",
    "app/models/admission.py": """from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class AdmissionApplication(Base):
    __tablename__ = "admission_application"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_person_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    target_org_id = Column(Integer, ForeignKey("org.id"), nullable=False)
    
    # ENQUIRY, APPLIED, TESTED, INTERVIEWED, OFFERED, ACCEPTED, REJECTED, WITHDRAWN
    status = Column(String, default="ENQUIRY", index=True)
    
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
""",
    "app/api/__init__.py": "",
    "app/api/admission.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.admission import AdmissionApplication

router = APIRouter(prefix="/admission", tags=["admission"])

class AdmissionCreate(BaseModel):
    target_org_id: int
    applicant_person_id: Optional[int] = None
    status: str = "ENQUIRY"

class AdmissionResponse(BaseModel):
    id: int
    target_org_id: int
    applicant_person_id: Optional[int]
    status: str
    applied_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=AdmissionResponse)
async def create_application(app: AdmissionCreate, db: AsyncSession = Depends(get_db)):
    db_app = AdmissionApplication(**app.model_dump())
    db.add(db_app)
    await db.commit()
    await db.refresh(db_app)
    return db_app

@router.get("/", response_model=List[AdmissionResponse])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdmissionApplication))
    return result.scalars().all()
""",
    "app/main.py": """from fastapi import FastAPI
from app.database import engine, Base
# Ensure all models are imported so Base.metadata knows about them
from app.models.org import Org
from app.models.identity import Person
from app.models.admission import AdmissionApplication
from app.api import admission
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="BrainiacsLMSV1", lifespan=lifespan)

app.include_router(admission.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to BrainiacsLMSV1 Admission API"}
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

print("Files generated successfully.")
