# backend/graphs/m1_interaccion/nodes/mapping.py
from typing import Dict, Any

def map_node(state: Dict[str, Any]) -> Dict[str, Any]:
    comps = state.get("entidades", {}).get("competencias", [])
    state["mapping"] = {c: [f"Modulo {i+1}: {c} - Fundamentos", f"Modulo {i+1}: {c} - Práctico"]
                        for i, c in enumerate(comps)}
    return state
