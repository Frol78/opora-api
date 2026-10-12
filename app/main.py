from fastapi import FastAPI
from app.database import Base, engine
from app.models import User, CheckIn  # noqa: F401 — нужны, чтобы таблицы попали в metadata
from app.routers.auth import router as auth_router
from app.routers.checkins import router as checkins_router

# Создаёт только отсутствующие таблицы, существующие не трогает
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Опора API", version="1.0.0")
app.include_router(auth_router)
app.include_router(checkins_router)

@app.get("/")
def root():
    return {"message": "Добро пожаловать в API приложения 'Опора'! 🌟"}
