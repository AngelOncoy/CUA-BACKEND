"""
Script para inicializar la base de datos con todas las tablas necesarias
"""
import sys
sys.path.append('.')

from api.config.database import engine, Base
from api.models.lms import (
    Company,
    Course,
    CourseEdition,
    Lesson,
    Participant,
    Enrollment,
    LessonProgress,
    Certificate,
    NotificationEvent
)

def init_database():
    """Crea todas las tablas en la base de datos"""
    print("Creando tablas en la base de datos...")
    print(f"Base de datos: {engine.url}")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Tablas creadas exitosamente:\n")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
        
        print("\n🎉 Base de datos inicializada correctamente!")
        
    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
