from sqlalchemy import ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

class CheckIn(Base):
    __tablename__ = "check_ins"  # Имя таблицы в базе данных

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Внешний ключ: ссылается на id в таблице users. 
    # База данных не разрешит создать чек-ин для несуществующего пользователя.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Настроение (например, от 1 до 10)
    mood: Mapped[int] = mapped_column(Integer)
    
    # Уровень тяги/желания сорваться (например, от 0 до 10)
    craving: Mapped[int] = mapped_column(Integer)
    
    # Текстовая заметка (до 1000 символов, по умолчанию пустая строка)
    note: Mapped[str] = mapped_column(String(1000), default="")
    
    # Время создания записи
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Обратная связь с пользователем (позволяет писать check_in.user)
    user: Mapped["User"] = relationship(back_populates="check_ins")