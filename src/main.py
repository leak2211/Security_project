from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.schemas import UserCreate

app = FastAPI(title="Registration")

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