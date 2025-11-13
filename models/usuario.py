"""
Modelo Pydantic para Usuario (Empleado)
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Usuario(BaseModel):
    """Esquema para un usuario/empleado"""
    empleado_id: str = Field(..., description="ID único del empleado")
    nombre: str = Field(..., description="Nombre completo del empleado")
    email: EmailStr = Field(..., description="Correo electrónico del empleado")
    departamento: Optional[str] = Field(None, description="Departamento del empleado")
    progreso: Optional[float] = Field(None, ge=0, le=100, description="Progreso en el curso (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "empleado_id": "EMP001",
                "nombre": "Juan Pérez",
                "email": "juan@empresa.com",
                "departamento": "Ventas",
                "progreso": 75.0
            }
        }