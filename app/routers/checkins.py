from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.checkin import CheckIn
from app.models.user import User
from app.schemas.checkin import CheckInCreate, CheckInResponse

router = APIRouter(prefix="/checkins", tags=["Check-ins"])


@router.post("/", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(
    data: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать чек-ин для текущего пользователя."""
    checkin = CheckIn(user_id=current_user.id, **data.model_dump())
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/", response_model=list[CheckInResponse])
def list_checkins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Все чек-ины текущего пользователя, от новых к старым."""
    return (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id)
        .order_by(CheckIn.id.desc())
        .all()
    )


@router.get("/{checkin_id}", response_model=CheckInResponse)
def get_checkin(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Одна запись. Чужая запись даёт 404, как и несуществующая."""
    record = (
        db.query(CheckIn)
        .filter(CheckIn.id == checkin_id, CheckIn.user_id == current_user.id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkin(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить свою запись. Чужая или несуществующая даёт 404."""
    record = (
        db.query(CheckIn)
        .filter(CheckIn.id == checkin_id, CheckIn.user_id == current_user.id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(record)
    db.commit()
    return None
