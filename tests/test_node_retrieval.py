import os, json, glob
from graphs.m2_creacion.nodes import retrieval
from dotenv import load_dotenv
load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_retrieval_from_mapping_dump_state():
    rdir = _latest_run_dir()
    with open(os.path.join(rdir, "baton.json"), "r", encoding="utf-8") as f:
        baton = json.load(f)
    state_path = baton["last_state"]

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Si tu retrieval tiene flags por config, puedes setearlos aquí:
    state.setdefault("config", {})
    state["config"].setdefault("retrieval", {"debug": True})

    state = retrieval.run(state)

    out_path = os.path.join(rdir, "03_retrieval.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    baton.update({"last_state": out_path})
    with open(os.path.join(rdir, "baton.json"), "w", encoding="utf-8") as f:
        json.dump(baton, f)

    print("[03] OK retrieval →", out_path)