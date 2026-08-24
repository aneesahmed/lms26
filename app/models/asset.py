from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Asset(Base):
    __tablename__ = "asset"
    id = Column(Integer, primary_key=True, index=True)
    
    # E.g., BUILDING, CLASSROOM, GROUND, EQUIPMENT
    type = Column(String, index=True)
    name = Column(String, index=True)
    
    # Self-referential relationship (e.g. Classroom belongs to Building)
    parent_id = Column(Integer, ForeignKey("asset.id"), nullable=True)
    
    # Which school/org owns this asset
    org_id = Column(Integer, ForeignKey("org.id"))
    
    # Additional attributes
    capacity = Column(Integer, nullable=True) # Useful for Classrooms
    status = Column(String, default="ACTIVE") # ACTIVE, MAINTENANCE, INACTIVE
