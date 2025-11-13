"""
Script de Prueba del Macroproceso 3
Ejecuta un flujo completo de entrega y monitoreo
"""
import httpx
import asyncio
import json
from datetime import datetime


BASE_URL = "http://localhost:8003"


async def test_flujo_completo():
    """
    Prueba el flujo completo del Macroproceso 3:
    1. Iniciar entrega de curso
    2. Consultar progreso
    3. Actualizar analytics
    """
    print("=" * 70)
    print("🧪 TEST DEL MACROPROCESO 3: ENTREGA Y ADMINISTRACIÓN")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # ===== PASO 1: VERIFICAR HEALTH =====
        print("📡 1. Verificando estado del servicio...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("   ✓ Servicio operacional")
            else:
                print(f"   ✗ Error: {response.status_code}")
                return
        except Exception as e:
            print(f"   ✗ No se pudo conectar al servicio: {e}")
            print("   💡 Asegúrate de que el servidor esté corriendo:")
            print("      python api/main.py")
            return
        
        print()
        
        # ===== PASO 2: INICIAR ENTREGA =====
        print("🚀 2. Iniciando proceso de entrega...")
        
        payload = {
            "curso_id": f"CURSO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "cliente_id": "CLI-TEST-001",
            "cliente_email": "cliente.test@empresa.com",
            "syllabus_aprobado": {
                "titulo": "Técnicas Avanzadas de Ventas B2B",
                "descripcion": "Curso completo sobre estrategias modernas de ventas B2B",
                "duracion_horas": 12,
                "nivel": "intermedio",
                "industria": "ventas",
                "precio": 2500.00,
                "modulos": [
                    {
                        "nombre": "Prospección Digital",
                        "lecciones": 12
                    },
                    {
                        "nombre": "Negociación Consultiva",
                        "lecciones": 12
                    },
                    {
                        "nombre": "Cierre y Seguimiento",
                        "lecciones": 12
                    }
                ]
            },
            "empleados": [
                {
                    "empleado_id": "EMP001",
                    "nombre": "Juan Pérez",
                    "email": "juan.perez@empresa.com",
                    "departamento": "Ventas",
                    "rol": "Ejecutivo"
                },
                {
                    "empleado_id": "EMP002",
                    "nombre": "María García",
                    "email": "maria.garcia@empresa.com",
                    "departamento": "Ventas",
                    "rol": "Supervisor"
                },
                {
                    "empleado_id": "EMP003",
                    "nombre": "Carlos Rodríguez",
                    "email": "carlos.rodriguez@empresa.com",
                    "departamento": "Ventas",
                    "rol": "Ejecutivo"
                }
            ]
        }
        
        try:
            response = await client.post(f"{BASE_URL}/m3/iniciar", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                run_id = result["run_id"]
                
                print(f"   ✓ Entrega iniciada exitosamente")
                print(f"   📋 Run ID: {run_id}")
                print(f"   🎓 Curso LMS ID: {result.get('lms_course_id')}")
                print(f"   🔗 URL de acceso: {result.get('url_acceso')}")
                print(f"   📧 Notificación enviada: {'✓' if result.get('notificacion_enviada') else '✗'}")
                print(f"   👥 Empleados asignados: {result.get('empleados_asignados_count')}")
                print(f"   🎮 Gamificación activa: {'✓' if result.get('gamificacion_activa') else '✗'}")
                print(f"   🏆 Certificados emitidos: {result.get('certificados_emitidos_count')}")
                
                if result.get('errors'):
                    print(f"   ⚠️  Errores: {result['errors']}")
                
            else:
                print(f"   ✗ Error {response.status_code}: {response.text}")
                return
                
        except Exception as e:
            print(f"   ✗ Excepción: {e}")
            return
        
        print()
        
        # ===== PASO 3: CONSULTAR PROGRESO =====
        print("📊 3. Consultando progreso y analytics...")
        await asyncio.sleep(1)  # Breve pausa
        
        try:
            response = await client.post(
                f"{BASE_URL}/m3/consultar-progreso",
                json={"run_id": run_id}
            )
            
            if response.status_code == 200:
                progreso = response.json()
                dashboard = progreso.get("analytics_dashboard", {})
                resumen = dashboard.get("resumen", {})
                
                print(f"   ✓ Analytics obtenidos")
                print(f"   ")
                print(f"   📈 RESUMEN GENERAL:")
                print(f"      • Empleados totales: {resumen.get('empleados_totales')}")
                print(f"      • Progreso promedio: {resumen.get('progreso_promedio')}%")
                print(f"      • Tasa de finalización: {resumen.get('tasa_finalizacion')}%")
                print(f"      • Completados: {resumen.get('empleados_completado')}")
                print(f"      • En progreso: {resumen.get('empleados_en_progreso')}")
                print(f"      • Tiempo promedio: {resumen.get('tiempo_promedio_minutos')} min")
                
                # Top performers
                top = dashboard.get("top_performers", [])
                if top:
                    print(f"   ")
                    print(f"   🏅 TOP PERFORMERS:")
                    for i, performer in enumerate(top[:3], 1):
                        print(f"      {i}. {performer['nombre']}: {performer['puntos']} pts ({performer['progreso']}%)")
                
                # Distribución de progreso
                dist = dashboard.get("distribucion_progreso", {})
                if dist:
                    print(f"   ")
                    print(f"   📊 DISTRIBUCIÓN DE PROGRESO:")
                    print(f"      • 0-25%:    {dist.get('0-25%', 0)} empleados")
                    print(f"      • 25-50%:   {dist.get('25-50%', 0)} empleados")
                    print(f"      • 50-75%:   {dist.get('50-75%', 0)} empleados")
                    print(f"      • 75-100%:  {dist.get('75-100%', 0)} empleados")
                
                # Certificados
                certificados = progreso.get("certificados_emitidos", [])
                if certificados:
                    print(f"   ")
                    print(f"   🎓 CERTIFICADOS EMITIDOS: {len(certificados)}")
                    for cert in certificados:
                        print(f"      • {cert['nombre_empleado']}: {cert['certificado_id']}")
                        print(f"        Calificación: {cert['calificacion_final']:.1f}%")
                
            else:
                print(f"   ✗ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Excepción: {e}")
        
        print()
        
        # ===== PASO 4: ACTUALIZAR ANALYTICS =====
        print("🔄 4. Actualizando analytics en tiempo real...")
        
        try:
            response = await client.post(f"{BASE_URL}/m3/actualizar-analytics/{run_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Analytics actualizados")
                print(f"   📊 Dashboard actualizado: {result.get('actualizado')}")
                print(f"   🎓 Nuevos certificados: {result.get('nuevos_certificados')}")
            else:
                print(f"   ✗ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ✗ Excepción: {e}")
        
        print()
        print("=" * 70)
        print("✅ TEST COMPLETADO")
        print("=" * 70)
        print()
        print("💡 Próximos pasos:")
        print("   1. Revisa la documentación en: http://localhost:8003/docs")
        print("   2. Consulta los logs para ver el flujo detallado")
        print("   3. Integra con tu LMS real modificando los servicios mock")


if __name__ == "__main__":
    asyncio.run(test_flujo_completo())