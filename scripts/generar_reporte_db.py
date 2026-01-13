"""
Genera reporte JSON de la base de datos
"""
import sqlite3
import json

db_path = "database.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def row_to_dict(row):
    return dict(zip(row.keys(), row))

reporte = {}

# Empresas
cursor.execute("SELECT * FROM companies")
reporte['companies'] = [row_to_dict(row) for row in cursor.fetchall()]

# Cursos
cursor.execute("SELECT * FROM courses")
reporte['courses'] = [row_to_dict(row) for row in cursor.fetchall()]

# Ediciones
cursor.execute("SELECT * FROM course_editions")
reporte['course_editions'] = [row_to_dict(row) for row in cursor.fetchall()]

# Participantes
cursor.execute("SELECT * FROM participants")
reporte['participants'] = [row_to_dict(row) for row in cursor.fetchall()]

# Inscripciones
cursor.execute("SELECT * FROM enrollments")
reporte['enrollments'] = [row_to_dict(row) for row in cursor.fetchall()]

conn.close()

# Guardar en archivo
with open('reporte_db.json', 'w', encoding='utf-8') as f:
    json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)

print(f"Reporte guardado en: reporte_db.json")
print(f"\nRESUMEN:")
print(f"  - Empresas: {len(reporte['companies'])}")
print(f"  - Cursos: {len(reporte['courses'])}")
print(f"  - Ediciones: {len(reporte['course_editions'])}")
print(f"  - Participantes: {len(reporte['participants'])}")
print(f"  - Inscripciones: {len(reporte['enrollments'])}")
