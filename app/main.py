from fastapi import FastAPI
from app.database import Base, engine
from app.models import User, CheckIn
from app.routers.auth import router as auth_router

app = FastAPI(title="Опора API", version="1.0.0")
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Добро пожаловать в API приложения 'Опора'! 🌟"}
