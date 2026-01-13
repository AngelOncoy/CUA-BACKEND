# graphs/m3_entrega/nodes/utils.py

import os
from datetime import datetime
from typing import Dict, Any


def load_prompt(filename: str) -> str:
    """
    Carga un archivo de prompt desde la carpeta 'prompts'
    ubicada en el mismo directorio que este módulo.
    """
    base_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(base_dir, "prompts", filename)

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback: si no se encuentra, devolvemos un texto mínimo
        return f"[WARNING] Prompt file '{filename}' not found."


def inicializar_estado(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inicializa el estado con valores por defecto y normaliza campos.
    Convierte nomenclatura de API (español) a nomenclatura de nodos (inglés).
    """
    # Timestamp de inicio
    state["timestamp_inicio"] = datetime.utcnow().isoformat()
    
    # Normalizar campos (API -> nodos)
    if "curso_id" in state and "course_id" not in state:
        state["course_id"] = state["curso_id"]
    
    if "cliente_id" in state and "company_id" not in state:
        state["company_id"] = state["cliente_id"]
    
    if "empleados" in state and "employees" not in state:
        state["employees"] = state["empleados"]
    
    # Inicializar campos opcionales con valores por defecto
    state.setdefault("errors", [])
    state.setdefault("curso_publicado", False)
    state.setdefault("notificacion_enviada", False)
    state.setdefault("gamificacion_activa", False)
    state.setdefault("asignaciones_completadas", False)
    state.setdefault("analytics", {})
    state.setdefault("analytics_dashboard", {})
    state.setdefault("certificados_emitidos", [])
    state.setdefault("certificates", [])
    state.setdefault("empleados_asignados", [])
    state.setdefault("enrollment_ids", [])
    
    return state
