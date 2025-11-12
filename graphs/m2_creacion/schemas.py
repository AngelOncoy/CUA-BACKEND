from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Entidades(BaseModel):
    industria: str
    nivel: str
    competencias: List[str]
    confianza: float = Field(ge=0, le=1)

class M2Input(BaseModel):
    run_id: Optional[str] = None            # para trazabilidad
    entidades: Entidades                    # del M1 (o respuestas consolidadas)
    syllabus_md: Optional[str] = None       # opcional: sílabus generado en M1
    mapping: Optional[Dict[str, Any]] = None  # opcional: mapping del M1