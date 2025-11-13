import os, json, uuid, datetime
from graphs.m2_creacion.adapter import m1_to_m2_input
from graphs.m2_creacion.nodes import objectives

RUNS_DIR = os.getenv("ARTIF_DIR", "artifacts")
def _run_dir():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(RUNS_DIR, f"{ts}_{str(uuid.uuid4())[:8]}")

def test_objectives_dump_state():
    # 1) Cargar output del M1
    m1_path = os.getenv("M1_JSON", "data/response_1762807952460.json")
    with open(m1_path, "r", encoding="utf-8") as f:
        m1 = json.load(f)

    # 2) Normalizar input para M2
    m2_input = m1_to_m2_input(m1)
    state = {
        "input": m2_input.model_dump(),
        "entidades": m2_input.entidades.model_dump(),
    }

    # 3) Ejecutar objectives
    state = objectives.run(state)

    # 4) Guardar artefacto para el siguiente test
    rdir = _run_dir()
    os.makedirs(rdir, exist_ok=True)
    out_path = os.path.join(rdir, "01_objectives.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # 5) Deja un “batón” con la ruta para el siguiente test
    with open(os.path.join(rdir, "baton.json"), "w", encoding="utf-8") as f:
        json.dump({"run_dir": rdir, "last_state": out_path}, f)

    print("[01] OK objectives →", out_path)