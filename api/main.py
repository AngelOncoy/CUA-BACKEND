# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import m1_interaccion, health

app = FastAPI(title="AUTOMA Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

app.include_router(health.router, tags=["Health"])
app.include_router(m1_interaccion.router, prefix="/m1", tags=["Macroproceso 1"])

@app.get("/")
def root():
    return {"status": "ok", "message": "AUTOMA backend corriendo correctamente"}
