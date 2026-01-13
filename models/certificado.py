"""
Modelo Pydantic para Certificado
"""
from pydantic import BaseModel, Field
from typing import Optional

class Certificado(BaseModel):
    """Esquema para un certificado"""
    certificado_id: str = Field(..., description="ID único del certificado")
    curso_id: str = Field(..., description="ID del curso asociado")
    empleado_id: str = Field(..., description="ID del empleado")
    empleado_nombre: str = Field(..., description="Nombre del empleado")
    fecha_emision: str = Field(..., description="Fecha de emisión (ISO format)")
    url_certificado: Optional[str] = Field(None, description="URL para descargar el certificado")

    class Config:
        json_schema_extra = {
            "example": {
                "certificado_id": "CERT-001",
                "curso_id": "CURSO-001",
                "empleado_id": "EMP001",
                "empleado_nombre": "Juan Pérez",
                "fecha_emision": "2025-11-12T18:30:00.000Z",
                "url_certificado": "https://lms.example.com/certificates/CERT-001"
            }
        }