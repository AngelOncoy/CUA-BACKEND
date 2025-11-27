"""
Estado del Macroproceso 3: Entrega y Administración del Aprendizaje
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class M3State(TypedDict, total=False):
    """Estado del grafo de entrega y administración"""
    
    # Identificadores (mantener compatibilidad con ambas nomenclaturas)
    run_id: str
    curso_id: str  # Usado por API
    course_id: str  # Usado por nodos internos
    cliente_id: str  # Usado por API
    company_id: str  # Usado por nodos internos
    cliente_email: str  # Usado por API
    syllabus_aprobado: Dict[str, Any]
    
    # Proceso 3.1: Publicación
    curso_publicado: bool
    edition_id: int  # ID de la edición creada
    lms_course_id: str
    url_acceso: str
    notificacion_enviada: bool
    email_status: Dict[str, Any]
    
    # Proceso 3.2: Gestión del Aprendizaje
    empleados: List[Dict[str, Any]]  # Usado por API
    employees: List[Dict[str, Any]]  # Usado por nodos internos
    empleados_asignados: List[Dict[str, Any]]
    enrollment_ids: List[int]  # IDs de matrículas creadas
    asignaciones_completadas: bool
    gamificacion_activa: bool
    
    # Proceso 3.3: Monitoreo
    analytics: Dict[str, Any]  # Usado por nodos internos
    analytics_dashboard: Dict[str, Any]  # Usado por API
    metricas_progreso: Dict[str, Any]
    certificados_emitidos: List[Dict[str, Any]]  # Usado por API
    certificates: List[Dict[str, Any]]  # Usado por nodos internos
    
    # Prompts de agentes (para auditoría)
    prompt_publicacion: str
    prompt_notificacion: str
    prompt_asignacion: str
    prompt_gamificacion: str
    prompt_monitoreo: str
    prompt_certificacion: str
    
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