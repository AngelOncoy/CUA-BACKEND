from typing import Dict, Any
from .schemas import M2Input, Entidades
from bs4 import BeautifulSoup

def parse_m1_html(html: str) -> Dict[str, Any]:
    """Extrae información clave desde la propuesta HTML generada por el M1."""
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # Título del curso
    h2 = soup.find("h2")
    data["curso"] = h2.text.replace("Propuesta Ejecutiva: ", "") if h2 else "Curso sin título"

    # Nivel
    nivel = "Avanzado" if "Avanzado" in html else "Básico"
    data["nivel"] = nivel

    # Módulos
    modulos = []
    for mod in soup.find_all("h4"):
        titulo = mod.text.strip()
        descripcion = mod.find_next("li").text if mod.find_next("li") else ""
        horas = 0
        for li in mod.find_all_next("li"):
            if "Horas Estimadas" in li.text:
                try:
                    horas = int(li.text.split(":")[-1].split()[0])
                except:
                    horas = 0
                break
        modulos.append({
            "titulo": titulo,
            "descripcion": descripcion,
            "horas": horas
        })
    data["modulos"] = modulos

    # Resultados de aprendizaje
    resultados = [
        li.text for li in soup.find_all("li")
        if any(word in li.text for word in ["Analizar", "Diseñar", "Implementar", "Optimizar", "Gestionar", "Evaluar"])
    ]
    data["resultados_aprendizaje"] = resultados

    # Precio total
    try:
        total_text = [li.text for li in soup.find_all("li") if "Precio Total" in li.text][0]
        data["precio_total"] = float(total_text.split(":")[-1].split()[0])
    except:
        data["precio_total"] = None

    return data


def m1_to_m2_input(m1_state: Dict[str, Any], run_id: str | None = None) -> M2Input:
    """Convierte la salida del M1 en el input estructurado del M2."""
    html = m1_state.get("propuesta_html", "")
    parsed = parse_m1_html(html)

    entidades = Entidades(
        industria="Educación",
        nivel=parsed.get("nivel", ""),
        competencias=[parsed.get("curso", "")],
        confianza=1.0,
    )

    return M2Input(
        run_id=run_id or m1_state.get("run_id"),
        entidades=entidades,
        syllabus_md=str(parsed),
        mapping={"modulos": parsed.get("modulos")},
    )