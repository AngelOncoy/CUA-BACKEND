"""
Estado del Macroproceso 3: Entrega y Administración del Aprendizaje
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class M3State(TypedDict, total=False):
    """Estado del grafo de entrega y administración"""
    
    # Identificadores
    run_id: str
    curso_id: str
    cliente_id: str
    syllabus_aprobado: Dict[str, Any]
    
    # Proceso 3.1: Publicación
    curso_publicado: bool
    lms_course_id: str
    url_acceso: str
    notificacion_enviada: bool
    email_status: Dict[str, Any]
    
    # Proceso 3.2: Gestión del Aprendizaje
    empleados_asignados: List[Dict[str, Any]]
    asignaciones_completadas: bool
    gamificacion_activa: bool
    
    # Proceso 3.3: Monitoreo
    metricas_progreso: Dict[str, Any]
    certificados_emitidos: List[Dict[str, Any]]
    analytics_dashboard: Dict[str, Any]
    
    # Control de flujo
    status: str  # "PUBLICANDO", "ASIGNANDO", "MONITOREANDO", "COMPLETADO"
    errors: List[str]
    timestamp_inicio: str
    timestamp_fin: Optional[str]


class CursoPublicacion(TypedDict):
    """Datos del curso para publicación"""
    titulo: str
    descripcion: str
    duracion_horas: int
    nivel: str
    industria: str
    modulos: List[Dict[str, Any]]
    syllabus_markdown: str
    precio: float


class EmpleadoAsignacion(TypedDict):
    """Datos de empleado para asignación"""
    empleado_id: str
    nombre: str
    email: str
    departamento: str
    rol: str


class ProgressMetrics(TypedDict):
    """Métricas de progreso de aprendizaje"""
    empleado_id: str
    curso_id: str
    porcentaje_avance: float
    lecciones_completadas: int
    lecciones_totales: int
    evaluaciones_completadas: int
    evaluaciones_totales: int
    tiempo_invertido_minutos: int
    ultimo_acceso: str
    puntos_ganados: int
    medallas_obtenidas: List[str]


class Certificado(TypedDict):
    """Datos del certificado digital"""
    certificado_id: str
    empleado_id: str
    curso_id: str
    nombre_empleado: str
    nombre_curso: str
    fecha_emision: str
    calificacion_final: float
    url_certificado: str
    hash_verificacion: str