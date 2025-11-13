import os, json, glob
from dotenv import load_dotenv
from graphs.m2_creacion.nodes import assembler

load_dotenv()

def _latest_run_dir():
    base = os.getenv("ARTIF_DIR", "artifacts")
    runs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime, reverse=True)
    assert runs, "No hay runs previos en artifacts/"
    return runs[0]

def test_assembler_from_qc_dump_state():
    rdir = _latest_run_dir()
    baton_path = os.path.join(rdir, "baton.json")

    with open(baton_path, "r", encoding="utf-8") as f:
        baton = json.load(f)
    state_path = baton["last_state"]

    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Ejecutar assembler
    state = assembler.run(state)

    out_path = os.path.join(rdir, "08_assembler.state.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # Actualizar baton
    baton["last_state"] = out_path
    with open(baton_path, "w", encoding="utf-8") as f:
        json.dump(baton, f, ensure_ascii=False, indent=2)

    paquete = state["paquete_m2"]
    print("\n=== ENSAMBLADOR (ASSEMBLER) ===")
    print("Curso:", paquete["manifest"]["nombre_paquete"])
    print("Módulos:", paquete["manifest"]["modulos"])
    print("Lecciones:", paquete["manifest"]["lecciones"])
    print("Score de calidad:", paquete["manifest"]["score_calidad"])
    print("Hash bundle:", paquete["bundle_hash"])
    print(f"[08] OK assembler → {out_path}")