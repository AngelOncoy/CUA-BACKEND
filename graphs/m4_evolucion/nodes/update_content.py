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


def update_content_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — ACTUALIZAR CONTENIDO FINAL
    Si FAISS no existe -> retorna contenido simple.
    """

    texto = state.get("generated_content", "")

    # ---------- FALLBACK ----------
    if not VECTORSTORE_AVAILABLE:
        return {
            "updated_content": f"""
            === CONTENIDO FINAL (sin FAISS) ===
            {texto}
            """
        }

    # ---------- MODO REAL ----------
    similares = vectorstore.similarity_search(texto, k=3)
    modulos = "\n".join([doc.page_content for doc in similares])

    final = f"""
    === CONTENIDO FINAL ACTUALIZADO ===

    {texto}

    === MÓDULOS RELACIONADOS ===
    {modulos}
    """

    return {"updated_content": final}


def update_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return update_content_node(state)
