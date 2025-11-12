# tests/test_node_authoring.py
import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import authoring

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_authoring_from_retrieval_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")

    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)
    state_path = baton["last_state"]

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Ejecutar authoring
    state = authoring.run(state)

    # Asegura que ahora exista curso_m2
    assert "curso_m2" in state and state["curso_m2"], "authoring no produjo curso_m2"

    out_path = os.path.join(rdir, "04_authoring.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # 🔴 IMPORTANTE: actualizar el “batón”
    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    print(f"[04] OK authoring → {out_path}")