from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Org(Base):
    __tablename__ = "org"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("org.id"), nullable=True)
    type = Column(String, index=True) # ORGANIZATION, SCHOOL, BRANCH
    name = Column(String)
