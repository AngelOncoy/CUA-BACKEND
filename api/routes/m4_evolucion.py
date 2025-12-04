from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from graphs.central_graph import build_graph

router = APIRouter()

# Build once
central_app = build_graph()

class M4Request(BaseModel):
    course_id: Optional[str] = None
    course_data: Optional[Dict[str, Any]] = None


@router.post("/run", summary="Ejecutar Macroproceso 4 (Evolución de contenido)")
async def run_m4(request: M4Request) -> Dict[str, Any]:
    """
    Ejecuta SOLO el Macroproceso 4 usando el grafo integrado (central_graph).
    Se dispara en el nodo M4_EXTRACT usando config={"start": "..."}.
    """

    initial_state = {
        "prompt_raw": "",
        "entidades": {},
        "confianza_nlp": 1.0,
        "requiere_clarificacion": False,
        "preguntas": [],
        "respuestas": [],
        "mapping": {},
        "syllabus": {},
        "precio": {},
        "propuesta_html": "",
        "decision": "",
        "metricas": {},
        "historial": [],

        # M3 placeholders (compatibilidad)
        "m3_publicado": False,
        "certificados": [],
        "gamificacion": {},
        "analytics": {},

        # M4
        "course_id": request.course_id,
        "course_data": request.course_data or {"mensaje": "curso sin data"},
        "prompts_analysis": {},
        "success_patterns": {},
        "gaps": [],
        "additional_content": [],
        "updated_content": {},
    }

    # 🔥 CORRECCIÓN CRUCIAL → usar config={"start": ...}
    final_state = await central_app.ainvoke(
        initial_state,
        config={"start": "M4_EXTRACT"}
    )

    return final_state
