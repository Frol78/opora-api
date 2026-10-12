from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Схема для создания чек-ина (данные от пользователя)
class CheckInCreate(BaseModel):
    mood: int = Field(..., ge=1, le=10, description="Настроение от 1 до 10")
    craving: int = Field(..., ge=0, le=10, description="Уровень тяги от 0 до 10")
    note: str = Field(default="", max_length=1000, description="Заметка")

# Схема для ответа клиенту (что мы возвращаем при запросе чек-инов)
class CheckInResponse(BaseModel):
    id: int
    user_id: int
    mood: int
    craving: int
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)