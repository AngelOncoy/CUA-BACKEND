"""
Script para probar el flujo completo M2->M3 con datos reales de la base de datos
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*80)
print("FLUJO COMPLETO M2->M3 CON DATOS REALES")
print("="*80)

# 1. Crear empresa
print("\n1. Creando empresa")
print("-" * 80)
company_response = requests.post(
    f"{BASE_URL}/api/companies/",
    json={
        "name": "Innovatech Solutions",
        "contact_email": "contacto@innovatech.com"
    }
)

if company_response.status_code == 200:
    company = company_response.json()
    company_id = company["id"]
    print(f"✅ Empresa creada:")
    print(f"   ID: {company_id}")
    print(f"   Nombre: {company['name']}")
    print(f"   Email: {company['contact_email']}")
elif company_response.status_code == 400:
    print("⚠️  La empresa ya existe, obteniendo datos...")
    companies = requests.get(f"{BASE_URL}/api/companies/").json()
    company = next((c for c in companies if c["contact_email"] == "contacto@innovatech.com"), companies[0])
    company_id = company["id"]
    print(f"   Usando empresa existente: ID={company_id}")
else:
    print(f"❌ Error creando empresa: {company_response.text}")
    exit(1)

# 2. Ejecutar M2 con persistencia
print(f"\n2. Ejecutando M2 (creación de curso) con persistencia")
print("-" * 80)
m2_response = requests.post(
    f"{BASE_URL}/m2/m2/run?persist=true",
    json={
        "company_id": company_id,
        "entidades": {
            "industria": "Inteligencia Artificial",
            "nivel": "Avanzado",
            "competencias": ["Machine Learning", "Deep Learning", "NLP"],
            "confianza": 0.95
        }
    },
    timeout=180
)

if m2_response.status_code == 200:
    m2_data = m2_response.json()
    course_id = m2_data.get("course_id")
    
    if course_id:
        print(f"✅ M2 ejecutado y curso guardado en DB:")
        print(f"   Course ID (DB): {course_id}")
        
        entidades = m2_data["result"]["entidades"]
        print(f"   Industria: {entidades['industria']}")
        print(f"   Nivel: {entidades['nivel']}")
        print(f"   Competencias: {', '.join(entidades['competencias'])}")
        
        paquete = m2_data["result"].get("paquete_m2", {})
        manifest = paquete.get("manifest", {})
        print(f" Quality Score: {manifest.get('score_calidad', 'N/A')}")
    else:
        print("⚠️  M2 ejecutado pero no se persistió en DB")
        course_id = None
else:
    print(f"❌ Error ejecutando M2: {m2_response.text}")
    exit(1)

# 3. Verificar curso en DB
if course_id:
    print(f"\n3. Verificando curso en la base de datos")
    print("-" * 80)
    courses = requests.get(f"{BASE_URL}/api/companies/{company_id}/courses").json()
    print(f"✅ Cursos de la empresa '{company['name']}':")
    for course in courses["courses"]:
        print(f"   - ID: {course['id']}, Nombre: {course['name']}, Status: {course['status']}")

# 4. Ejecutar M3 con datos reales
print(f"\n4. Ejecutando M3 (entrega) con curso real de DB")
print("-" * 80)

if not course_id:
    print("❌ No hay course_id disponible, abortando M3")
    exit(1)

m3_response = requests.post(
    f"{BASE_URL}/m3/m3/iniciar",
    json={
        "curso_id": str(course_id),  # ID real del curso en DB
        "cliente_id": str(company_id),  # ID real de la empresa
        "cliente_email": company["contact_email"],
        "syllabus_aprobado": m2_data["result"].get("paquete_m2", {}).get("manifest", {}),
        "empleados": [
            {
                "empleado_id": "EMP-AI-001",
                "nombre": "Dr. Elena Martínez",
                "email": "elena.martinez@innovatech.com"
            },
            {
                "empleado_id": "EMP-AI-002",
                "nombre": "Ing. Carlos Rodríguez",
                "email": "carlos.rodriguez@innovatech.com"
            },
            {
                "empleado_id": "EMP-AI-003",
                "nombre": "Lic. Ana Fernández",
                "email": "ana.fernandez@innovatech.com"
            }
        ]
    },
    timeout=120
)

if m3_response.status_code == 200:
    m3_data = m3_response.json()
    
    print(f"✅ M3 ejecutado exitosamente:")
    print(f"   Run ID: {m3_data.get('run_id')}")
    print(f"   Status: {m3_data.get('status')}")
    print(f"   Curso publicado: {m3_data.get('curso_publicado')}")
    print(f"   URL acceso: {m3_data.get('url_acceso')}")
    print(f"   Empleados asignados: {m3_data.get('empleados_asignados_count')}")
    print(f"   Gamificación activa: {m3_data.get('gamificacion_activa')}")
    
    if m3_data.get('errors'):
        print(f"\n⚠️  Advertencias/Errores reportados:")
        for error in m3_data['errors'][:3]:
            print(f"   - {error}")
    
    # Guardar resultado
    with open("flujo_completo_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "company": company,
            "m2_course_id": course_id,
            "m3_result": m3_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultado completo guardado en: flujo_completo_result.json")
    
else:
    print(f"❌ Error ejecutando M3: {m3_response.status_code}")
    print(m3_response.text)

# Resumen final
print(f"\n{'='*80}")
print("RESUMEN DEL FLUJO")
print(f"{'='*80}")
print(f"✓ Empresa: {company['name']} (ID: {company_id})")
print(f"✓ Curso creado en M2: ID {course_id}")
print(f"✓ M3 Run ID: {m3_data.get('run_id') if m3_response.status_code == 200 else 'N/A'}")
print(f"\n🎉 Flujo completo M2->M3 con datos reales ejecutado!")
