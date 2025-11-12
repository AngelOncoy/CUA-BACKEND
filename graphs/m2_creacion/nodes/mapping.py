from typing import Dict, Any, List

def _mk_lecciones_basicas(titulo_modulo: str, horas: int) -> List[Dict[str, Any]]:
    # 1 lección por cada ~4 horas (mínimo 2)
    n = max(2, max(1, horas // 4))
    return [
        {
            "titulo": f"{titulo_modulo} - Lección {i+1}",
            "objetivo": f"Introducir y ejercitar conceptos clave ({i+1}) de {titulo_modulo}",
            "estimado_min": 30
        } for i in range(n)
    ]

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    # Lee módulos del input normalizado
    modulos = (state.get("input", {}).get("mapping", {}) or {}).get("modulos", [])
    syllabus = {"modulos": []}

    for idx, m in enumerate(modulos, start=1):
        titulo = m.get("titulo", f"Módulo {idx}")
        horas = int(m.get("horas", 4))
        unidades = [{
            "titulo": f"Unidad {idx}.1 - {titulo}",
            "descripcion": m.get("descripcion", ""),
            "lecciones": _mk_lecciones_basicas(titulo, horas)
        }]

        syllabus["modulos"].append({
            "titulo": titulo,
            "horas": horas,
            "unidades": unidades
        })

    state["syllabus_detallado"] = syllabus
    return state