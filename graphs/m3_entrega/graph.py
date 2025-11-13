"""
Grafo Principal del Macroproceso 3: Entrega y Administración del Aprendizaje

Flujo:
1. PUBLICAR → Publicar curso en LMS
2. NOTIFICAR → Enviar email al cliente
3. ASIGNAR → Asignar curso a empleados
4. GAMIFICAR → Activar sistema de gamificación
5. MONITOREAR → Generar dashboard de analytics
6. CERTIFICAR → Emitir certificados para completadores
"""
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import M3State
from .nodes.publicacion import publicar_en_lms
from .nodes.notificacion import enviar_notificacion
from .nodes.asignacion import asignar_empleados
from .nodes.gamificacion import activar_gamificacion
from .nodes.monitoreo import generar_analytics
from .nodes.certificacion import emitir_certificados

logger = logging.getLogger(__name__)


def build_m3_graph():
    """
    Construye el grafo de LangGraph para el Macroproceso 3.
    """
    
    # Crear el grafo con el estado tipado
    graph = StateGraph(M3State)
    
    # ===== PROCESO 3.1: PUBLICACIÓN Y COMUNICACIÓN =====
    graph.add_node("PUBLICAR", publicar_en_lms)
    graph.add_node("NOTIFICAR", enviar_notificacion)
    
    # ===== PROCESO 3.2: GESTIÓN DEL APRENDIZAJE =====
    graph.add_node("ASIGNAR", asignar_empleados)
    graph.add_node("GAMIFICAR", activar_gamificacion)
    
    # ===== PROCESO 3.3: MONITOREO Y EVALUACIÓN =====
    graph.add_node("MONITOREAR", generar_analytics)
    graph.add_node("CERTIFICAR", emitir_certificados)
    
    # ===== DEFINIR EL FLUJO =====
    
    # Punto de entrada
    graph.set_entry_point("PUBLICAR")
    
    # Flujo lineal del Proceso 3.1
    graph.add_edge("PUBLICAR", "NOTIFICAR")
    
    # Transición a Proceso 3.2
    graph.add_edge("NOTIFICAR", "ASIGNAR")
    graph.add_edge("ASIGNAR", "GAMIFICAR")
    
    # Transición a Proceso 3.3
    graph.add_edge("GAMIFICAR", "MONITOREAR")
    graph.add_edge("MONITOREAR", "CERTIFICAR")
    
    # Fin del flujo
    graph.add_edge("CERTIFICAR", END)
    
    logger.info("[GRAPH] Grafo M3 construido exitosamente")
    
    return graph


def build_m3_app():
    """
    Compila el grafo con persistencia SQLite para checkpoints.
    """
    graph = build_m3_graph()
    
    # Crear el saver para persistencia
    memory = AsyncSqliteSaver.from_conn_string("m3_checkpoints.db")
    
    # Compilar el grafo
    app = graph.compile(checkpointer=memory)
    
    logger.info("[APP] Aplicación M3 compilada con persistencia")
    
    return app


# Instancia global del grafo compilado
m3_app = build_m3_app()