# api/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =============== Importar Routers ==================
from api.routes.m1_interaccion import router as m1_router
from api.routes.m2_creacion import router as m2_router
from api.routes.m3_entrega import router as m3_router
from api.routes.m4_evolucion import router as m4_router
from api.routes.auth_routes import router as auth_router
from api.routes.user_routes import router as user_router

# =============== Base de Datos =====================
from api.config.database import Base, engine
from api.models import lms   # IMPORTANTE: para crear el LMS
from api.models import user as user_models  # crea tablas de usuarios


# ====================================================
#  LOGGING PROFESIONAL
# ====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("CUA_BACEND")


# ====================================================
#  CREACIÓN DE TABLAS
# ====================================================
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✔ Tablas creadas correctamente en la base de datos")
except Exception as e:
    logger.error("❌ Error creando tablas: %s", e)


# ====================================================
#  INSTANCIA FASTAPI
# ====================================================
app = FastAPI(
    title="Centro de Capacitación Ultra-Automatizado",
    version="2.0.0",
    description="Backend con orquestación de IA: M1, M2, M3, M4",
)


# ====================================================
#  CONFIGURACIÓN DE CORS
# ====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir luego en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====================================================
#  REGISTRO DE ROUTERS
# ====================================================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])

# Macroprocesos
app.include_router(m1_router, prefix="/m1", tags=["Macroproceso 1"])
app.include_router(m2_router, prefix="/m2", tags=["Macroproceso 2"])
app.include_router(m3_router, prefix="/m3", tags=["Macroproceso 3"])
app.include_router(m4_router, prefix="/m4", tags=["Macroproceso 4"])


# ====================================================
#  ENDPOINTS BÁSICOS
# ====================================================
@app.get("/")
def root():
    return {
        "message": "CUA Backend funcionando correctamente",
        "version": "2.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CUA Backend",
        "version": "2.0.0"
    }


# ====================================================
#  EJECUCIÓN UVICORN
# ====================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
