# graphs/m1_interaccion/nodes/pricing.py
from typing import Dict, Any
from core.config import PRICING_TARIFA_HORA

def pricing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    horas = 12
    licencias = 10
    subtotal = horas * PRICING_TARIFA_HORA
    total = subtotal + licencias
    state["precio"] = {
        "horas": horas,
        "tarifa_h": PRICING_TARIFA_HORA,
        "subtotal": subtotal,
        "licencias": licencias,
        "total": total,
        "moneda": "USD"
    }
    return state
