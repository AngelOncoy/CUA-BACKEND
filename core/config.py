# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GRAPH_DB_PATH = os.getenv("GRAPH_DB_PATH", "./data/checkpoints/m1.sqlite")
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "./data/skills_index")
UMBRAL_CONFIANZA_NLP = float(os.getenv("UMBRAL_CONFIANZA_NLP", "0.78"))
PRICING_TARIFA_HORA = float(os.getenv("PRICING_TARIFA_HORA", "30"))
