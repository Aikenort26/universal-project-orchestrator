# -*- coding: utf-8 -*-
"""Valida el bloque '## Resultado' del estado de una sesion hija (S11).
Uso: python resultado_purgado.py <ruta.md>  (sale con 1 si hay errores)."""
import os
import re
import sys
import urllib.parse

CAMPOS = ["veredicto", "resumen", "fases", "entregables", "verificacion", "pendientes", "riesgos"]
VEREDICTOS = {"logrado", "parcial", "fallido"}
FASES = ["handshake", "scavenge", "mapping", "ejecucion"]
REVISIONES = {"Aprobada", "Con corrección", "No aprobada"}


def extraer_bloque(texto):
    m = re.search(r"^## Resultado[ \t]*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    return m.group(0) if m else None


def _ruta(r):
    r = r.strip(" `<>")
    m = re.fullmatch(r"\[[^\]]*\]\(([^)]*)\)", r)
    if m:
        r = m.group(1).strip(" `<>")
    if r.startswith("file:///"):
        r = r[len("file:///"):]
    return urllib.parse.unquote(r)


def validar(texto, comprobar_rutas=True):
    bloque = extraer_bloque(texto)
    if bloque is None:
        return ["falta el bloque ## Resultado"]
    err = []
    campos = {}
    for c in CAMPOS:
        m = re.search(rf"^- {c}:[ \t]*(.*)$", bloque, re.M)
        v = m.group(1).strip() if m else ""
        campos[c] = v
        if not v:
            err.append(f"campo vacío o ausente: {c}")
    ver = campos["veredicto"]
    if ver and ver not in VEREDICTOS:
        err.append(f"veredicto inválido: {ver}")
    if len(campos["resumen"].split()) > 80:
        err.append("resumen de más de 80 palabras")
    if campos["fases"]:
        pares = dict(p.strip().split("=", 1) for p in campos["fases"].split(";") if "=" in p)
        for f in FASES:
            v = pares.get(f, "")
            if not (v == "aprobada" or re.fullmatch(r"omitida\(.+\)", v)):
                err.append(f"fase {f} debe ser aprobada u omitida(motivo)")
    filas = []
    for ln in bloque.splitlines():
        celdas = [c.strip() for c in ln.strip().strip("|").split("|")]
        if ln.strip().startswith("|") and len(celdas) == 5 and celdas[0] != "obrero" and not set(celdas[0]) <= {"-", ":"}:
            filas.append(celdas)
    if not filas:
        err.append("falta al menos una fila de obrero")
    for _, _, fase, intentos, rev in filas:
        if fase not in FASES:
            err.append(f"fase de obrero inválida: {fase}")
        if intentos not in ("1", "2", "3"):
            err.append(f"intentos fuera de 1 a 3: {intentos}")
        if rev not in REVISIONES:
            err.append(f"revision inválida: {rev}")
    if ver == "logrado" and any(f[4] == "No aprobada" for f in filas):
        err.append("veredicto logrado con una fila No aprobada")
    ent = campos["entregables"]
    if comprobar_rutas and ver != "fallido" and ent and ent != "ninguno":
        for r in (x.strip() for x in ent.split(";") if x.strip()):
            if not os.path.exists(_ruta(r)):
                err.append(f"entregable no existe: {r}")
    return err


if __name__ == "__main__":
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            errores = validar(f.read())
    except Exception as e:  # falla en abierto con mensaje, no traceback
        errores = [f"no se pudo leer: {e}"]
    print("\n".join(errores))
    sys.exit(1 if errores else 0)
