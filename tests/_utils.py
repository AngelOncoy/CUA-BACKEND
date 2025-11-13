import os, json, uuid, datetime
from pathlib import Path
from dotenv import load_dotenv

ARTIF_BASE = Path(os.getenv("M2_ARTIFACTS_DIR", "artifacts"))

def ensure_env():
    load_dotenv()
    return True

def read_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(obj, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def resolve_run_id(m1_output: dict) -> str:
    rid = (m1_output.get("run_id") or "").strip()
    if rid:
        return rid
    # si no hay run_id en M1, generamos uno corto y fechamos
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{ts}-{str(uuid.uuid4())[:8]}"

def run_dir(run_id: str) -> Path:
    return ARTIF_BASE / run_id

def art_path(run_id: str, name: str) -> Path:
    """Nombre relativo dentro del run (ej: '01_mapping.state.json')."""
    return run_dir(run_id) / name

def baton_path(run_id: str) -> Path:
    """Archivo pequeño para pasar info mínima al siguiente test (ej: run_id)."""
    return art_path(run_id, "baton.json")

def save_baton(run_id: str, extra: dict = None):
    data = {"run_id": run_id}
    if extra:
        data.update(extra)
    write_json(data, baton_path(run_id))

def load_baton(explicit_run_id: str | None = None) -> dict:
    """Permite reanudar: si pasas RUN_ID, usa ese; sino toma el 'último' por mtime."""
    if explicit_run_id:
        return read_json(baton_path(explicit_run_id))
    # último run (por fecha de modificación)
    if not ARTIF_BASE.exists():
        raise FileNotFoundError("No hay carpeta de artifacts aún.")
    runs = sorted(ARTIF_BASE.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise FileNotFoundError("No hay runs en artifacts/.")
    return read_json(runs[0] / "baton.json")