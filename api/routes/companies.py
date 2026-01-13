# api/routes/companies.py
"""
Endpoints para gestionar empresas/clientes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from api.config.database import get_db
from api.models.lms import Company, Course

router = APIRouter(prefix="/companies", tags=["Companies"])


class CompanyCreate(BaseModel):
    """Schema para crear empresa"""
    name: str
    contact_email: EmailStr


class CompanyResponse(BaseModel):
    """Schema de respuesta de empresa"""
    id: int
    name: str
    contact_email: str
    courses_count: int = 0
    
    class Config:
        from_attributes = True


@router.post("/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva empresa/cliente
    """
    # Verificar si ya existe
    existing = db.query(Company).filter(Company.contact_email == company.contact_email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una empresa con el email {company.contact_email}"
        )
    
    db_company = Company(
        name=company.name,
        contact_email=company.contact_email
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return CompanyResponse(
        id=db_company.id,
        name=db_company.name,
        contact_email=db_company.contact_email,
        courses_count=0
    )


@router.get("/", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    """
    Lista todas las empresas
    """
    companies = db.query(Company).all()
    return [
        CompanyResponse(
            id=c.id,
            name=c.name,
            contact_email=c.contact_email,
            courses_count=len(c.courses)
        )
        for c in companies
    ]


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una empresa por ID
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return CompanyResponse(
        id=company.id,
        name=company.name,
        contact_email=company.contact_email,
        courses_count=len(company.courses)
    )


@router.get("/{company_id}/courses")
def get_company_courses(company_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los cursos de una empresa
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    courses = db.query(Course).filter(Course.company_id == company_id).all()
    
    return {
        "company_id": company_id,
        "company_name": company.name,
        "courses": [
            {
                "id": c.id,
                "name": c.name,
                "level": c.level,
                "duration_hours": c.duration_hours,
                "status": c.status
            }
            for c in courses
        ]
    }
