from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)

class RoleAssignment(Base):
    __tablename__ = "role_assignment"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person.id"))
    org_id = Column(Integer, ForeignKey("org.id"))
    role = Column(String, index=True) # STUDENT, TEACHER, ADMIN, GUARDIAN
    local_identifier = Column(String, nullable=True) # GR number / employee number

