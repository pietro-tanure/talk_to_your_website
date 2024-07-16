from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from src.url_chat import URLChat


app = FastAPI()

# Initialize URLChat model
url_chat = URLChat()

class URLIndexRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    url: str
    question: str

@app.post("/index-url/")
def index_url(request: URLIndexRequest):
    try:
        url_chat.index(request.url)
        return {"message": "URL indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/")
def ask_question(request: QuestionRequest) -> Dict:
    try:
        response = url_chat.ask(request.url, request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))