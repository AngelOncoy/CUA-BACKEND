from typing import Dict, Any, List
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def _get_model():
    """Carga el modelo de Gemini si hay API_KEY"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GOOGLE_API_KEY en el entorno para generar multimedia")
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(model_name=model_name)

def _mk_prompts_from_lesson(lesson: Dict[str, Any]) -> List[str]:
    prompts = []
    conceptos = lesson.get("contenido", {}).get("conceptos_clave", [])
    ejemplos = lesson.get("contenido", {}).get("ejemplos", [])
    if conceptos:
        prompts.append(f"Infografía explicativa sobre: {conceptos[0]}")
    if ejemplos:
        prompts.append(f"Imagen representando el ejemplo: {ejemplos[0].get('titulo','ejemplo práctico')}")
    if not prompts:
        prompts.append(f"Imagen conceptual ilustrando la temática de la lección: {lesson.get('titulo')}")
    return prompts[:3]

def _describe_assets(model, prompts: List[str]) -> List[Dict[str, str]]:
    assets = []
    for p in prompts:
        try:
            prompt = f"Genera una breve descripción de un recurso visual o multimedia para: {p}. Devuelve solo texto corto."
            resp = model.generate_content(prompt)
            desc = (resp.text or "").strip().replace("```", "")
            assets.append({
                "tipo": "imagen",
                "prompt": p,
                "descripcion": desc[:300],
                "url": None
            })
        except Exception as e:
            assets.append({
                "tipo": "imagen",
                "prompt": p,
                "descripcion": f"Descripción no generada ({e})",
                "url": None
            })
    return assets

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agrega descripciones multimedia a cada lección del curso.
    Lee: state['curso_m2']
    Escribe: state['curso_m2_multimedia']
    """
    curso = state.get("curso_m2", {})
    if not curso:
        raise ValueError("Falta curso_m2 en el estado. Ejecuta authoring antes.")

    model = _get_model()

    nuevo_curso = curso.copy()
    for m in nuevo_curso.get("modulos", []):
        for l in m.get("lecciones", []):
            prompts = _mk_prompts_from_lesson(l)
            multimedia = _describe_assets(model, prompts)
            l["multimedia"] = multimedia

    state["curso_m2_multimedia"] = nuevo_curso
    return state