from pydantic import BaseModel, EmailStr
from datetime import datetime

# Схема для регистрации (что клиент отправляет нам при создании аккаунта)
class UserCreate(BaseModel):
    email: EmailStr  # Pydantic сам проверит, что это валидный email
    password: str    # Пароль в чистом виде (позже мы его захэшируем)

# Схема для выдачи пользователя наружу (чтобы не отдавать пароль, возвращаем только безопасные данные)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # Позволяет Pydantic читать данные прямо из SQLAlchemy-моделей