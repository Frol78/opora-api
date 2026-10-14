import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("sub")
        token_version = payload.get("tver")
        
        if user_id is None or token_version is None:
            raise error
    except jwt.InvalidTokenError:
        raise error

    user = db.get(User, int(user_id))
    if user is None:
        raise error
        
    # Если версия токена в базе изменилась (например, после смены пароля), токен больше недействителен
    if user.token_version != token_version:
        raise error

    return user