"""
Script para mostrar todos los datos de la base de datos
"""
import sys
sys.path.append('.')

from api.config.database import SessionLocal
from api.models.lms import (
    Company,
    Course,
    CourseEdition,
    Lesson,
    Participant,
    Enrollment,
    LessonProgress,
    Certificate
)

def mostrar_base_datos():
    """Muestra todos los datos de la base de datos de forma organizada"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("DATOS EN LA BASE DE DATOS")
        print("="*80)
        
        # 1. EMPRESAS
        print("\n1. EMPRESAS (Companies)")
        print("-" * 80)
        companies = db.query(Company).all()
        if companies:
            for c in companies:
                print(f"  ID: {c.id}")
                print(f"  Nombre: {c.name}")
                print(f"  Email: {c.contact_email}")
                print(f"  Cursos: {len(c.courses)}")
                print(f"  Participantes: {len(c.participants)}")
                print()
        else:
            print("  (Sin empresas)")
        
        # 2. CURSOS
        print("\n2. CURSOS (Courses)")
        print("-" * 80)
        courses = db.query(Course).all()
        if courses:
            for c in courses:
                print(f"  ID: {c.id}")
                print(f"  Nombre: {c.name}")
                print(f"  Descripción: {c.description}")
                print(f"  Nivel: {c.level}")
                print(f"  Duración: {c.duration_hours} horas")
                print(f"  Status: {c.status}")
                if c.company_id:
                    print(f"  Empresa ID: {c.company_id}")
                print(f"  Ediciones: {len(c.editions)}")
                print(f"  Lecciones: {len(c.lessons)}")
                print()
        else:
            print("  (Sin cursos)")
        
        # 3. EDICIONES
        print("\n3. EDICIONES DE CURSOS (Course Editions)")
        print("-" * 80)
        editions = db.query(CourseEdition).all()
        if editions:
            for e in editions:
                course = db.query(Course).filter(Course.id == e.course_id).first()
                print(f"  ID: {e.id}")
                print(f"  Curso: {course.name if course else 'N/A'} (ID: {e.course_id})")
                print(f"  Fecha inicio: {e.start_date}")
                print(f"  Status: {e.status}")
                print(f"  Inscripciones: {len(e.enrollments)}")
                print()
        else:
            print("  (Sin ediciones)")
        
        # 4. LECCIONES
        print("\n4. LECCIONES (Lessons)")
        print("-" * 80)
        lessons = db.query(Lesson).all()
        if lessons:
            for l in lessons:
                course = db.query(Course).filter(Course.id == l.course_id).first()
                print(f"  ID: {l.id}")
                print(f"  Curso: {course.name if course else 'N/A'} (ID: {l.course_id})")
                print(f"  Título: {l.title}")
                print(f"  Orden: {l.order}")
                print(f"  Tipo: {l.type}")
                print()
        else:
            print("  (Sin lecciones)")
        
        # 5. PARTICIPANTES
        print("\n5. PARTICIPANTES (Participants)")
        print("-" * 80)
        participants = db.query(Participant).all()
        if participants:
            for p in participants:
                company = db.query(Company).filter(Company.id == p.company_id).first()
                print(f"  ID: {p.id}")
                print(f"  Nombre: {p.name}")
                print(f"  Email: {p.email}")
                print(f"  Empresa: {company.name if company else 'N/A'} (ID: {p.company_id})")
                print(f"  Activo: {p.is_active}")
                print(f"  Inscripciones: {len(p.enrollments)}")
                print()
        else:
            print("  (Sin participantes)")
        
        # 6. INSCRIPCIONES
        print("\n6. INSCRIPCIONES (Enrollments)")
        print("-" * 80)
        enrollments = db.query(Enrollment).all()
        if enrollments:
            for e in enrollments:
                participant = db.query(Participant).filter(Participant.id == e.participant_id).first()
                edition = db.query(CourseEdition).filter(CourseEdition.id == e.edition_id).first()
                course = db.query(Course).filter(Course.id == edition.course_id).first() if edition else None
                
                print(f"  ID: {e.id}")
                print(f"  Participante: {participant.name if participant else 'N/A'} ({participant.email if participant else 'N/A'})")
                print(f"  Curso: {course.name if course else 'N/A'}")
                print(f"  Edición ID: {e.edition_id}")
                print(f"  Fecha asignación: {e.assigned_at}")
                print(f"  Status: {e.status}")
                print(f"  Progreso de lecciones: {len(e.progresses)}")
                print()
        else:
            print("  (Sin inscripciones)")
        
        # 7. PROGRESO DE LECCIONES
        print("\n7. PROGRESO DE LECCIONES (Lesson Progress)")
        print("-" * 80)
        progresses = db.query(LessonProgress).limit(10).all()  # Limitar a 10 para no saturar
        if progresses:
            print(f"  Mostrando primeros 10 de {db.query(LessonProgress).count()} registros:")
            print()
            for p in progresses:
                enrollment = db.query(Enrollment).filter(Enrollment.id == p.enrollment_id).first()
                participant = db.query(Participant).filter(Participant.id == enrollment.participant_id).first() if enrollment else None
                lesson = db.query(Lesson).filter(Lesson.id == p.lesson_id).first()
                
                print(f"  ID: {p.id}")
                print(f"  Participante: {participant.name if participant else 'N/A'}")
                print(f"  Lección: {lesson.title if lesson else 'N/A'}")
                print(f"  Status: {p.status}")
                if p.score:
                    print(f"  Score: {p.score}")
                print()
        else:
            print("  (Sin progreso registrado)")
        
        # 8. CERTIFICADOS
        print("\n8. CERTIFICADOS (Certificates)")
        print("-" * 80)
        certificates = db.query(Certificate).all()
        if certificates:
            for c in certificates:
                enrollment = db.query(Enrollment).filter(Enrollment.id == c.enrollment_id).first()
                participant = db.query(Participant).filter(Participant.id == enrollment.participant_id).first() if enrollment else None
                
                print(f"  ID: {c.id}")
                print(f"  Participante: {participant.name if participant else 'N/A'}")
                print(f"  Código: {c.code}")
                print(f"  Fecha emisión: {c.issued_at}")
                if c.grade:
                    print(f"  Calificación: {c.grade}")
                if c.url:
                    print(f"  URL: {c.url}")
                print()
        else:
            print("  (Sin certificados emitidos)")
        
        # RESUMEN
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"  Empresas: {len(companies)}")
        print(f"  Cursos: {len(courses)}")
        print(f"  Ediciones: {len(editions)}")
        print(f"  Lecciones: {len(lessons)}")
        print(f"  Participantes: {len(participants)}")
        print(f"  Inscripciones: {len(enrollments)}")
        print(f"  Registros de progreso: {db.query(LessonProgress).count()}")
        print(f"  Certificados: {db.query(Certificate).count()}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    mostrar_base_datos()
