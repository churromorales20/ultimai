import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from database.db import db_manager

class AnsweredQuestion(db_manager.Base):
    __tablename__ = "answered_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String, index=True)
    question = Column(String, index=True)
    rule = Column(String, index=True)
    explanation = Column(String)
    short_answer = Column(String)
    in_agree = Column(Boolean, default=None)
    user_response = Column(JSON, nullable=True)
    signals = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)