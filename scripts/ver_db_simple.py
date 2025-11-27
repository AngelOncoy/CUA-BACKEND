"""
Consulta directa a la base de datos usando SQL
"""
import sqlite3
import json

db_path = "database.db"

print("\n" + "="*80)
print("DATOS DIRECTOS DE LA BASE DE DATOS (SQL)")
print("="*80)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. EMPRESAS
print("\n1. EMPRESAS")
print("-" * 80)
cursor.execute("SELECT * FROM companies")
companies = cursor.fetchall()
for row in companies:
    print(f"  ID: {row['id']}, Nombre: {row['name']}, Email: {row['contact_email']}")

# 2. CURSOS
print("\n2. CURSOS")
print("-" * 80)
cursor.execute("SELECT * FROM courses")
courses = cursor.fetchall()
for row in courses:
    print(f"  ID: {row['id']}")
    print(f"  Nombre: {row['name']}")
    print(f"  Nivel: {row['level']}, Duración: {row['duration_hours']}h")
    print(f"  Status: {row['status']}, Company ID: {row['company_id']}")
    print()

# 3. EDICIONES
print("\n3. EDICIONES DE CURSOS")
print("-" * 80)
cursor.execute("""
    SELECT ce.*, c.name as course_name 
    FROM course_editions ce
    JOIN courses c ON ce.course_id = c.id
""")
editions = cursor.fetchall()
for row in editions:
    print(f"  ID: {row['id']}, Curso: {row['course_name']}")
    print(f"  Fecha: {row['start_date']}, Status: {row['status']}")
    print()

# 4. PARTICIPANTES
print("\n4. PARTICIPANTES")
print("-" * 80)
cursor.execute("""
    SELECT p.*, c.name as company_name
    FROM participants p
    JOIN companies c ON p.company_id = c.id
""")
participants = cursor.fetchall()
for row in participants:
    print(f"  ID: {row['id']}, Nombre: {row['name']}")
    print(f"  Email: {row['email']}, Empresa: {row['company_name']}")
    print()

# 5. INSCRIPCIONES
print("\n5. INSCRIPCIONES (ENROLLMENTS)")
print("-" * 80)
cursor.execute("""
    SELECT e.*, p.name as participant_name, c.name as course_name
    FROM enrollments e
    JOIN participants p ON e.participant_id = p.id
    JOIN course_editions ce ON e.edition_id = ce.id
    JOIN courses c ON ce.course_id = c.id
""")
enrollments = cursor.fetchall()
for row in enrollments:
    print(f"  ID: {row['id']}")
    print(f"  Participante: {row['participant_name']}")
    print(f"  Curso: {row['course_name']}")
    print(f"  Status: {row['status']}, Asignado: {row['assigned_at']}")
    print()

# 6. PROGRESO (sample)
print("\n6. PROGRESO DE LECCIONES (primeros 5)")
print("-" * 80)
cursor.execute("""
    SELECT lp.*, p.name as participant_name, l.title as lesson_title
    FROM lesson_progresses lp
    JOIN enrollments e ON lp.enrollment_id = e.id
    JOIN participants p ON e.participant_id = p.id
    JOIN lessons l ON lp.lesson_id = l.id
    LIMIT 5
""")
progresses = cursor.fetchall()
for row in progresses:
    print(f"  {row['participant_name']} - {row['lesson_title']}: {row['status']}")

# RESUMEN
print("\n" + "="*80)
print("RESUMEN")
print("="*80)

cursor.execute("SELECT COUNT(*) as count FROM companies")
print(f"  Empresas: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM courses")
print(f"  Cursos: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM course_editions")
print(f"  Ediciones: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM participants")
print(f"  Participantes: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM enrollments")
print(f"  Inscripciones: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM lesson_progresses")
print(f"  Registros de progreso: {cursor.fetchone()['count']}")

print("="*80 + "\n")

conn.close()
