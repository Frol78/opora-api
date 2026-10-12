from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя."""
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован."
        )
    
    # Создаем нового пользователя с хешированным паролем
    hashed_password = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, password_hash=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    """Вход пользователя и выдача JWT-токена."""
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == user_in.email).first()
    
    # Если пользователя нет или пароль неверный — возвращаем ошибку 401
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Генерируем JWT-токен (в качестве sub (subject) записываем id пользователя)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }