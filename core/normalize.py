from __future__ import annotations
from typing import Any, Dict, List
from collections import OrderedDict
import json, os

# ---------- Utilidades ----------

def _clean_empty(v: Any) -> Any:
    # Normaliza strings vacíos a None en campos descriptivos
    if isinstance(v, str) and v.strip() == "":
        return None
    return v

def _uniq(seq: List[Dict], key: str) -> List[Dict]:
    seen = set()
    out = []
    for x in seq:
        k = x.get(key)
        if k and k not in seen:
            out.append(x)
            seen.add(k)
        elif not k:  # si no hay key, deja pasar 1
            out.append(x)
    return out

def _sorted_by(items: List[Dict], *keys: str) -> List[Dict]:
    def _key(d):
        return tuple((d.get(k) or "").lower() for k in keys)
    return sorted(items, key=_key)

def _order_multimedia(items: List[Dict]) -> List[Dict]:
    # Orden semántico: tipo, prompt, descripcion, url
    out = []
    for it in items:
        it = {
            "tipo": it.get("tipo"),
            "prompt": _clean_empty(it.get("prompt")),
            "descripcion": _clean_empty(it.get("descripcion")),
            "url": it.get("url")  # puede ser None y está bien
        }
        out.append(it)
    # orden estable por tipo -> prompt
    return _sorted_by(out, "tipo", "prompt")

def _order_eval_form(items: List[Dict]) -> List[Dict]:
    # Orden: tipo, enunciado, respuesta
    out = []
    for it in items:
        out.append(OrderedDict([
            ("tipo", it.get("tipo")),
            ("enunciado", it.get("enunciado")),
            ("respuesta", it.get("respuesta")),
        ]))
    # orden estable por tipo -> enunciado
    return _sorted_by(out, "tipo", "enunciado")

def _order_leccion(lec: Dict[str, Any]) -> Dict[str, Any]:
    # Lección: titulo, objetivos, contenido{introduccion, conceptos_clave, procedimientos, ejemplos, errores_comunes, glosario}, actividad_practica, evaluacion_formativa, lecturas_sugeridas, multimedia
    contenido = lec.get("contenido") or {}
    procedimientos = contenido.get("procedimientos") or []
    ejemplos = contenido.get("ejemplos") or []
    glosario = contenido.get("glosario") or []
    errores = contenido.get("errores_comunes") or []
    conceptos = contenido.get("conceptos_clave") or []

    # Normaliza orden interno de contenido
    contenido_od = OrderedDict([
        ("introduccion", _clean_empty(contenido.get("introduccion"))),
        ("conceptos_clave", conceptos),
        ("procedimientos", procedimientos),
        ("ejemplos", ejemplos),
        ("errores_comunes", errores),
        ("glosario", glosario),
    ])

    ev_form = _order_eval_form(lec.get("evaluacion_formativa") or [])
    multimedia = _order_multimedia(lec.get("multimedia") or [])

    # Construye la lección ordenada
    out = OrderedDict([
        ("titulo", lec.get("titulo")),
        ("objetivos", lec.get("objetivos") or []),
        ("contenido", contenido_od),
        ("actividad_practica", _clean_empty(lec.get("actividad_practica"))),
        ("evaluacion_formativa", ev_form),
        ("lecturas_sugeridas", lec.get("lecturas_sugeridas") or []),
        ("multimedia", multimedia),
    ])
    return out

def _order_unidad(uni: Dict[str, Any]) -> Dict[str, Any]:
    lecciones = [_order_leccion(l) for l in (uni.get("lecciones") or [])]
    lecciones = _sorted_by(lecciones, "titulo")
    return OrderedDict([
        ("titulo", uni.get("titulo")),
        ("descripcion", _clean_empty(uni.get("descripcion"))),
        ("lecciones", lecciones),
    ])

def _order_modulo(mod: Dict[str, Any]) -> Dict[str, Any]:
    unidades = [_order_unidad(u) for u in (mod.get("unidades") or [])]
    unidades = _sorted_by(unidades, "titulo")
    return OrderedDict([
        ("titulo", mod.get("titulo")),
        ("descripcion", _clean_empty(mod.get("descripcion"))),
        ("horas", mod.get("horas")),
        ("unidades", unidades),
        # Campos opcionales tipo overview/key_points/procedures si existieran
        *[(k, mod[k]) for k in ["overview", "key_points", "procedures"] if k in mod],
    ])

def _order_curso(curso: Dict[str, Any]) -> Dict[str, Any]:
    modulos = [_order_modulo(m) for m in (curso.get("modulos") or [])]
    modulos = _sorted_by(modulos, "titulo")
    # Estructura general del plan del curso
    plan = curso.get("plan") or {}
    # Secciones superiores (si existen): rubrica, proyecto, faq
    rubrica = plan.get("rubrica") or curso.get("rubrica") or []
    proyecto = plan.get("proyecto") or curso.get("proyecto") or None
    faq = plan.get("faq") or curso.get("faq") or []

    out = OrderedDict([
        ("curso", curso.get("curso")),
        ("nivel", curso.get("nivel")),
        ("resultados_aprendizaje", curso.get("resultados_aprendizaje") or []),
        ("modulos", modulos),
    ])

    if proyecto:
        # Ordena proyecto (criterios y entregables)
        pj = OrderedDict([
            ("titulo", proyecto.get("titulo")),
            ("enunciado", proyecto.get("enunciado")),
            ("entregables", proyecto.get("entregables") or []),
            ("criterios_rubrica", proyecto.get("criterios_rubrica") or []),
        ])
        out["proyecto"] = pj

    if rubrica:
        out["rubrica"] = rubrica

    if faq:
        # Normaliza orden Q/A por pregunta
        out["faq"] = _sorted_by(faq, "q")

    return out

def _order_assets(assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Cada asset: modulo, queries_sugeridas, synthesis{overview, key_points, procedures}, referencias/multimedia
    out = []
    for a in assets or []:
        syn = a.get("synthesis") or {}
        syn_od = OrderedDict([
            ("overview", _clean_empty(syn.get("overview"))),
            ("key_points", syn.get("key_points") or []),
            ("procedures", syn.get("procedures") or []),
        ])
        out.append(OrderedDict([
            ("modulo", a.get("modulo")),
            ("queries_sugeridas", a.get("queries_sugeridas") or []),
            ("synthesis", syn_od),
            # Mantén otros campos si existieran (p.ej. referencias)
            *[(k, a[k]) for k in ["referencias", "multimedia"] if k in a],
        ]))
    return _sorted_by(out, "modulo")

def canonicalize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve un nuevo dict con orden lógico estable para exportar.
    No muta el 'state' original.
    """
    curso = state.get("curso_m2") or state.get("curso_final") or {}
    curso_ord = _order_curso(curso)

    assets = _order_assets(state.get("assets") or [])

    # Orden tope del state exportado:
    out = OrderedDict([
        ("run_id", state.get("run_id")),
        ("entidades", state.get("entidades") or {}),
        ("curso", curso_ord),               # renombrado para el export
        ("assets", assets),
        ("config", state.get("config") or {}),
        ("bundle_hash", state.get("bundle_hash")),
    ])
    return out

def dump_canonical_state(state: Dict[str, Any], path: str) -> None:
    canon = canonicalize_state(state)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(canon, f, ensure_ascii=False, indent=2)