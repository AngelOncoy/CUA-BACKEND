import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import qc  # 👈 coincide con tu archivo qc.py

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_quality_control_from_assessments_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")

    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)

    state_path = baton["last_state"]  # debería apuntar a 06_assessments.state.json
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # ✅ Ejecutar el nodo qc
    state = qc.run(state)

    out_path = os.path.join(rdir, "07_qc.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    # ✅ Mostrar resumen
    report = state.get("control_calidad_m2", {})
    resumen = report.get("resumen", {})
    print("\n=== CONTROL DE CALIDAD (QC) ===")
    print("Score global:", resumen.get("score_global"))
    print("Módulos:", resumen.get("modulos"), "| Lecciones:", resumen.get("lecciones"))
    print("Quizzes:", resumen.get("quizzes_total_items"), "| Rúbricas OK:", resumen.get("rubricas_ok"))
    print(f"[07] OK qc → {out_path}")