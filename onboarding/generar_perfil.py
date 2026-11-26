# -*- coding: utf-8 -*-
"""Genera perfil.json y REGLAS_PERSONALES.md a partir de las respuestas del cuestionario.

Uso:
  python generar_perfil.py --respuestas respuestas.json [--salida ~/.claude/upo] [--forzar]

Solo biblioteca estándar. Las reglas salen de los fragmentos de plantillas/.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from string import Template

VERSION = 1
PLANTILLAS = Path(__file__).parent / "plantillas"

# Valores por plan. Los techos son tokens de contexto en que la sesión escribe HANDOFF.md y se releva.
PLANES = {
    "basico": {"modelos": {"principal": "sonnet", "hijas": "sonnet", "obreros": "haiku"},
               "techos": {"relevo_principal": 120000, "relevo_hija": 100000}},
    "medio": {"modelos": {"principal": "opus", "hijas": "sonnet", "obreros": "sonnet"},
              "techos": {"relevo_principal": 150000, "relevo_hija": 120000}},
    "alto": {"modelos": {"principal": "opus", "hijas": "opus", "obreros": "sonnet"},
             "techos": {"relevo_principal": 300000, "relevo_hija": 240000}},
}

OPCIONES = {
    "entregables": {"informes", "articulos", "codigo", "presentaciones", "hojas_calculo"},
    "formalidad": {"formal", "tecnica", "cercana"},
    "formato_numeros": {"punto_miles", "coma_miles", "espacio_miles"},
    "formato_fecha": {"iso", "dia_mes_anio", "mes_dia_anio"},
    "ubicacion_trabajo": {"nube_sincronizada", "local", "repositorio"},
    "convencion_nombres": {"minusculas_guiones", "prefijo_numerico", "fecha_prefijo"},
    "plan": set(PLANES) | {"personalizado"},
    "herramientas_externas": {"segundo_agente", "modelo_local"},
    "delegacion_automatica": {"nunca", "solo_lectura", "siempre"},
    "puertas_humanas": {"plan", "entrega", "borrado", "gasto", "redaccion_en_mi_nombre"},
    "acciones_externas": {"siempre_preguntar", "push_libre", "todo_libre"},
}
OBLIGATORIAS = ["idioma", "dominio", "entregables", "formalidad", "formato_numeros", "formato_fecha",
                "ubicacion_trabajo", "plan", "delegacion_automatica", "puertas_humanas", "acciones_externas"]
LISTAS = {"entregables", "signos_prohibidos", "herramientas_externas", "puertas_humanas"}
POR_DEFECTO = {"signos_prohibidos": [], "herramientas_externas": [], "raiz_trabajo": "la carpeta de cada proyecto",
               "convencion_nombres": "minusculas_guiones", "alias": ""}
# "plan" no admite texto libre: define modelos y techos. Las demás opciones aceptan "otro: <texto>".
SIN_TEXTO_LIBRE = {"plan"}


class RespuestaInvalida(ValueError):
    pass


class PerfilExistente(FileExistsError):
    pass


def _es_libre(v):
    return isinstance(v, str) and v.lower().startswith("otro:") and v[5:].strip()


def validar(r):
    if not isinstance(r, dict):
        raise RespuestaInvalida("las respuestas deben ser un objeto JSON")
    faltan = [k for k in OBLIGATORIAS if r.get(k) in (None, "", [])]
    if faltan:
        raise RespuestaInvalida("faltan respuestas obligatorias: " + ", ".join(faltan))
    out = {**POR_DEFECTO, **r}
    for k, ok in OPCIONES.items():
        if k not in out:
            continue
        vals = out[k] if k in LISTAS else [out[k]]
        if k in LISTAS and not isinstance(out[k], list):
            raise RespuestaInvalida(f"{k} debe ser una lista")
        for v in vals:
            if v not in ok and (k in SIN_TEXTO_LIBRE or not _es_libre(v)):
                raise RespuestaInvalida(f"{k}: valor no reconocido {v!r}; opciones: {', '.join(sorted(ok))}"
                                        + ("" if k in SIN_TEXTO_LIBRE else " o 'otro: <texto>'"))
    if out["plan"] == "personalizado" and not (out.get("modelos") and out.get("techos")):
        raise RespuestaInvalida("plan 'personalizado' exige 'modelos' y 'techos'")
    base = PLANES.get(out["plan"], {"modelos": {}, "techos": {}})
    out["modelos"] = {**base["modelos"], **(out.get("modelos") or {})}
    out["techos"] = {**base["techos"], **(out.get("techos") or {})}
    for k in ("principal", "hijas", "obreros"):
        if not out["modelos"].get(k):
            raise RespuestaInvalida(f"modelos.{k} es obligatorio")
    for k in ("relevo_principal", "relevo_hija"):
        if not isinstance(out["techos"].get(k), int) or out["techos"][k] <= 0:
            raise RespuestaInvalida(f"techos.{k} debe ser un entero positivo")
    return out


def numero(n, formato):
    s = f"{n:,}"
    return {"punto_miles": s.replace(",", "."), "espacio_miles": s.replace(",", " ")}.get(formato, s)


def bloques(nombre):
    """Lee plantillas/<nombre>.md y devuelve {bloque: texto}. El bloque '_' es lo previo al primer marcador."""
    texto = (PLANTILLAS / f"{nombre}.md").read_text(encoding="utf-8")
    partes = re.split(r"^<!-- bloque: (\S+) -->\s*$", texto, flags=re.M)
    out = {"_": partes[0].strip()}
    for i in range(1, len(partes), 2):
        out[partes[i]] = partes[i + 1].strip()
    return out


def elegir(nombre, clave, campo):
    b = bloques(nombre)
    if _es_libre(clave):
        return b["otro_" + campo].replace("$texto", clave[5:].strip())
    return b[clave]


def componer(r):
    lista = lambda xs, vacio: "\n".join(f"  - {x}" for x in xs) if xs else f"  - {vacio}"  # noqa: E731
    libres = [x[5:].strip() for x in r["entregables"] if _es_libre(x)]
    v = {
        "idioma": r["idioma"], "dominio": r["dominio"], "alias": r["alias"] or "la persona usuaria",
        "fecha": date.today().isoformat(), "raiz_trabajo": r["raiz_trabajo"],
        "signos_prohibidos": lista(r["signos_prohibidos"], "Ninguno declarado."),
        "modelo_principal": r["modelos"]["principal"], "modelo_hijas": r["modelos"]["hijas"],
        "modelo_obreros": r["modelos"]["obreros"],
        "relevo_principal": numero(r["techos"]["relevo_principal"], r["formato_numeros"]),
        "relevo_hija": numero(r["techos"]["relevo_hija"], r["formato_numeros"]),
        "ejemplo_numero": numero(1234567, r["formato_numeros"]),
    }
    secciones = [
        bloques("00_encabezado")["_"],
        bloques("10_universal")["_"],
        bloques("20_redaccion")["_"],
        elegir("20_redaccion", r["formalidad"], "formalidad"),
        elegir("20_redaccion", r["formato_numeros"], "formato_numeros"),
        elegir("20_redaccion", r["formato_fecha"], "formato_fecha"),
        bloques("30_organizacion")["_"],
        elegir("30_organizacion", r["ubicacion_trabajo"], "ubicacion_trabajo"),
        elegir("30_organizacion", r["convencion_nombres"], "convencion_nombres"),
        bloques("40_modelos")["_"],
        bloques("50_delegacion")["_"],
        elegir("50_delegacion", r["delegacion_automatica"], "delegacion_automatica"),
    ]
    secciones += [elegir("50_delegacion", h, "herramientas_externas") for h in r["herramientas_externas"]]
    secciones += [bloques("60_autonomia")["_"]]
    secciones += [elegir("60_autonomia", p, "puertas_humanas") for p in r["puertas_humanas"]]
    secciones += [elegir("60_autonomia", r["acciones_externas"], "acciones_externas")]
    ent = bloques("70_entregables")
    secciones += [ent["_"]] + [ent[e] for e in r["entregables"] if e in ent]
    if libres:
        secciones += ["### Otros entregables\n" + "\n".join(f"- {x}: acordar formato y verificación en el arranque."
                                                         for x in libres)]
    texto = Template("\n\n".join(s for s in secciones if s)).safe_substitute(v)
    # une en una sola lista las viñetas que vienen de bloques distintos
    return re.sub(r"\n\n(?=- )", "\n", texto).rstrip() + "\n"


def generar(respuestas, salida, forzar=False):
    r = validar(respuestas)
    salida = Path(salida).expanduser()
    destinos = [salida / "perfil.json", salida / "REGLAS_PERSONALES.md"]
    if not forzar and any(d.exists() for d in destinos):
        raise PerfilExistente(f"ya existe un perfil en {salida}; use --forzar para rehacerlo")
    reglas = componer(r)
    salida.mkdir(parents=True, exist_ok=True)
    perfil = {"version": VERSION, "creado": date.today().isoformat(), "respuestas": respuestas,
              "modelos": r["modelos"], "techos": r["techos"]}
    destinos[0].write_text(json.dumps(perfil, ensure_ascii=False, indent=2), encoding="utf-8")
    destinos[1].write_text(reglas, encoding="utf-8")
    return destinos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--respuestas", required=True, help="JSON con las respuestas del cuestionario")
    ap.add_argument("--salida", default="~/.claude/upo", help="carpeta destino (por defecto ~/.claude/upo)")
    ap.add_argument("--forzar", action="store_true", help="rehacer un perfil existente")
    a = ap.parse_args(argv)
    try:
        datos = json.loads(Path(a.respuestas).read_text(encoding="utf-8"))
        for d in generar(datos, a.salida, a.forzar):
            print(d)
    except (RespuestaInvalida, PerfilExistente, json.JSONDecodeError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
