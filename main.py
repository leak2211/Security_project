from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import bleach
from src.schemas import UserCreate
import os
from dotenv import load_dotenv
import sys

load_dotenv()

secret = os.getenv('APP_SECRET')

if secret is None:
    print("Ошибка: Переменная окружения APP_SECRET не найдена!")
    sys.exit(1)

print(f"System started. Secret hash: {secret[:3]}***")

app = FastAPI(title="Registration with Comments")

templates = Jinja2Templates(directory="templates")

comments_storage = []

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong']
ALLOWED_ATTRIBUTES = {} 

def sanitize_text(text: str) -> str:
    """
    Очистка текста от опасных тегов и атрибутов.
    Разрешены только теги: b, i, u, em, strong
    """
    if not text:
        return ""
    
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True  
    )
    
    return cleaned

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        return response

app.add_middleware(CSPMiddleware)

@app.get("/comments", response_class=HTMLResponse)
async def get_comments(request: Request):
    """Отображение страницы с комментариями"""
    return templates.TemplateResponse(
        "comments.html", 
        {"request": request, "comments": comments_storage}
    )

@app.post("/comments")
async def post_comment(comment_text: str = Form(...)):
    """Обработка POST запроса с комментарием"""
    if not comment_text or len(comment_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    
    cleaned_comment = sanitize_text(comment_text)
    
    comments_storage.append(cleaned_comment)
    
    return RedirectResponse(url="/comments", status_code=303)
@app.post("/registration")
async def register(user: UserCreate):
    return {
        "msg": "User created",
        "user": user.username,
        "email": user.email
    }

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")