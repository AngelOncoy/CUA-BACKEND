from typing import Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

VECTORSTORE_PATH = "./data/skills_index"

# Intentamos cargar FAISS
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    VECTORSTORE_AVAILABLE = True
except Exception:
    vectorstore = None
    VECTORSTORE_AVAILABLE = False


def validate_content_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — VALIDAR CONTENIDO
    Si FAISS no existe -> se asume contenido válido.
    """

    texto = state.get("generated_content", "")

    # ---------- FALLBACK ----------
    if not VECTORSTORE_AVAILABLE:
        return {
            "content_validated": True,
            "validation_score": None,
            "message": "FAISS no disponible, validación automática."
        }

    # ---------- MODO REAL ----------
    resultados = vectorstore.similarity_search(texto, k=1)
    score = resultados[0].metadata.get("score", 0)

    return {
        "content_validated": score >= 0.60,
        "validation_score": score
    }


def validate_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return validate_content_node(state)
