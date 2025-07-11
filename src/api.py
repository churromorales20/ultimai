import uuid
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import FastAPI, Response, Cookie, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from services.rule_questions_service import UltimateRulesAssistantSrvc
from services.rule_answers_service import RuleAnswerSrvc
from services.views_service import ViewsSrvc

app = FastAPI()
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def root(
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

class QuestionRequest(BaseModel):
    question: str

class AnswerFeedbackRequest(BaseModel):
    in_agree: bool
    answer_id: str
    rule: Optional[str] = None  # Rule es opcional y puede ser None
    comment: Optional[str] = None  # Comment es opcional y puede ser None

@app.get("/init")
async def root(ultimai_identifier: str | None = Cookie(default=None)):
    answers = []
    if ultimai_identifier:
        answers = RuleAnswerSrvc.loadPrevious(ultimai_identifier)

    return {"answers": answers}

@app.post("/")
async def root(
    payload: QuestionRequest, 
    preferred_language: str | None = Cookie(default=None), 
    ultimai_identifier: str | None = Cookie(default=None)):
    try:
        response = UltimateRulesAssistantSrvc.invoke(payload.question, ultimai_identifier, preferred_language)
        id = RuleAnswerSrvc.save(payload.question, response, ultimai_identifier)

        response.id = id
        return {"success": True, "response": response}
    except Exception as e:
        print(e)
        return {"success": False}
    
@app.post("/answer/feedback")
async def root(payload: AnswerFeedbackRequest):
    
    try:
        RuleAnswerSrvc.add_feeback(payload)

        return {"success": True}
    except Exception as e:
        print(e)
        return {"success": False}
    
@app.get("/reset")
async def root(response: Response, ultimai_identifier: str | None = Cookie(default=None)):
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