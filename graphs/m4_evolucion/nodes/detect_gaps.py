from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

VECTORSTORE_PATH = "./data/skills_index"

# Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")

# Vectorstore FAISS del M2
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

VECTORSTORE_PATH = "./data/skills_index"
embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

def detect_gaps_node(state):
    """
    NODO M4 — DETECTAR BRECHAS USANDO FAISS
    """

    temas = state.get("course_data", {}).get("temas", [])
    brechas = []

    for tema in temas:
        resultados = vectorstore.similarity_search(tema, k=1)
        score = resultados[0].metadata.get("score", 0)

        if score < 0.70:
            brechas.append({
                "tema": tema,
                "score": score,
                "motivo": "baja similitud con competencias existentes"
            })

    return {
        "gaps_detected": len(brechas) > 0,
        "gap_details": brechas
    }
