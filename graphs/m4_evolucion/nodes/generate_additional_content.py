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
from langchain_google_genai import ChatGoogleGenerativeAI

VECTORSTORE_PATH = "./data/skills_index"

embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

def generate_additional_content_node(state):
    """
    NODO M4 — GENERAR CONTENIDO COMPLEMENTARIO
    """

    brechas = state.get("gap_details", [])
    if not brechas:
        return {"generated_content": "No se detectaron brechas."}

    textos = []

    for b in brechas:
        similares = vectorstore.similarity_search(b["tema"], k=3)
        relacionados = [doc.page_content for doc in similares]

        prompt = f"""
        Genera contenido complementario para el tema '{b["tema"]}'.
        Usa estos módulos de referencia:
        {relacionados}
        """

        respuesta = llm.invoke(prompt)
        textos.append(str(respuesta))

    return {"generated_content": "\n\n".join(textos)}
