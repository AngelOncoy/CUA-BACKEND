"""
Modelo Pydantic para Curso
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class Curso(BaseModel):
    """Esquema para un curso"""
    curso_id: str = Field(..., description="ID único del curso")
    titulo: str = Field(..., description="Título del curso")
    descripcion: Optional[str] = Field(None, description="Descripción del curso")
    duracion_horas: int = Field(..., gt=0, description="Duración en horas")
    nivel: str = Field(..., description="Nivel del curso (básico, intermedio, avanzado)")
    industria: str = Field(..., description="Industria objetivo")
    precio: float = Field(..., ge=0, description="Precio del curso")

    class Config:
        json_schema_extra = {
            "example": {
                "curso_id": "CURSO-001",
                "titulo": "Técnicas Avanzadas de Ventas B2B",
                "descripcion": "Curso completo de ventas",
                "duracion_horas": 12,
                "nivel": "intermedio",
                "industria": "ventas",
                "precio": 2500.00
            }
        }