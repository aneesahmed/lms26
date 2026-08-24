from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    """Simplified, student-facing notification - not the full spec's
    Event/Audience/Delivery split, just enough for the dashboard bell."""
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("person.id"), index=True)
    type = Column(String)  # GRADE_POSTED | ABSENCE | DEADLINE | ANNOUNCEMENT
    title = Column(String)
    body = Column(String, nullable=True)
    related_course_section_id = Column(Integer, ForeignKey("course_section.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
