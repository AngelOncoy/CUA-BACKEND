#!/bin/bash

echo "=== INICIANDO PARCHE PARA CUA-BACKEND ==="

##############################################
# 1. Corrección de api/main.py
##############################################

cat > api/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.user_routes import router as UserRouter
from api.routes.auth_routes import router as AuthRouter
from api.config.database import engine, Base

app = FastAPI(title="CUA API", version="1.0.0")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(UserRouter, prefix="/users", tags=["Users"])
app.include_router(AuthRouter, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "CUA Backend funcionando correctamente"}
EOF

echo "[OK] main.py corregido"


##############################################
# 2. Corrección de api/config/database.py
##############################################

cat > api/config/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

echo "[OK] database.py corregido"


##############################################
# 3. Corrección del modelo User
##############################################

cat > api/models/user.py << 'EOF'
from sqlalchemy import Column, Integer, String, Boolean
from api.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
EOF

echo "[OK] Modelo User corregido"


##############################################
# 4. Corrección de user_routes
##############################################

cat > api/routes/user_routes.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models.user import User
from api.config.database import get_db

router = APIRouter()

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/")
def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email ya está registrado")

    new_user = User(name=name, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
EOF

echo "[OK] user_routes corregido"


##############################################
# 5. Corrección de auth_routes
##############################################

cat > api/routes/auth_routes.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models.user import User
from api.config.database import get_db

router = APIRouter()

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.password != password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {"message": "Login correcto", "user_id": user.id}
EOF

echo "[OK] auth_routes corregido"


##############################################
# 6. Crear __init__.py en carpetas necesarias
##############################################

touch api/__init__.py
touch api/routes/__init__.py
touch api/models/__init__.py
touch api/config/__init__.py

echo "[OK] Archivos __init__.py agregados"


##############################################
# FIN DEL PARCHE
##############################################

echo "=== PARCHE COMPLETADO. Proyecto reparado ==="
