"""
Ejemplo rápido: Crear empresa y verificar que funciona
"""
import sys
sys.path.append('.')

from api.config.database import SessionLocal
from api.models.lms import Company, Course

def ejemplo_datos_reales():
    """Demuestra cómo trabajar con datos reales"""
    db = SessionLocal()
    
    try:
        # 1. Crear una empresa de prueba
        print("1. Creando empresa...")
        company = Company(
            name="TechCorp Demo",
            contact_email="demo@techcorp.com"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"✅ Empresa creada: ID={company.id}, Nombre={company.name}")
        
        # 2. Crear un curso asociado a la empresa
        print("\n2. Creando curso...")
        course = Course(
            name="Introducción a Python",
            description="Curso básico de Python para principiantes",
            level="Basico",
            duration_hours=20.0,
            status="ACTIVO",
            company_id=company.id
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        print(f"✅ Curso creado: ID={course.id}, Nombre={course.name}")
        
        # 3. Listar todas las empresas
        print("\n3. Listando todas las empresas en la DB...")
        companies = db.query(Company).all()
        for c in companies:
            print(f"   - ID={c.id}: {c.name} ({c.contact_email})")
            courses_count = len(c.courses)
            print(f"     Cursos: {courses_count}")
        
        # 4. Listar todos los cursos
        print("\n4. Listando todos los cursos en la DB...")
        courses = db.query(Course).all()
        for c in courses:
            print(f"   - ID={c.id}: {c.name} (Nivel: {c.level}, Status: {c.status})")
        
        print("\n🎉 ¡Datos reales funcionando correctamente!")
        print(f"\n💡 Ahora puedes usar company_id={company.id} y course_id={course.id} en tus APIs")
        
        return company.id, course.id
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        return None, None
    finally:
        db.close()

if __name__ == "__main__":
    company_id, course_id = ejemplo_datos_reales()
    
    if company_id and course_id:
        print(f"\n{'='*80}")
        print("PRÓXIMO PASO:")
        print(f"{'='*80}")
        print(f"\nPuedes probar el flujo M3 con estos datos reales:")
        print(f'  curso_id: "{course_id}"')
        print(f'  company_id: "{company_id}"')
        print(f'\nEn Swagger UI (/docs), usa estos IDs en lugar de IDs de prueba.')
