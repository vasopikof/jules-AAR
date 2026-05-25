from sqlalchemy import Column, Integer, String, Text
from .database import Base

class ReflectionSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    context_text = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    report = Column(Text, nullable=True)
