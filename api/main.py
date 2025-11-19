# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
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
=======
# Usar importaciones consistentes apuntando al paquete 'api.routes'
from api.routes import m1_interaccion, health
from api.routes.m3_entrega import router as m3_router
from api.routes.publicacion import router as publicacion_router
from api.routes.gestion import router as gestion_router
from api.routes.monitoreo import router as monitoreo_router

import logging

# Si no vas a usar asynccontextmanager, no lo importes.
# from contextlib import asynccontextmanager

logger = logging.getLogger("uvicorn.error")

# Configuración básica de la app
app = FastAPI(title="AUTOMA Backend", version="1.0.0")

# CORS: en desarrollo permite todo, pero en producción especifica orígenes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto por una lista de orígenes en producción
>>>>>>> 566ced2 (Modificacones)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD

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
=======
# Incluye routers con prefijos y tags para mejor organización
# Ajusta los prefijos según tu API design
app.include_router(m1_interaccion.router, prefix="/m1", tags=["m1-interaccion"])
app.include_router(m3_router, prefix="/m3", tags=["m3-entrega"])
app.include_router(publicacion_router, prefix="/publicacion", tags=["publicacion"])
app.include_router(gestion_router, prefix="/gestion", tags=["gestion"])
app.include_router(monitoreo_router, prefix="/monitoreo", tags=["monitoreo"])
app.include_router(health.router, prefix="/health", tags=["health"])

@app.get("/")
async def root():
    return {"message": "CUA Backend funcionando correctamente"}

# Ejemplo de startup/shutdown simple (opcional)
@app.on_event("startup")
async def startup_event():
    logger.info("Starting AUTOMA Backend...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AUTOMA Backend...")

# Ejecutar con uvicorn de forma segura desde el mismo archivo.
if __name__ == "__main__":
    import uvicorn

    # Opción 1 (recomendada para ejecutar desde este archivo directamente):
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True, log_level="info")

    # Opción 2 (si prefieres ejecutar por módulo desde la raíz del proyecto):
    # uvicorn.run("api.main:app", host="0.0.0.0", port=8003, reload=True, log_level="info")
>>>>>>> 566ced2 (Modificacones)
