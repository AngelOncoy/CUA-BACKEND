from typing import Dict, Any, TYPE_CHECKING
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY, GEMINI_MODEL
from core.utils import timed_node
import os

# Inicializar el modelo de IA
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# Función para leer el archivo de prompt
def read_file(file_path: str) -> str:
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(dir_actual, file_path)

    with open(prompt_file_path, "r", encoding="utf-8") as file:
        return file.read()


# Cargar el prompt de propuesta desde el archivo
prompt_prop_text = read_file("prompts/prompt_prop.txt")

# Crear el ChatPromptTemplate con el nuevo prompt
prompt_prop = ChatPromptTemplate.from_messages([
    ("system", prompt_prop_text),
    ("user", "Sílabus:\n{syllabus}\nPrecio:\n{precio}")
])


@timed_node
def proposal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log.info("Generando propuesta ejecutiva...")

    # Generar la propuesta ejecutiva usando el modelo de IA
    html = (prompt_prop | llm).invoke({
        "syllabus": state.get("syllabus", {}),
        "precio": state.get("precio", {})
    })

    # Almacenar la propuesta generada en el estado
    state["propuesta_html"] = str(html.content)
    log.info("Propuesta generada correctamente. Esperando aprobación.")

    return state


# Función de enrutamiento para la decisión de aprobación
def approval_router(state: "M1State") -> str:
    decision = state.get("decision")
    log.info(f"Evaluando decisión del usuario → {decision}")

    # Si el usuario aprueba la propuesta
    if decision == "APROBADO":
        log.info("Flujo finalizado con aprobación.")
        return "END"  # Finaliza el flujo del Macroproceso 1 y continúa al siguiente

    # Si el usuario rechaza la propuesta
    elif decision == "RECHAZADO":
        log.info("Flujo finalizado con rechazo.")
        return "END"  # También termina el flujo del Macroproceso 1

    # Si el usuario necesita aclaraciones
    elif decision == "ACLARAR":
        log.info("Volviendo a nodo ASK para aclaraciones.")
        return "ASK"  # Regresa al nodo de aclaraciones (si es necesario)

    # Si la decisión es desconocida o no tomada, espera la entrada del usuario
    log.info("Esperando decisión del usuario (estado WAIT).")
    return "WAIT"  # Este estado indica que el flujo debe esperar una acción o decisión del usuario

