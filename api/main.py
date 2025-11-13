# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Routers oficiales
from api.routes.m1_interaccion import router as m1_router
from api.routes.m2_creacion import router as m2_router
from api.routes.m3_entrega import router as m3_router
from api.routes.m4_evolucion import router as m4_router



# ==========================
# Logging
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AUTOMA")


# ==========================
# Lifespan
# ==========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando Centro de Capacitación Ultra-Automatizado")
    yield
    logger.info("🛑 Apagando servicio AUTOMA")


# ==========================
# App única
# ==========================
app = FastAPI(
    title="Centro de Capacitación Ultra-Automatizado",
    description="""
    Sistema de Macroprocesos:
    - M1: Interacción y recolección de requerimientos
    - M2: Creación del curso
    - M3: Entrega y administración automatizada
    
    """,
    version="1.0.0",
    lifespan=lifespan
)


# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# Routers reales por macroproceso
# ==========================
app.include_router(m1_router, prefix="/m1", tags=["Macroproceso 1"])
app.include_router(m2_router, prefix="/m2", tags=["Macroproceso 2"])
app.include_router(m3_router, prefix="/m3", tags=["Macroproceso 3"])
app.include_router(m4_router, prefix="/m4", tags=["Macroproceso 4"])



# ==========================
# Health global
# ==========================
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AUTOMA", "version": "1.0.0"}


# ==========================
# Runner
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
