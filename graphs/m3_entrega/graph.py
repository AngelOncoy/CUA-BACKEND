# graphs/m3_entrega/graph.py
"""
Grafo Principal del Macroproceso 3: Entrega y Administración del Aprendizaje
"""

import logging
import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .state import M3State
from .nodes.publicacion import publicar_en_lms
from .nodes.notificacion import enviar_notificaciones
from .nodes.asignacion import asignar_empleados
from .nodes.gamificacion import preparar_gamificacion
from .nodes.monitoreo import generar_analytics
from .nodes.certificacion import generar_certificados
from .nodes.utils import inicializar_estado

logger = logging.getLogger(__name__)


def build_m3_graph():
    graph = StateGraph(M3State)

    # INICIALIZACIÓN
    graph.add_node("INICIALIZAR", inicializar_estado)

    # PROCESO 3.1
    graph.add_node("PUBLICAR", publicar_en_lms)
    graph.add_node("NOTIFICAR", enviar_notificaciones)

    # PROCESO 3.2
    graph.add_node("ASIGNAR", asignar_empleados)
    graph.add_node("GAMIFICAR", preparar_gamificacion)

    # PROCESO 3.3
    graph.add_node("MONITOREAR", generar_analytics)
    graph.add_node("CERTIFICAR", generar_certificados)

    # FLUJO
    graph.set_entry_point("INICIALIZAR")
    graph.add_edge("INICIALIZAR", "PUBLICAR")
    graph.add_edge("PUBLICAR", "NOTIFICAR")
    graph.add_edge("NOTIFICAR", "ASIGNAR")
    graph.add_edge("ASIGNAR", "GAMIFICAR")
    graph.add_edge("GAMIFICAR", "MONITOREAR")
    graph.add_edge("MONITOREAR", "CERTIFICAR")
    graph.add_edge("CERTIFICAR", END)

    logger.info("[GRAPH] Grafo M3 construido exitosamente")
    return graph


def build_m3_app():
    """
    Construye y compila la aplicación M3 sin persistencia.
    Para workflows simples que no requieren reanudar estado entre sesiones.
    """
    graph = build_m3_graph()
    
    # Compilar sin checkpointer para soportar métodos async
    app = graph.compile()
    logger.info("[APP] Aplicación M3 compilada sin persistencia")
    return app


m3_app = build_m3_app()
