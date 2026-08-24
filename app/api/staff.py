from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.staff import JobApplication
from app.models.identity import Person, RoleAssignment
from app.services.auth import require_role

router = APIRouter(prefix="/staff", tags=["Staff"])

class JobApplicationResponse(BaseModel):
    id: int
    applicant_person_id: int
    position: str
    status: str
    is_locked: bool
    
    class Config:
        from_attributes = True

class RoleAssignmentCreate(BaseModel):
    person_id: int
    role: str # TEACHER, ADMIN, etc.

# 1. Get all Job Applications
@router.get("/applications", response_model=List[JobApplicationResponse])
async def list_job_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobApplication))
    return result.scalars().all()

# 2. Update Application Status
@router.put("/applications/{app_id}/status", response_model=JobApplicationResponse)
async def update_job_status(
    app_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    result = await db.execute(select(JobApplication).where(JobApplication.id == app_id))
    db_app = result.scalars().first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db_app.status = status
    await db.commit()
    await db.refresh(db_app)
    return db_app

# 3. Get all active staff (People with RoleAssignment != STUDENT)
# Note: For simplicity, we just fetch RoleAssignments directly here and join Person
@router.get("/active")
async def list_active_staff(db: AsyncSession = Depends(get_db)):
    # Fetch roles that are not STUDENT
    stmt = select(RoleAssignment, Person).join(Person, RoleAssignment.person_id == Person.id).where(RoleAssignment.role != "STUDENT")
    result = await db.execute(stmt)
    
    staff_list = []
    for role, person in result.all():
        staff_list.append({
            "person_id": person.id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "email": person.email,
            "role": role.role,
            "role_id": role.id
        })
    return staff_list

# 4. Assign a Role (Hire someone)
@router.post("/roles")
async def assign_role(
    assignment: RoleAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("ADMIN")),
):
    # In reality, org_id would be passed or determined from context. We default to 1.
    new_role = RoleAssignment(person_id=assignment.person_id, org_id=1, role=assignment.role)
    db.add(new_role)
    await db.commit()
    return {"message": "Role assigned successfully"}
