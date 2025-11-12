# tests/test_node_media.py
import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import authoring, media

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_media_from_authoring_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")
    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)

    state_path = baton["last_state"]
    print(f"[media] run_dir={rdir}")
    print(f"[media] intentando cargar state={state_path}")

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    if not state.get("curso_m2"):
        # intenta tomar el archivo canon de authoring
        authoring_state = os.path.join(rdir, "04_authoring.state.json")
        if os.path.exists(authoring_state):
            print(f"[media] curso_m2 ausente, usando {authoring_state}")
            with open(authoring_state, "r", encoding="utf-8") as f:
                state = json.load(f)
        else:
            # como último recurso, ejecuta authoring ahora
            print("[media] curso_m2 ausente, ejecutando authoring en caliente…")
            state = authoring.run(state)
            with open(authoring_state, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            baton["last_state"] = authoring_state
            with open(baton_path, "w", encoding="utf-8") as f:
                json.dump(baton, f, ensure_ascii=False, indent=2)

    # ya con curso_m2 disponible, ejecuta media
    state = media.run(state)

    out_path = os.path.join(rdir, "05_media.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    print(f"[05] OK media → {out_path}")