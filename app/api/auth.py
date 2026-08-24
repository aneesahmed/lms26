from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.identity import Person, RoleAssignment
from app.services.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    person_id: int
    full_name: str


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )

    person = (await db.execute(select(Person).where(Person.email == body.email))).scalars().first()
    if not person or not person.password_hash or not verify_password(body.password, person.password_hash):
        raise invalid_credentials

    role_assignment = (
        await db.execute(select(RoleAssignment).where(RoleAssignment.person_id == person.id))
    ).scalars().first()
    if not role_assignment:
        raise HTTPException(status_code=403, detail="No role assigned to this account")

    token = create_access_token(person_id=person.id, role=role_assignment.role, org_id=role_assignment.org_id)
    return LoginResponse(
        access_token=token,
        role=role_assignment.role,
        person_id=person.id,
        full_name=f"{person.first_name} {person.last_name}",
    )
