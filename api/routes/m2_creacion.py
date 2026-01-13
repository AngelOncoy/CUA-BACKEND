# api/routes/m2_creacion.py
from fastapi import APIRouter, HTTPException
from graphs.m2_creacion.graph import build_graph
from graphs.m2_creacion.schemas import M2Input
from graphs.m2_creacion.adapter import m1_to_m2_input
from services.course_storage import save_m2_course_to_db
import logging

router = APIRouter(prefix="/m2", tags=["m2_creacion"])
graph = build_graph()
logger = logging.getLogger(__name__)

@router.post("/run")
def run_m2(payload: dict, persist: bool = False):
    """
    Ejecuta el Macroproceso 2 (Creación de Cursos)
    
    Args:
        payload: Datos de entrada
          - Si incluye "entidades": se usa directamente como M2Input
          - Si no: se convierte desde output de M1 usando adapter
          - Puede incluir "company_id": ID de la empresa (opcional)
        persist: Si True, guarda el curso en la base de datos
    
    Returns:
        dict con:
          - ok: bool
          - result: output del grafo M2
          - course_id: ID del curso en DB (si persist=True)
    """
    try:
        if "entidades" in payload:
            m2in = M2Input(**payload)
        else:
            m2in = m1_to_m2_input(payload)

        state = {
            "input": m2in.model_dump(),
            "entidades": m2in.entidades.model_dump(),
        }
        result = graph.invoke(state)
        
        # Guardar en DB si persist=True
        course_id = None
        if persist and result:
            company_id = payload.get("company_id")
            try:
                course_id = save_m2_course_to_db(result, company_id)
                logger.info(f"✅ Curso persistido en DB con ID: {course_id}")
            except Exception as e:
                logger.error(f"⚠️  Error persistiendo curso: {e}")
                # No falla el request, solo logea el error
        
        return {
            "ok": True,
            "result": result,
            "course_id": course_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))