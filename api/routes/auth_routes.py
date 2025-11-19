from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.config.database import get_db
from api.models.user import User

router = APIRouter()


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.password != password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {"message": "Login correcto", "user_id": user.id}

