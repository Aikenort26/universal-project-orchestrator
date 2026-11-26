#!/usr/bin/env python3
"""Validador de la skill universal-project-orchestrator (UPO).

Solo biblioteca estandar de Python 3.
Comprueba estructura, limites de lineas, sintaxis JSON, esquemas,
skills/agentes citados, rutas absolutas y enrutado.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Validador de la skill universal-project-orchestrator"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Imprimir solo fallas y el resultado",
    )
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    raiz = scripts_dir.parent

    # Skills y agentes instalados del usuario (opcionales: su ausencia es aviso, no falla)
    claude_dir = Path.home() / ".claude"
    skills_dir = claude_dir / "skills"
    claude_agents_dir = claude_dir / "agents"

    total_fallas = 0

    def avisar(nombre, avisos):
        if not args.quiet:
            for a in avisos:
                print(f"AVISO {nombre}: {a}")

    def reportar(nombre, errores):
        nonlocal total_fallas
        if not errores:
            if not args.quiet:
                print(f"OK {nombre}")
        else:
            for err in errores:
                total_fallas += 1
                print(f"FALLA {nombre}: {err}")

    # 1. existe SKILL.md y tiene como maximo 120 lineas; frontmatter con name y description
    skill_md = raiz / "SKILL.md"
    err1 = []
    if not skill_md.is_file():
        err1.append("SKILL.md no existe")
    else:
        try:
            content = skill_md.read_text(encoding="utf-8")
            lines = content.splitlines()
            if len(lines) > 120:
                err1.append(f"SKILL.md supera 120 lineas (tiene {len(lines)})")

            has_fm = False
            fm_text = ""
            if lines and lines[0].strip() == "---":
                for idx in range(1, len(lines)):
                    if lines[idx].strip() == "---":
                        has_fm = True
                        fm_text = "\n".join(lines[1:idx])
                        break
            if not has_fm:
                err1.append("SKILL.md no contiene frontmatter delimitado por '---'")
            else:
                has_name = bool(re.search(r"^name\s*:", fm_text, re.MULTILINE))
                has_desc = bool(re.search(r"^description\s*:", fm_text, re.MULTILINE))
                if not has_name:
                    err1.append("frontmatter no contiene campo 'name'")
                if not has_desc:
                    err1.append("frontmatter no contiene campo 'description'")
        except Exception as e:
            err1.append(f"error al leer SKILL.md: {e}")
    reportar("skill_md", err1)

    # 2. cada references/*.md tiene como maximo 150 lineas
    ref_dir = raiz / "references"
    err2 = []
    if ref_dir.is_dir():
        for rf in sorted(ref_dir.glob("*.md")):
            try:
                lines = rf.read_text(encoding="utf-8").splitlines()
                if len(lines) > 150:
                    err2.append(f"{rf.name} supera 150 lineas (tiene {len(lines)})")
            except Exception as e:
                err2.append(f"error al leer {rf.name}: {e}")
    reportar("references_lineas", err2)

    # 3. en SKILL.md y references/*.md: cero caracteres U+00A7 y U+2014 (informar archivo:linea)
    err3 = []
    md_files = []
    if skill_md.is_file():
        md_files.append(skill_md)
    if ref_dir.is_dir():
        md_files.extend(sorted(ref_dir.glob("*.md")))

    for mf in md_files:
        try:
            lines = mf.read_text(encoding="utf-8").splitlines()
            for num, line in enumerate(lines, 1):
                if "\u00a7" in line:
                    err3.append(f"{mf.name}:{num} contiene caracter U+00A7")
                if "\u2014" in line:
                    err3.append(f"{mf.name}:{num} contiene caracter U+2014")
        except Exception as e:
            err3.append(f"error al leer {mf.name}: {e}")
    reportar("caracteres_prohibidos", err3)

    # 4. workflow.json, adapter_schema.json y dominios/*.json son JSON validos
    err4 = []
    json_files = [raiz / "workflow.json", raiz / "adapter_schema.json"]
    dom_dir = raiz / "dominios"
    if dom_dir.is_dir():
        json_files.extend(sorted(dom_dir.glob("*.json")))

    parsed_jsons = {}
    for jf in json_files:
        if not jf.is_file():
            err4.append(f"{jf.name} no existe")
        else:
            try:
                parsed_jsons[jf.name] = json.loads(jf.read_text(encoding="utf-8"))
            except Exception as e:
                err4.append(f"{jf.name} no es JSON valido: {e}")
    reportar("json_sintaxis", err4)

    # 5. cada dominios/*.json cumple adapter_schema.json
    err5 = []
    schema_data = parsed_jsons.get("adapter_schema.json")
    if not schema_data:
        err5.append("adapter_schema.json no esta disponible para validacion")
    else:
        req_keys = schema_data.get("required", [])
        props = schema_data.get("properties", {})
        add_props = schema_data.get("additionalProperties", True)

        if dom_dir.is_dir():
            for df in sorted(dom_dir.glob("*.json")):
                ddata = parsed_jsons.get(df.name)
                if not isinstance(ddata, dict):
                    continue
                # claves requeridas
                for rk in req_keys:
                    if rk not in ddata:
                        err5.append(f"{df.name}: falta clave requerida '{rk}'")
                # additionalProperties false
                if add_props is False:
                    for k in ddata:
                        if k not in props:
                            err5.append(f"{df.name}: clave no permitida '{k}'")
                # validacion de propiedades
                for k, v in ddata.items():
                    if k not in props:
                        continue
                    pdef = props[k]
                    ptype = pdef.get("type")
                    if ptype == "string":
                        if not isinstance(v, str):
                            err5.append(f"{df.name}: '{k}' debe ser string")
                        else:
                            pat = pdef.get("pattern")
                            if pat and not re.search(pat, v):
                                err5.append(f"{df.name}: '{k}' no coincide con patron '{pat}'")
                            enum_vals = pdef.get("enum")
                            if enum_vals and v not in enum_vals:
                                err5.append(f"{df.name}: '{k}' valor '{v}' no pertenece al enum")
                    elif ptype == "array":
                        if not isinstance(v, list):
                            err5.append(f"{df.name}: '{k}' debe ser array")
                        else:
                            min_items = pdef.get("minItems")
                            if min_items is not None and len(v) < min_items:
                                err5.append(f"{df.name}: '{k}' tiene {len(v)} items (minimo {min_items})")
                            item_type = pdef.get("items", {}).get("type")
                            if item_type == "string":
                                for item in v:
                                    if not isinstance(item, str):
                                        err5.append(f"{df.name}: '{k}' contiene elemento no string: {item}")
    reportar("adapter_schema", err5)

    # 6. cada skill citada en dominios existe como ~/.claude/skills/<nombre>/SKILL.md;
    #    cada agente de agentes_rol existe como ~/.claude/agents/<nombre>.md (aviso si falta)
    err6 = []
    if dom_dir.is_dir():
        for df in sorted(dom_dir.glob("*.json")):
            ddata = parsed_jsons.get(df.name)
            if not isinstance(ddata, dict):
                continue
            for sk in ddata.get("skills", []):
                sk_file = skills_dir / sk / "SKILL.md"
                if not sk_file.is_file():
                    err6.append(f"{df.name}: skill '{sk}' no existe en {sk_file}")
            for ag in ddata.get("agentes_rol", []):
                ag_file = claude_agents_dir / f"{ag}.md"
                if not ag_file.is_file():
                    err6.append(f"{df.name}: agente '{ag}' no instalado en {ag_file}")
    avisar("skills_y_agentes_dominios", err6)

    # 7. portabilidad: ningun .md ni .json de la skill cita rutas absolutas de un equipo concreto
    err7 = []
    ruta_fija = re.compile(r'\b[A-Za-z]:[\\/]|/Users/|/home/')
    for pf in sorted(list(raiz.rglob("*.md")) + list(raiz.rglob("*.json"))):
        if ".git" in pf.parts:
            continue
        try:
            for num, line in enumerate(pf.read_text(encoding="utf-8").splitlines(), 1):
                if ruta_fija.search(line):
                    err7.append(f"{pf.relative_to(raiz)}:{num} cita una ruta absoluta")
        except Exception as e:
            err7.append(f"error al leer {pf.name}: {e}")
    reportar("rutas_portables", err7)

    # 8. cada skill nombrada en la tabla de enrutado de SKILL.md con el formato `skill:<nombre>`
    err8 = []
    if skill_md.is_file():
        try:
            content = skill_md.read_text(encoding="utf-8")
            skill_refs = re.findall(r'skill:([a-zA-Z0-9_\-:]+)', content)
            for sk in skill_refs:
                if ":" in sk:
                    continue
                sk_path = skills_dir / sk / "SKILL.md"
                if not sk_path.is_file():
                    err8.append(f"skill '{sk}' no instalada en {sk_path}")
        except Exception as e:
            err8.append(f"error al analizar skills en SKILL.md: {e}")
    avisar("skills_enrutado", err8)

    # 9. arranque S11: paso cero literal (interfaz con onboarding/) y los cuatro archivos de fase
    err9 = []
    if skill_md.is_file():
        content = skill_md.read_text(encoding="utf-8")
        requeridos = [
            "Primera vez: si no existe `~/.claude/upo/perfil.json`, seguir `onboarding/CUESTIONARIO.md` antes de cualquier fase.",
            "01_HANDSHAKE.md", "02_SCAVENGE.md", "03_MAPPING.md", "04_EJECUCION.md",
            "PLANTILLA_BRIEF.md", "PLANTILLA_BRIEF_OBRERO.md", "resultado_purgado.py",
        ]
        for r in requeridos:
            if r not in content:
                err9.append(f"SKILL.md no contiene '{r}'")
    for f in ["plantillas/PLANTILLA_BRIEF.md", "plantillas/PLANTILLA_BRIEF_OBRERO.md",
              "plantillas/PLANTILLA_ESTADO.md", "plantillas/PLANTILLA_RESULTADO.md",
              "scripts/resultado_purgado.py", "references/reglas-s.md"]:
        if not (raiz / f).is_file():
            err9.append(f"falta {f}")
    reportar("arranque_s11", err9)

    print(f"RESULTADO: {total_fallas} fallas")
    sys.exit(0 if total_fallas == 0 else 1)


if __name__ == "__main__":
    main()
