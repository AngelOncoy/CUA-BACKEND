from typing import Dict, Any


def extract_course_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — EXTRACT_COURSE_DATA

    Por ahora es un placeholder: simplemente devuelve el estado tal cual.
    Aquí luego puedes agregar la lógica real para extraer datos del curso
    (id del curso, módulos, métricas, historial, etc.).
    """
    # Ejemplo de cómo podrías ir rellenando en el futuro:
    #
    # course_id = state.get("course_id", "curso_demo")
    # course_data = {
    #     "id": course_id,
    #     "nombre": "Curso de IA Aplicada",
    #     "modulos": ["Introducción", "Prompts", "Casos prácticos"]
    # }
    #
    # state["course_data"] = course_data
    # return state
    #
    # Por ahora solo devolvemos el estado sin cambios:
    return state


def extract_course_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central (central_graph.py).

    El grafo M4 interno usa `extract_course_data_node`,
    mientras que el grafo central importa `extract_course_data`.
    Ambos llaman a la misma lógica para mantener consistencia.
    """
    return extract_course_data_node(state)
