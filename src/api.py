import uuid
from typing import Optional
from fastapi import FastAPI, Response, Cookie, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from services.rule_questions_service import UltimateRulesAssistantSrvc
from services.rule_answers_service import RuleAnswerSrvc
from services.views_service import ViewsSrvc
from sqlalchemy.orm import Session
from database.db import db_manager
from utils.requests import AnswerFeedbackRequest, QuestionRequest

db_manager.create_all_tables()

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
def index(
    response: Response, 
    ultimai_identifier: str | None = Cookie(default=None), 
    preferred_language: str | None = Cookie(default=None), 
    accept_language: Optional[str] = Header(None, alias="Accept-Language")):
    
    if not ultimai_identifier:
        response.set_cookie(
            key="ultimai_identifier",
            value=uuid.uuid4(),
            httponly=True
        )
    
    if not preferred_language:
        languages = accept_language.split(",")
        browser_language = languages[0].split(";")[0].strip()
        response.set_cookie(
            key="preferred_language",
            value=browser_language[:2]
        )

        preferred_language = browser_language[:2]

    return ViewsSrvc.render('home', preferred_language)

@app.get("/init")
def init(
    ultimai_identifier: str | None = Cookie(default=None),
    db: Session = Depends(db_manager.get_db),
    answers = []):
    
    if ultimai_identifier:
        answers = RuleAnswerSrvc.loadPrevious(db, ultimai_identifier)

    return {"answers": answers}

@app.post("/")
def response_answer(
    payload: QuestionRequest, 
    preferred_language: str | None = Cookie(default=None), 
    db: Session = Depends(db_manager.get_db),
    ultimai_identifier: str | None = Cookie(default=None)):
    try:
        response = UltimateRulesAssistantSrvc.invoke(payload.question, ultimai_identifier, preferred_language)
        id = RuleAnswerSrvc.save(db, payload.question, response, ultimai_identifier)
        response.id = id

        return {"success": True, "response": response}
    except Exception as e:
        print(e)
        return {"success": False}
    
@app.post("/answer/feedback")
def answer_feedback(payload: AnswerFeedbackRequest, db: Session = Depends(db_manager.get_db)):
    try:
        RuleAnswerSrvc.add_feeback(db, payload)

        return {"success": True}
    except Exception as e:
        print(e)
        return {"success": False}
    
@app.get("/reset")
def reset_conversation(response: Response, ultimai_identifier: str | None = Cookie(default=None)):
    response.set_cookie(
        key="ultimai_identifier",
        value=uuid.uuid4(),
        httponly=True
    )

    UltimateRulesAssistantSrvc.remove_memory(ultimai_identifier)

    return {"success": True}

@app.get("/language/select/{lang}")
async def set_cookie_and_redirect(lang: str, response: Response):
    
    response.set_cookie(
        key="preferred_language",
        value=lang
    )
    return {'success': True}