import os
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

class VectorManager:
    def __init__(self, persist_path: str = None):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en .env")
        
        # Ruta de persistencia (puedes ajustarla en tu .env o usar el default)
        self.persist_path = persist_path or os.getenv("VECTORSTORE_PATH", "./data/skills_index")
        
        # Configuración de Embeddings con Google (Gemini)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=self.api_key
        )
        
        # Inicializar ChromaDB
        self.db = Chroma(
            persist_directory=self.persist_path,
            embedding_function=self.embeddings,
            collection_name="curso_contexto"
        )

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Agrega textos a la base de datos vectorial."""
        if not texts:
            return
        self.db.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Busca los fragmentos más relevantes para la query."""
        return self.db.similarity_search(query, k=k)