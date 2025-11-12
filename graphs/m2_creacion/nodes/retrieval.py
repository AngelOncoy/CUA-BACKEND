# graphs/m2_creacion/nodes/retrieval.py
from typing import Dict, Any, List
import os, json, re
import google.generativeai as genai

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TEMPERATURE = 0.0  # bajar alucinación

PROMPT = """Eres experto en diseño instruccional y en el tema: "{topic}".
Genera contenido didáctico en ESPAÑOL, SIN citar fuentes ni URLs.
Devuelve SOLO JSON válido (sin ``` ni etiquetas), respetando exactamente este esquema y mínimos:

{{
  "overview": "2–3 párrafos introductorios (máx 900 caracteres)",
  "key_points": ["bullet 1","bullet 2","bullet 3","bullet 4"],
  "procedures": [
    {{"title":"Procedimiento 1","steps":["Paso 1","Paso 2","Paso 3"]}},
    {{"title":"Procedimiento 2","steps":["Paso 1","Paso 2","Paso 3"]}}
  ],
  "pitfalls": ["error frecuente 1","error frecuente 2","error frecuente 3"],
  "examples": [
    {{"title":"Ejemplo 1","description":"qué se hace y por qué"}},
    {{"title":"Ejemplo 2","description":"qué se hace y por qué"}}
  ],
  "glossary": [
    {{"term":"Término 1","definition":"Definición breve"}},
    {{"term":"Término 2","definition":"Definición breve"}},
    {{"term":"Término 3","definition":"Definición breve"}}
  ],
  "faq": [
    {{"q":"Pregunta frecuente 1","a":"Respuesta breve y clara"}},
    {{"q":"Pregunta frecuente 2","a":"Respuesta breve y clara"}},
    {{"q":"Pregunta frecuente 3","a":"Respuesta breve y clara"}}
  ]
}}

Reglas:
- NO uses bloques ``` ni etiquetas como ```json.
- NO inventes números/versiones específicas. Si algo depende del contexto, dilo (“depende del conector”).
- Mantén español neutro y técnico cuando corresponda.
- No agregues campos extra ni comentarios.

Tema: {topic}
Subtemas orientadores: {subtopics}
"""

def _coerce_json(text: str) -> dict:
    """
    Intenta limpiar y parsear JSON devuelto por el modelo:
    - Elimina fences ``` y etiquetas.
    - Recorta texto antes/después del primer objeto JSON si vienen notas.
    - Corrige comas colgantes simples.
    """
    t = (text or "").strip()

    # quitar backticks y etiquetas
    t = t.replace("```json", "").replace("```", "").strip()

    # extraer primer bloque {...} si el modelo envolvió con texto
    # heurística simple: encontrar el primer '{' y el último '}' válido
    first = t.find("{")
    last = t.rfind("}")
    if first != -1 and last != -1 and last > first:
        t = t[first:last+1].strip()

    # quitar comas colgantes antes de ] o }
    t = re.sub(r",\s*(\]|\})", r"\1", t)

    # parseo final
    return json.loads(t)

def _mk_subtopics(titulo_modulo: str) -> List[str]:
    base = titulo_modulo.replace("Modulo", "Módulo")
    return [
        f"Panorama de {base}",
        f"Buenas prácticas de {base}",
        f"Casos de uso y ejemplos de {base}",
        f"Errores frecuentes en {base}",
        f"Procedimientos clave en {base}"
    ]

def _get_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Falta GOOGLE_API_KEY en el entorno")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=DEFAULT_MODEL,
        generation_config={"temperature": TEMPERATURE}
    )

def _synthesize(model, topic: str, subtopics: List[str]) -> Dict[str, Any]:
    prompt = PROMPT.format(topic=topic[:300], subtopics=subtopics[:800])
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    try:
        data = _coerce_json(text)
    except Exception:
        # Si falla, devolvemos overview con el bruto y listas vacías
        data = {"overview": text}

    # sane defaults
    data.setdefault("overview", "")
    data.setdefault("key_points", [])
    data.setdefault("procedures", [])
    data.setdefault("pitfalls", [])
    data.setdefault("examples", [])
    data.setdefault("glossary", [])
    data.setdefault("faq", [])

    # --- Validaciones mínimas y arreglos suaves ---
    # key_points >= 4
    if not isinstance(data["key_points"], list):
        data["key_points"] = []
    while len(data["key_points"]) < 4:
        data["key_points"].append("Punto clave adicional")

    # procedures >= 2, cada uno con ≥3 pasos
    if not isinstance(data["procedures"], list):
        data["procedures"] = []
    while len(data["procedures"]) < 2:
        data["procedures"].append({"title": "Procedimiento adicional", "steps": ["Paso 1","Paso 2","Paso 3"]})
    for p in data["procedures"]:
        p.setdefault("title", "Procedimiento")
        steps = p.get("steps")
        if not isinstance(steps, list):
            steps = []
        while len(steps) < 3:
            steps.append("Paso adicional")
        p["steps"] = steps

    # pitfalls >= 3
    if not isinstance(data["pitfalls"], list):
        data["pitfalls"] = []
    while len(data["pitfalls"]) < 3:
        data["pitfalls"].append("Riesgo/Problema a considerar")

    # examples >= 2
    if not isinstance(data["examples"], list):
        data["examples"] = []
    while len(data["examples"]) < 2:
        data["examples"].append({"title":"Ejemplo adicional","description":"Descripción breve"})
    for e in data["examples"]:
        e.setdefault("title", "Ejemplo")
        e.setdefault("description", "Descripción breve")

    # glossary >= 3
    if not isinstance(data["glossary"], list):
        data["glossary"] = []
    while len(data["glossary"]) < 3:
        data["glossary"].append({"term":"Término","definition":"Definición breve"})
    for g in data["glossary"]:
        g.setdefault("term", "Término")
        g.setdefault("definition", "Definición breve")

    # faq >= 3
    if not isinstance(data["faq"], list):
        data["faq"] = []
    while len(data["faq"]) < 3:
        data["faq"].append({"q":"Pregunta frecuente","a":"Respuesta breve"})
    for q in data["faq"]:
        q.setdefault("q", "Pregunta frecuente")
        q.setdefault("a", "Respuesta breve")

    # recorte suave del overview (por si el modelo se extiende)
    data["overview"] = (data["overview"] or "")[:1200]

    return data

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Closed-book: sintetiza conocimiento por módulo SIN web.
    Guarda en state['assets'] una ficha por módulo:
      { modulo, synthesis: {...}, referencias: [] }
    """
    syllabus = state.get("syllabus_detallado", {})
    model = _get_model()
    assets: List[Dict[str, Any]] = []

    for m in syllabus.get("modulos", []):
        titulo_mod = m.get("titulo", "Módulo sin título")
        subs = _mk_subtopics(titulo_mod)
        synthesis = _synthesize(model, titulo_mod, subs)

        assets.append({
            "modulo": titulo_mod,
            "queries_sugeridas": subs,  # solo orientativas
            "synthesis": synthesis,
            "referencias": []           # compatibilidad con etapas siguientes
        })

    state["assets"] = assets
    return state