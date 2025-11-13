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

def validate_content_node(state):
    """
    NODO M4 — VALIDAR CONTENIDO
    """

    texto = state.get("generated_content", "")

    resultados = vectorstore.similarity_search(texto, k=1)
    score = resultados[0].metadata.get("score", 0)

    return {
        "content_validated": score >= 0.60,
        "validation_score": score
    }
