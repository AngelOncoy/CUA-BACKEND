# graphs/m2_creacion/nodes/notify_ready.py
from typing import Dict, Any
from datetime import datetime
import os, json
import requests

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _coalesce_webhook(state: Dict[str, Any]) -> str | None:
    # 1) config en el state
    url = ((state.get("config") or {}).get("notify") or {}).get("webhook_url")
    if url:
        return url
    # 2) variable de entorno
    return os.getenv("NOTIFY_WEBHOOK_URL")

def _safe_post(url: str, payload: dict, timeout: int = 8) -> Dict[str, Any]:
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "reason": r.reason,
            "text": r.text[:500]
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Notifica que el paquete del M2 quedó listo.
    Lee:
      - state['paquete_m2'] (REQUIRED)
    Usa opcionalmente:
      - state['config']['notify'] = { 'webhook_url'?, 'dry_run'?, 'extra'?: {...} }
      - env: NOTIFY_WEBHOOK_URL
    Escribe:
      - state['notificacion_m2'] con resultado del envío y copia del payload
    """
    pkg = state.get("paquete_m2")
    if not pkg:
        raise ValueError("Falta 'paquete_m2' en el estado. Ejecuta assembler antes.")

    manifest = pkg.get("manifest", {})
    files = list((pkg.get("files") or {}).keys())

    payload = {
        "event": "M2_PACKAGE_READY",
        "timestamp": _now_iso(),
        "course": {
            "name": manifest.get("package_name") or manifest.get("nombre_paquete"),
            "level": manifest.get("level") or manifest.get("nivel"),
            "modules": manifest.get("modules_count") or manifest.get("modulos"),
            "lessons": manifest.get("lecciones"),
        },
        "quality_score": manifest.get("quality_score") or manifest.get("score_calidad"),
        "assessments_items_total": manifest.get("assessments_items_total") or manifest.get("evaluaciones"),
        "bundle_hash": pkg.get("bundle_hash"),
        "files": files,
        "extra": ((state.get("config") or {}).get("notify") or {}).get("extra")
    }

    # Config
    cfg = (state.get("config") or {}).get("notify") or {}
    dry_run = bool(cfg.get("dry_run", False))
    webhook = _coalesce_webhook(state)

    # 1) Siempre persistimos el payload en el estado
    result = {"local": "saved", "webhook": None, "dry_run": dry_run, "webhook_url": webhook}

    # 2) Webhook (si hay y no es dry-run)
    if webhook and not dry_run:
        result["webhook"] = _safe_post(webhook, payload)
    elif webhook and dry_run:
        result["webhook"] = {"ok": True, "skipped": True, "reason": "dry_run"}

    # 3) Impresión legible (útil en CI / logs)
    print("\n=== NOTIFY READY (M2) ===")
    print(f"Curso: {payload['course']['name']} | Nivel: {payload['course']['level']}")
    print(f"Módulos: {payload['course']['modules']} | Lecciones: {payload['course']['lessons']}")
    print(f"Quality score: {payload['quality_score']} | Quiz items: {payload['assessments_items_total']}")
    print(f"Bundle hash: {payload['bundle_hash']}")
    if webhook:
        print(f"Webhook: {webhook} | Enviado: {not dry_run}")
        if result["webhook"] and result["webhook"].get("ok") is False:
            print("Webhook error:", result["webhook"])

    state["notificacion_m2"] = {
        "payload": payload,
        "result": result
    }
    return state