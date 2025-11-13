def extract_course_data_node(state):
    """
    NODO M4 — EXTRAER DATOS DEL CURSO
    Datos simulados porque no existe BD real.
    """
    data = {
        "curso_id": "CUR-2025-001",
        "participantes": 25,
        "duracion_horas": 10,
        "temas": ["IA aplicada", "Automatización", "Prompt Engineering"],
        "evaluacion_promedio": 4.7,
        "asistencia": 93,
        "dificultades_reportadas": ["prompts avanzados"],
        "feedback": "Curso altamente valorado por los alumnos"
    }

    return {"course_data": data}
