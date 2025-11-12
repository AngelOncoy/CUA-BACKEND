import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import notify  # 👈 coincide con tu archivo notify.py

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_notify_from_assembler_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")
    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)

    # debería apuntar a 08_assembler.state.json
    state_path = baton["last_state"]
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Configuración de notificación (evita llamadas reales)
    state.setdefault("config", {})
    state["config"]["notify"] = {
        "dry_run": True,             # deja True para no enviar webhook real
        # "webhook_url": "https://tu.endpoint/webhook",  # si quisieras probarlo
        "extra": {"owner": "Totty", "macroproceso": "M2"}
    }

    # ✅ Ejecutar el nodo notify
    state = notify.run(state)

    # Guardar salida y baton
    out_path = os.path.join(rdir, "09_notify.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    # Snapshot legible
    payload = state["notificacion_m2"]["payload"]
    payload_path = os.path.join(rdir, "09_notify.payload.txt")
    with open(payload_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))

    print("\n=== NOTIFY (FINAL M2) ===")
    print("Evento:", payload.get("event"))
    print("Curso:", payload["course"]["name"])
    print("Webhook (dry-run):", state["notificacion_m2"]["result"]["webhook"])
    print(f"[09] OK notify → {out_path}")