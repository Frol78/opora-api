from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


def _check_bytes(value: str) -> str:
    # bcrypt использует только первые 72 байта, кириллица занимает 2 байта на символ
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Пароль не длиннее 72 байт (около 36 кириллических символов)")
    return value


class RegisterIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return _check_bytes(value)


class PasswordChangeIn(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def new_password_fits_bcrypt(cls, value: str) -> str:
        return _check_bytes(value)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    """Регистрация. Пароль хранится только в виде хеша."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Этот email уже занят")

    user = User(email=data.email, password_hash=get_password_hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Вход в форме OAuth2: поле username содержит email.
    Swagger «Authorize» отправляет именно такой формат.
    """
    user = db.query(User).filter(User.email == form.username).first()
    # Одинаковое сообщение для неверного email и пароля
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/change-password")
def change_password(
    data: PasswordChangeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Смена пароля. Нужны токен и текущий пароль."""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Текущий пароль неверный")

    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="Новый пароль должен отличаться от старого")

    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Пароль изменён"}