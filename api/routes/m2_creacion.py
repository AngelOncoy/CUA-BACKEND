# api/routes/m2_creacion.py
from fastapi import APIRouter, HTTPException
from graphs.m2_creacion.graph import build_graph
from graphs.m2_creacion.schemas import M2Input
from graphs.m2_creacion.adapter import m1_to_m2_input

router = APIRouter(prefix="/m2", tags=["m2_creacion"])
graph = build_graph()

@router.post("/run")
def run_m2(payload: dict):
    """
    Acepta:
      - output de M1 (dict) -> usa adapter m1_to_m2_input
      - o directamente un M2Input (dict con entidades/...)
    """
    try:
        if "entidades" in payload:
            m2in = M2Input(**payload)
        else:
            m2in = m1_to_m2_input(payload)

        state = {
            "input": m2in.model_dump(),
            "entidades": m2in.entidades.model_dump(),
        }
        result = graph.invoke(state)
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))