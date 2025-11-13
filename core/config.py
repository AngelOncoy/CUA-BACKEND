# core/config.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GRAPH_DB_PATH = os.getenv("GRAPH_DB_PATH")
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH")
UMBRAL_CONFIANZA_NLP = float(os.getenv("UMBRAL_CONFIANZA_NLP", "0.78"))
PRICING_TARIFA_HORA = float(os.getenv("PRICING_TARIFA_HORA", "30"))
PAYPAL_CLIENT_ID="AeYg6exHd4glD74JDaHGR7sQLgFRbj4S8tYdvzBNoUIQzCBFnzIRE34EySK7JLV6q-ERJqtoMmg3nxe7"
PAYPAL_CLIENT_SECRET="EIR6pcjg8awja58Hm353vGRL6cw_EBJfllMEoe9JyHzFkYwWc7yM9RtBbRiakUnNDGm6eAEp0RISWfUr"
PAYPAL_MODE = "sandbox"  # o "live"

