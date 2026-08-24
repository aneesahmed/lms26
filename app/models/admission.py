from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class AdmissionApplication(Base):
    __tablename__ = "admission_application"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_person_id = Column(Integer, ForeignKey("person.id"), nullable=True)
    target_org_id = Column(Integer, ForeignKey("org.id"), nullable=False)
    
    # ENQUIRY, APPLIED, TESTED, INTERVIEWED, OFFERED, ACCEPTED, REJECTED, WITHDRAWN
    status = Column(String, default="ENQUIRY", index=True)
    
    # Admin lock
    is_locked = Column(Boolean, default=False)
    
    # Document paths (saved locally for now, multimedia DB later)
    # Storing as a JSON dictionary: {"birth_certificate": "path/...", "transfer_certificate": "path/..."}
    documents = Column(JSON, default=dict)
    
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)

