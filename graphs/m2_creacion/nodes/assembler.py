from typing import Dict, Any, List
import json, hashlib, os
from datetime import datetime
from core.normalize import dump_canonical_state

# --- NUEVO: Importamos el gestor de memoria ---
from services.vector_manager import VectorManager

def _sha1(obj: Any) -> str:
    """Devuelve un hash SHA1 del paquete para control de integridad."""
    b = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(b).hexdigest()

def _vectorize_course(course_data: Dict[str, Any], vector_manager: VectorManager):
    """
    Desglosa el curso en fragmentos (chunks) y los guarda en la Vector Store
    para que el Macroproceso 4 pueda 'razonar' sobre el contenido final.
    """
    texts_to_index = []
    metadatas = []
    
    curso_titulo = course_data.get("titulo", "Curso")
    print(f"   -> Vectorizando curso: {curso_titulo}...")

    # 1. Indexar Módulos
    for idx_m, mod in enumerate(course_data.get("modulos", [])):
        mod_titulo = mod.get("titulo", "")
        # Resumen del módulo
        texts_to_index.append(f"CURSO: {curso_titulo}\nMÓDULO: {mod_titulo}\nRESUMEN: {mod.get('resumen', '')}")
        metadatas.append({
            "source": "assembler_m2",
            "type": "module_overview",
            "course": curso_titulo,
            "module": mod_titulo
        })

        # 2. Indexar Lecciones
        for idx_l, lec in enumerate(mod.get("lecciones", [])):
            lec_titulo = lec.get("titulo", "")
            contenido = lec.get("contenido", {})
            
            # Convertimos contenido a texto plano para búsqueda
            intro = contenido.get("introduccion", "")
            conceptos = ", ".join(contenido.get("conceptos_clave", [])) if isinstance(contenido.get("conceptos_clave"), list) else str(contenido.get("conceptos_clave"))
            
            full_text = (
                f"CURSO: {curso_titulo}\n"
                f"MÓDULO: {mod_titulo}\n"
                f"LECCIÓN: {lec_titulo}\n"
                f"INTRO: {intro}\n"
                f"CONCEPTOS: {conceptos}"
            )
            
            texts_to_index.append(full_text)
            metadatas.append({
                "source": "assembler_m2",
                "type": "lesson_content",
                "course": curso_titulo,
                "module": mod_titulo,
                "lesson": lec_titulo
            })

    # Guardar en lotes si hay algo que guardar
    if texts_to_index:
        vector_manager.add_texts(texts=texts_to_index, metadatas=metadatas)
        print(f"   -> {len(texts_to_index)} fragmentos indexados en Vector Store.")

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensambla el paquete final del M2.
    """
    print("--- ASSEMBLER: EMPAQUETANDO Y GUARDANDO ---")
    curso = state.get("curso_m2_multimedia") or state.get("curso_m2")
    evaluaciones = state.get("evaluaciones_m2", {})
    calidad = state.get("control_calidad_m2", {})
    objetivos = state.get("objetivos_m2", {})

    if not curso:
        raise ValueError("Falta curso_m2 o curso_m2_multimedia en el estado.")
    if not evaluaciones:
        raise ValueError("Faltan evaluaciones_m2.")
    if not calidad:
        raise ValueError("Falta control_calidad_m2.")

    # 1. Creación del Manifiesto (Tu lógica original)
    manifest = {
        "nombre_paquete": curso.get("titulo", "Curso generado"),
        "nivel": curso.get("nivel", "Avanzado"),
        "modulos": len(curso.get("modulos", [])),
        "lecciones": sum(len(m.get("lecciones", [])) for m in curso.get("modulos", [])),
        "evaluaciones": sum(len(m.get("quiz", {}).get("items", [])) for m in evaluaciones.get("modulos", [])),
        "score_calidad": calidad.get("resumen", {}).get("score_global"),
        "generado_en": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

    files = {
        "curso.json": curso,
        "evaluaciones.json": evaluaciones,
        "calidad.json": calidad
    }
    if objetivos:
        files["objetivos.json"] = objetivos

    # Extra: prompts multimedia
    media_prompts = []
    for m in curso.get("modulos", []):
        for l in m.get("lecciones", []):
            for asset in (l.get("multimedia") or []):
                media_prompts.append({
                    "modulo": m.get("titulo"),
                    "leccion": l.get("titulo"),
                    "tipo": asset.get("tipo"),
                    "prompt": asset.get("prompt"),
                    "descripcion": asset.get("descripcion"),
                })
    files["media_prompts.json"] = media_prompts

    paquete = {
        "manifest": manifest,
        "files": files,
        "bundle_hash": _sha1({"manifest": manifest, "files": files})
    }

    state["paquete_m2"] = paquete

    # Identificador de corrida
    run_id = (
        state.get("run_id")
        or (state.get("input") or {}).get("run_id")
        or "manual_run"
    )

    # === NUEVO: Integración para M4 (Memoria Física) ===
    # Guardamos el JSON limpio en una ruta conocida para que M4 lo cargue
    output_dir = os.path.join("data", "outputs", run_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardamos curso completo y el paquete
    curso_path = os.path.join(output_dir, "curso_final.json")
    with open(curso_path, "w", encoding="utf-8") as f:
        json.dump(curso, f, indent=2, ensure_ascii=False)
    
    state["curso_final_path"] = curso_path # Referencia para M4
    print(f"   -> Backup físico guardado en: {curso_path}")

    # === NUEVO: Integración para M4 (Memoria Semántica) ===
    try:
        vm = VectorManager()
        _vectorize_course(curso, vm)
    except Exception as e:
        print(f"   ⚠️ Error indexando en Vector Store (no crítico): {e}")

    # === Export canónico original ===
    export_cfg = (state.get("config") or {}).get("export") or {}
    write_canonical = export_cfg.get("write_canonical", True)
    out_dir = export_cfg.get("dir", "runs")

    if write_canonical:
        path = os.path.join(out_dir, run_id, "08_assembler.canonical.json")
        dump_canonical_state(state, path)
        
    return state