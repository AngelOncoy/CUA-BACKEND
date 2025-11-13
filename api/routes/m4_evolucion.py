from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

from graphs.m4_evolucion.graph import m4_app

router = APIRouter()


class PromptIn(BaseModel):
    prompt: str


class ContinueIn(BaseModel):
    run_id: str
    data: dict = {}


def cfg_for(run_id: str):
    return {"configurable": {"thread_id": run_id}}


# ===========================
# POST /m4/prompt  → iniciar flujo M4
# ===========================
@router.post("/prompt")
async def start_m4(data: PromptIn):
    run_id = str(uuid4())
    state = await m4_app.ainvoke(
        {"prompt_raw": data.prompt},
        config=cfg_for(run_id)
    )
    return {"run_id": run_id, "state": state}


# ===========================
# POST /m4/next → continuar flujo M4
# ===========================
@router.post("/next")
async def continue_m4(data: ContinueIn):
    state = await m4_app.ainvoke(
        data.data,
        config=cfg_for(data.run_id)
    )
    return {"run_id": data.run_id, "state": state}
