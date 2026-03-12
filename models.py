from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, index=True) # e.g., "April2025" or "April 2025"
    member_name = Column(String, index=True)
    amount = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
