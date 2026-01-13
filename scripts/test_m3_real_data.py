"""
Prueba M3 con datos reales de la base de datos
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# IDs reales de la base de datos (del script anterior)
COMPANY_ID = 1
COURSE_ID = 1

print("="*80)
print("PROBANDO M3 CON DATOS REALES DE LA BASE DE DATOS")
print("="*80)

# Payload usando IDs reales
m3_payload = {
    "curso_id": str(COURSE_ID),  # ID real del curso en DB
    "cliente_id": f"company-{COMPANY_ID}",
    "cliente_email": "demo@techcorp.com",  # Email real de la empresa
    "syllabus_aprobado": {
        "titulo": "Introducción a Python",
        "nivel": "Basico",
        "industria": "Tecnología",
        "competencias": ["Python", "Programación", "Algoritmos"],
        "duracion_horas": 20
    },
    "empleados": [
        {
            "empleado_id": "EMP-001",
            "nombre": "Ana García",
            "email": "ana.garcia@techcorp.com"
        },
        {
            "empleado_id": "EMP-002", 
            "nombre": "Carlos Ruiz",
            "email": "carlos.ruiz@techcorp.com"
        }
    ]
}

print(f"\nUsando datos reales:")
print(f"  - Company ID: {COMPANY_ID}")
print(f"  - Course ID: {COURSE_ID}")
print(f"  - Empleados: {len(m3_payload['empleados'])}")

print(f"\n{'='*80}")
print("EJECUTANDO M3...")
print(f"{'='*80}\n")

try:
    response = requests.post(
        f"{BASE_URL}/m3/m3/iniciar",
        json=m3_payload,
        timeout=120
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"{'='*80}")
        print("RESULTADO")
        print(f"{'='*80}")
        print(f"\nRun ID: {result.get('run_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Gamificación: {result.get('gamificacion_activa')}")
        print(f"Empleados asignados: {result.get('empleados_asignados_count')}")
        
        if result.get('errors'):
            print(f"\nErrores/Advertencias:")
            for err in result.get('errors', []):
                print(f"  ⚠️  {err}")
            
            print(f"\n{'='*80}")
            print("NOTA:")
            print(f"{'='*80}")
            print("Los errores son esperados porque los nodos de M3 todavía")
            print("están configurados para buscar cursos con IDs de tipo string")
            print("en lugar de IDs numéricos de la base de datos.")
            print("\nPara resolver esto, necesitas modificar los nodos M3")
            print("según la guía en: guia_datos_reales.md")
        else:
            print(f"\n🎉 ¡M3 ejecutado exitosamente con datos reales!")
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n{'='*80}")
print("SIGUIENTES PASOS:")
print(f"{'='*80}")
print("\n1. Revisa la guía: guia_datos_reales.md")
print("2. Modifica los nodos de M3 para usar la base de datos")
print("3. Vuelve a probar con este script")
