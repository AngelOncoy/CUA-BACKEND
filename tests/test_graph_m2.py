# tests/test_graph_m2.py
import json
from dotenv import load_dotenv
from graphs.m2_creacion.graph import build_graph
from graphs.m2_creacion.adapter import m1_to_m2_input

load_dotenv()

def test_run_graph_m2():
    # Cargar output del M1 (usa tu archivo real)
    with open("data/response_1762807952460.json", "r", encoding="utf-8") as f:
        m1 = json.load(f)

    app = build_graph()
    m2 = m1_to_m2_input(m1)

    state = {
        "input": m2.model_dump(),
        "entidades": m2.entidades.model_dump(),
        "config": {
            "retrieval": {"debug": True},
            "notify": {"dry_run": True, "extra": {"owner": "Cliente", "macroproceso": "M2"}}
        }
    }

    result = app.invoke(state)
    print("\n✅ GRAPH M2 COMPLETED")
    print("Curso:", result.get("paquete_m2", {}).get("manifest", {}).get("nombre_paquete"))
    print("Score:", result.get("paquete_m2", {}).get("manifest", {}).get("score_calidad"))
    print("Bundle hash:", result.get("paquete_m2", {}).get("bundle_hash"))

    assert "paquete_m2" in result