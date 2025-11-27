"""
Servicio para guardar cursos del M2 en la base de datos
"""
from sqlalchemy.orm import Session
from api.models.lms import Course, Lesson
from api.config.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def save_m2_course_to_db(m2_result: dict, company_id: int = None) -> int:
    """
    Guarda el resultado del M2 en la base de datos
    
    Args:
        m2_result: Resultado completo del grafo M2
        company_id: ID de la empresa (opcional)
    
    Returns:
        int: ID del curso creado en la DB
    """
    db = SessionLocal()
    try:
        entidades = m2_result.get('entidades', {})
        paquete_m2 = m2_result.get('paquete_m2', {})
        manifest = paquete_m2.get('manifest', {})
        
        # Crear curso
        course = Course(
            name=manifest.get('nombre_paquete', f"Curso de {entidades.get('industria', 'Sin título')}"),
            description=f"Nivel: {entidades.get('nivel', 'N/A')}. Competencias: {', '.join(entidades.get('competencias', []))}",
            level=entidades.get('nivel', 'Intermedio'),
            duration_hours=40.0,  # Valor por defecto
            status="CREADO_M2",
            company_id=company_id
        )
        
        db.add(course)
        db.commit()
        db.refresh(course)
        
        # Crear lecciones si hay módulos
        curso_m2 = m2_result.get('curso_m2_multimedia', {})
        modulos = curso_m2.get('modulos', [])
        
        lesson_order = 1
        for modulo in modulos:
            for leccion in modulo.get('lecciones', []):
                lesson = Lesson(
                    course_id=course.id,
                    title=leccion.get('titulo', 'Lección sin título'),
                    order=lesson_order,
                    type=leccion.get('tipo', 'TEORICA')
                )
                db.add(lesson)
                lesson_order += 1
        
        db.commit()
        
        logger.info(f"✅ Curso guardado en DB con ID: {course.id}")
        return course.id
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error guardando curso: {e}")
        raise
    finally:
        db.close()
