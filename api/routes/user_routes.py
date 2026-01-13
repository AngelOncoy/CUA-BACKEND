from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.config.database import get_db
from api.models.user import User

router = APIRouter()


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(name=name, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

