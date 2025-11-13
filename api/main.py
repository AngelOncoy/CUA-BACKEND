# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import m1_interaccion, health
from routes.m3_entrega import router as m3_router
from routes.publicacion import router as publicacion_router
from routes.gestion import router as gestion_router
from routes.monitoreo import router as monitoreo_router
import logging
from contextlib import asynccontextmanager

app = FastAPI(title="AUTOMA Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

app.include_router(health.router, tags=["Health"])
app.include_router(m1_interaccion.router, prefix="/m1", tags=["Macroproceso 1"])

@app.get("/")
def root():
    return {"status": "ok", "message": "AUTOMA backend corriendo correctamente"}


app = FastAPI(title="Macroproceso 3 API")

app.include_router(m3_router)
app.include_router(publicacion_router)
app.include_router(gestion_router)
app.include_router(monitoreo_router)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("🚀 Iniciando Macroproceso 3: Entrega y Administración")
    logger.info("=" * 60)
    yield
    logger.info("🛑 Cerrando Macroproceso 3")


# Crear aplicación FastAPI
app = FastAPI(
    title="Centro de Capacitación Ultra-Automatizado - Macroproceso 3",
    description="""
    Sistema de Entrega y Administración del Aprendizaje completamente automatizado.
    
    ## Procesos Automatizados:
    
    ### 3.1 Publicación y Comunicación
    - Publicación automática en LMS
    - Notificación inmediata por email
    
    ### 3.2 Gestión del Aprendizaje
    - Asignación automática de empleados
    - Sistema de gamificación integrado
    
    ### 3.3 Monitoreo y Evaluación
    - Dashboard de analytics en tiempo real
    - Emisión automática de certificaciones digitales
    
    ## Métricas Objetivo:
    - Tiempo de entrega tras pago: **inmediato - 5 minutos**
    - Tasa de finalización de cursos: **65-75%**
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar y registrar rutas
from api.routes.m3_entrega import router as m3_router

app.include_router(m3_router)


@app.get("/")
async def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "Macroproceso 3: Entrega y Administración del Aprendizaje",
        "version": "1.0.0",
        "status": "operational",
        "description": "Sistema automatizado de publicación, asignación y monitoreo de cursos",
        "endpoints": {
            "iniciar_entrega": "/m3/iniciar",
            "consultar_progreso": "/m3/consultar-progreso",
            "actualizar_analytics": "/m3/actualizar-analytics/{run_id}",
            "health": "/m3/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check general"""
    return {
        "status": "healthy",
        "service": "m3-entrega",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )