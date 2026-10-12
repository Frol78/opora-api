# Импортируем типы колонок из SQLAlchemy
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
# Импортируем наш базовый класс Base из database.py
from app.database import Base

class User(Base):
    __tablename__ = "users"  # Имя таблицы в базе данных

    # Первичный ключ (уникальный ID пользователя)
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Email пользователя (строка до 255 символов, уникальный, с индексом для быстрого поиска)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Хеш пароля (мы никогда не храним сам пароль, только его безопасный хеш!)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Дата и время создания аккаунта (автоматически проставляется базой данных в UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связь "один ко многим": у одного пользователя может быть много чек-инов.
    # cascade="all, delete-orphan" означает: если мы удаляем пользователя, 
    # все его чек-ины тоже автоматически удаляются (право на забвение и приватность!).
    check_ins: Mapped[list["CheckIn"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )