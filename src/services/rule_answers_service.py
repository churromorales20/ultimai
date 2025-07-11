from fastapi import Depends
from sqlalchemy.orm import Session
from database.db import db_manager
from models.answered_question import AnsweredQuestion

class RuleAnswerSrvc:
  
  @classmethod  
  def loadPrevious(cls, db, identifier):
    
    return db.query(AnsweredQuestion).filter(AnsweredQuestion.identifier == identifier).order_by(AnsweredQuestion.created_at.asc()).all()
  
  @classmethod  
  def save(cls, db, question, response, identifier):
    rule_answered = AnsweredQuestion(
        question=question, 
        rule=response.rule,
        identifier=identifier,
        explanation=response.explanation,
        signals=response.signals,
        short_answer=response.short_answer
    )

    db.add(rule_answered)
    db.commit()
    db.refresh(rule_answered)

    return rule_answered.id
  
  @classmethod  
  def add_feeback(cls, db, feedback_request):

    answered_question = db.query(AnsweredQuestion).filter(AnsweredQuestion.id == feedback_request.answer_id).first()

    if answered_question:
        answered_question.in_agree = feedback_request.in_agree  
        if not feedback_request.in_agree:
            answered_question.user_response = {
              'rule': feedback_request.rule,
              'comment': feedback_request.comment
            }

        db.commit()
        db.refresh(answered_question)
        return answered_question
    
    else:
        return None