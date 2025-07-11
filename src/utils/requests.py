from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
  question: str

class AnswerFeedbackRequest(BaseModel):
  in_agree: bool
  answer_id: str
  rule: Optional[str] = None
  comment: Optional[str] = None