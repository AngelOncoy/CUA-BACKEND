# api/routes/m4_evolucion.py

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from graphs.central_graph import build_m4_graph

# OJO: aquí NO usamos prefix="/m4"
# porque el prefix ya lo pone api/main.py al incluir el router.
router = APIRouter()


class M4Request(BaseModel):
    """
    Payload de entrada para el Macroproceso 4.
    Por ahora solo usamos course_id opcional.
    Más adelante puedes agregar más campos si los necesitas.
    """
    course_id: Optional[str] = None


@router.post("/run", summary="Ejecutar Macroproceso 4 (Evolución de contenido)")
def run_m4(request: M4Request) -> Dict[str, Any]:
    """
    Ejecuta el grafo completo del Macroproceso 4 usando build_m4_graph()
    definido en graphs/central_graph.py y devuelve el estado final.
    """
    # Construimos el grafo de M4
    app = build_m4_graph()

    # Estado inicial mínimo
    initial_state: Dict[str, Any] = {}
    if request.course_id is not None:
        initial_state["course_id"] = request.course_id

    # Ejecutamos TODO el flujo de M4
    final_state = app.invoke(initial_state)

    return final_state
