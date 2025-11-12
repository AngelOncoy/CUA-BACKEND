from typing import Dict, Any
import json, hashlib, os
from datetime import datetime
from core.normalize import dump_canonical_state

def _sha1(obj: Any) -> str:
    """Devuelve un hash SHA1 del paquete para control de integridad."""
    b = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha1(b).hexdigest()

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensambla el paquete final del M2.
    Lee:
      - curso_m2_multimedia o curso_m2
      - evaluaciones_m2
      - control_calidad_m2
      - objetivos_m2 (opcional)
    Escribe:
      - paquete_m2 (con manifest, bundle_hash, y archivos listos)
    """
    curso = state.get("curso_m2_multimedia") or state.get("curso_m2")
    evaluaciones = state.get("evaluaciones_m2", {})
    calidad = state.get("control_calidad_m2", {})
    objetivos = state.get("objetivos_m2", {})

    if not curso:
        raise ValueError("Falta curso_m2 o curso_m2_multimedia en el estado. Ejecuta authoring/media antes.")
    if not evaluaciones:
        raise ValueError("Faltan evaluaciones_m2. Ejecuta assessments antes.")
    if not calidad:
        raise ValueError("Falta control_calidad_m2. Ejecuta qc antes.")

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

    # Extra: prompts multimedia individuales
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

    # === Export canónico opcional ===
    export_cfg = (state.get("config") or {}).get("export") or {}
    write_canonical = export_cfg.get("write_canonical", True)  # True por defecto
    out_dir = export_cfg.get("dir", "runs")                    # 'runs' por defecto

    # run_id robusto
    run_id = (
        state.get("run_id")
        or (state.get("input") or {}).get("run_id")
        or "graph"  # fallback cuando se ejecuta el grafo
    )

    if write_canonical:
        path = os.path.join(out_dir, run_id, "08_assembler.canonical.json")
        dump_canonical_state(state, path)
    return state