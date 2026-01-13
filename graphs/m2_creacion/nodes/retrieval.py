import os
import json
import re
from typing import Dict, Any, List

import google.generativeai as genai
from langchain_community.utilities import SerpAPIWrapper

# --- CAMBIO AQUÍ: Importamos desde services ---
from services.vector_manager import VectorManager

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
TEMPERATURE = 0.2

# Prompt RAG
RAG_PROMPT = """Eres un experto diseñador instruccional. Tienes el siguiente CONTEXTO RECUPERADO de fuentes expertas:

CONTEXTO:
{context}

INSTRUCCIÓN:
Usando EXCLUSIVAMENTE el contexto anterior (y tu conocimiento general solo para llenar vacíos obvios), genera el contenido didáctico para el tema: "{topic}".
Debes devolver un JSON válido con la siguiente estructura exacta:

{{
  "overview": "Resumen técnico basado en el contexto (máx 1000 chars)",
  "key_points": ["Punto clave 1", "Punto clave 2", "Punto clave 3", "Punto clave 4"],
  "procedures": [
    {{"title":"Nombre del procedimiento","steps":["Paso 1","Paso 2","Paso 3"]}}
  ],
  "pitfalls": ["Error común 1", "Error común 2", "Error común 3"],
  "examples": [
    {{"title":"Ejemplo práctico","description":"Descripción basada en el contexto"}}
  ],
  "glossary": [
    {{"term":"Término","definition":"Definición"}}
  ],
  "faq": [
    {{"q":"Pregunta","a":"Respuesta"}}
  ]
}}

IMPORTANTE:
- Responde SOLO JSON válido.
- NO incluyas markdown (```json).
"""

def _coerce_json(text: str) -> dict:
    t = (text or "").strip().replace("```json", "").replace("```", "").strip()
    first, last = t.find("{"), t.rfind("}")
    if first != -1 and last != -1 and last > first:
        t = t[first:last+1].strip()
    t = re.sub(r",\s*(\]|\})", r"\1", t)
    try:
        return json.loads(t)
    except:
        return {}

def _get_search_results(query: str) -> List[str]:
    try:
        search = SerpAPIWrapper()
        results = search.results(query)
        snippets = []
        if "organic_results" in results:
            for r in results["organic_results"]:
                snippets.append(f"Fuente: {r.get('title')}\nInfo: {r.get('snippet')}\nLink: {r.get('link')}")
        return snippets
    except Exception as e:
        print(f"Error en búsqueda '{query}': {e}")
        return []

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    syllabus = state.get("syllabus_detallado", {})
    
    # Instanciamos el nuevo VectorManager desde services
    vector_manager = VectorManager()
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(
        model_name=DEFAULT_MODEL,
        generation_config={"temperature": TEMPERATURE}
    )
    
    assets: List[Dict[str, Any]] = []

    print("--- INICIANDO RETRIEVAL & VECTOR STORE ---")

    for m in syllabus.get("modulos", []):
        titulo_mod = m.get("titulo", "Tema General")
        print(f"Procesando: {titulo_mod}")
        
        # 1. Búsqueda Web
        search_query = f"{titulo_mod} tutorial guía mejores prácticas errores comunes"
        snippets = _get_search_results(search_query)
        
        # 2. Guardar en Vector Store (Services)
        if snippets:
            print(f"  -> Indexando {len(snippets)} fragmentos...")
            vector_manager.add_texts(
                texts=snippets,
                metadatas=[{"source": "serpapi", "module": titulo_mod} for _ in snippets]
            )

        # 3. Recuperar Contexto (RAG)
        docs = vector_manager.similarity_search(titulo_mod, k=5)
        context_str = "\n\n".join([d.page_content for d in docs])

        # 4. Generar con LLM + Contexto
        prompt_fmt = RAG_PROMPT.format(topic=titulo_mod, context=context_str[:5000])
        resp = model.generate_content(prompt_fmt)
        
        synthesis = _coerce_json(resp.text)
        
        # Fallback de seguridad
        if not synthesis.get("key_points"):
             synthesis["key_points"] = ["Punto clave (Generado por fallback)"]

        # Referencias para el frontend/reporte
        referencias = []
        for d in docs:
            referencias.append({"fuente": "Búsqueda Web", "titulo": d.page_content[:100] + "..."})

        assets.append({
            "modulo": titulo_mod,
            "queries_sugeridas": [search_query],
            "synthesis": synthesis,
            "referencias": referencias
        })

    state["assets"] = assets
    state["vector_store_ready"] = True
    print("--- RETRIEVAL FINALIZADO ---")
    
    return state