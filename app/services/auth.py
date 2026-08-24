import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.identity import Person

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(person_id: int, role: str, org_id: int | None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(person_id), "role": role, "org_id": org_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


class CurrentPerson:
    def __init__(self, person: Person, role: str, org_id: int | None):
        self.person = person
        self.id = person.id
        self.role = role
        self.org_id = org_id
        self.first_name = person.first_name
        self.last_name = person.last_name
        self.email = person.email


async def get_current_person(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentPerson:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        person_id = payload.get("sub")
        role = payload.get("role")
        org_id = payload.get("org_id")
        if person_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    person = (await db.execute(select(Person).where(Person.id == int(person_id)))).scalars().first()
    if not person:
        raise credentials_exception

    return CurrentPerson(person=person, role=role, org_id=org_id)


def require_role(*allowed_roles: str):
    async def dependency(current: CurrentPerson = Depends(get_current_person)) -> CurrentPerson:
        if current.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(allowed_roles)}",
            )
        return current

    return dependency
