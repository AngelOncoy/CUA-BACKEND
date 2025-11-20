# graphs/m3_entrega/nodes/utils.py

import os


def load_prompt(filename: str) -> str:
    """
    Carga un archivo de prompt desde la carpeta 'prompts'
    ubicada en el mismo directorio que este módulo.
    """
    base_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(base_dir, "prompts", filename)

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback: si no se encuentra, devolvemos un texto mínimo
        return f"[WARNING] Prompt file '{filename}' not found."
