import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import assessments

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_assessments_from_media_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")

    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)

    state_path = baton["last_state"]
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Ejecuta assessments
    state = assessments.run(state)

    out_path = os.path.join(rdir, "06_assessments.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    # Resumen rápido en consola
    ev = state.get("evaluaciones_m2", {})
    print("\n=== RESUMEN EVALUACIONES ===")
    for mm in ev.get("modulos", []):
        print(f"- {mm['modulo']}: quiz={len(mm['quiz']['items'])} ítems | rúbrica={len(mm['rubrica'])} criterios")

    print(f"[06] OK assessments → {out_path}")