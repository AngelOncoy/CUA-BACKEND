# graphs/m3_entrega/graph.py
"""
Grafo Principal del Macroproceso 3: Entrega y Administración del Aprendizaje
"""

import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .state import M3State
from .nodes.publicacion import publicar_en_lms
from .nodes.notificacion import enviar_notificaciones
from .nodes.asignacion import asignar_empleados
from .nodes.gamificacion import preparar_gamificacion
from .nodes.monitoreo import actualizar_analytics
from .nodes.certificacion import generar_certificados

logger = logging.getLogger(__name__)


def build_m3_graph():
    graph = StateGraph(M3State)

    # PROCESO 3.1
    graph.add_node("PUBLICAR", publicar_en_lms)
    graph.add_node("NOTIFICAR", enviar_notificaciones)

    # PROCESO 3.2
    graph.add_node("ASIGNAR", asignar_empleados)
    graph.add_node("GAMIFICAR", preparar_gamificacion)

    # PROCESO 3.3
    graph.add_node("MONITOREAR", actualizar_analytics)
    graph.add_node("CERTIFICAR", generar_certificados)

    # FLUJO
    graph.set_entry_point("PUBLICAR")
    graph.add_edge("PUBLICAR", "NOTIFICAR")
    graph.add_edge("NOTIFICAR", "ASIGNAR")
    graph.add_edge("ASIGNAR", "GAMIFICAR")
    graph.add_edge("GAMIFICAR", "MONITOREAR")
    graph.add_edge("MONITOREAR", "CERTIFICAR")
    graph.add_edge("CERTIFICAR", END)

    logger.info("[GRAPH] Grafo M3 construido exitosamente")
    return graph


def build_m3_app():
    graph = build_m3_graph()
    memory = AsyncSqliteSaver.from_conn_string("m3_checkpoints.db")
    app = graph.compile(checkpointer=memory)
    logger.info("[APP] Aplicación M3 compilada con persistencia")
    return app


m3_app = build_m3_app()
