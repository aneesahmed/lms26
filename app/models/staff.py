from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class JobApplication(Base):
    __tablename__ = "job_application"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_person_id = Column(Integer, ForeignKey("person.id"))
    target_org_id = Column(Integer, ForeignKey("org.id"), nullable=False)
    
    position = Column(String) # E.g., "Math Teacher", "Librarian", "Admin"
    status = Column(String, index=True, default="APPLIED") # APPLIED, INTERVIEWED, HIRED, REJECTED
    is_locked = Column(Boolean, default=False)
    
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
