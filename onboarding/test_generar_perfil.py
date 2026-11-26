# -*- coding: utf-8 -*-
"""Pruebas del generador de perfil de UPO.
Ejecutar: python -m pytest test_generar_perfil.py -q -p no:cacheprovider"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import generar_perfil as gp  # noqa: E402

EJEMPLO = AQUI / "ejemplos" / "respuestas_ejemplo.json"


def respuestas():
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


def test_ejemplo_genera_dos_archivos(tmp_path):
    gp.generar(respuestas(), tmp_path)
    perfil = json.loads((tmp_path / "perfil.json").read_text(encoding="utf-8"))
    reglas = (tmp_path / "REGLAS_PERSONALES.md").read_text(encoding="utf-8")
    assert perfil["respuestas"]["idioma"] == respuestas()["idioma"]
    assert perfil["version"] == gp.VERSION
    assert reglas.startswith("# Reglas personales")
    assert "$" not in reglas.replace("$$", ""), "quedó un marcador sin reemplazar"


def test_falta_obligatoria_falla_con_mensaje(tmp_path):
    r = respuestas()
    del r["idioma"]
    with pytest.raises(gp.RespuestaInvalida, match="idioma"):
        gp.generar(r, tmp_path)
    assert not (tmp_path / "perfil.json").exists()


def test_opcion_invalida_falla(tmp_path):
    r = respuestas()
    r["plan"] = "ilimitado"
    with pytest.raises(gp.RespuestaInvalida, match="plan"):
        gp.generar(r, tmp_path)


def test_no_sobrescribe_sin_forzar(tmp_path):
    gp.generar(respuestas(), tmp_path)
    with pytest.raises(gp.PerfilExistente):
        gp.generar(respuestas(), tmp_path)
    gp.generar(respuestas(), tmp_path, forzar=True)


def test_reglas_reflejan_respuestas(tmp_path):
    r = respuestas()
    r["signos_prohibidos"] = ["punto y coma"]
    r["entregables"] = ["codigo"]
    r["delegacion_automatica"] = "nunca"
    r["acciones_externas"] = "siempre_preguntar"
    gp.generar(r, tmp_path)
    reglas = (tmp_path / "REGLAS_PERSONALES.md").read_text(encoding="utf-8")
    assert "punto y coma" in reglas
    assert "### Código" in reglas
    assert "### Presentaciones" not in reglas
    assert "Nunca delegar" in reglas
    assert "pedir aprobación" in reglas.lower()


def test_modelos_y_techos_personalizados_ganan_al_plan(tmp_path):
    r = respuestas()
    r["modelos"] = {"principal": "opus", "hijas": "opus", "obreros": "haiku"}
    r["techos"] = {"relevo_principal": 150000, "relevo_hija": 120000}
    gp.generar(r, tmp_path)
    perfil = json.loads((tmp_path / "perfil.json").read_text(encoding="utf-8"))
    assert perfil["modelos"]["obreros"] == "haiku"
    assert perfil["techos"]["relevo_hija"] == 120000
    assert "150.000" in (tmp_path / "REGLAS_PERSONALES.md").read_text(encoding="utf-8") or \
        "150,000" in (tmp_path / "REGLAS_PERSONALES.md").read_text(encoding="utf-8")


def test_cli_codigo_de_salida(tmp_path):
    cmd = [sys.executable, str(AQUI / "generar_perfil.py"), "--respuestas", str(EJEMPLO),
           "--salida", str(tmp_path)]
    ok = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert ok.returncode == 0, ok.stderr
    otra = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert otra.returncode != 0 and "--forzar" in otra.stderr


def test_texto_libre_otro(tmp_path):
    r = respuestas()
    r["formalidad"] = "otro: académico en primera persona del plural"
    r["herramientas_externas"] = ["otro: un servidor de búsqueda interno"]
    r["entregables"] = ["codigo", "otro: planos"]
    gp.generar(r, tmp_path)
    reglas = (tmp_path / "REGLAS_PERSONALES.md").read_text(encoding="utf-8")
    assert "académico en primera persona del plural" in reglas
    assert "servidor de búsqueda interno" in reglas
    assert "planos" in reglas
