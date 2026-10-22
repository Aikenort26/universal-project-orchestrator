#!/usr/bin/env python
"""Servidor MCP y CLI de Ingenieria Civil e Hidroinformatica (Costo Cero).

Provee herramientas unificadas de validacion normativa RAS 0330 de 2017,
calculo de perdidas por friccion (Hazen-Williams), flujo en canales (Manning)
y consulta canonica de articulos normativos sin consumo innecesario de tokens.

Puede ejecutarse via CLI o como servidor MCP JSON-RPC sobre stdio.

Uso CLI:
    python mcp_civil_server.py --tool verificar_criterio_ras --args '{"diametro_mm": 200, "pendiente_m_m": 0.008, "caudal_l_s": 25.0}'
    python mcp_civil_server.py --tool calcular_perdidas_hw --args '{"caudal_l_s": 15.0, "longitud_m": 120.0, "diametro_mm": 110.0, "c_hw": 150}'
    python mcp_civil_server.py --tool consultar_norma --args '{"norma": "RAS_0330", "articulo": 134}'
"""
from __future__ import annotations

import argparse
import json
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Base canónica local de artículos normativos (0 tokens de red / cero alucinaciones)
NORMATIVA_CANONICA = {
    "RAS_0330": {
        "134": {
            "titulo": "Velocidad y fuerza tractiva mínimas en redes de alcantarillado",
            "resolucion": "Resolución 0330 de 2017 (Ministerio de Vivienda, Ciudad y Territorio)",
            "requisitos": {
                "velocidad_minima_sanitario_m_s": 0.75,
                "velocidad_minima_pluvial_m_s": 0.75,
                "fuerza_tractiva_minima_sanitario_pa": 1.0,
                "fuerza_tractiva_minima_pluvial_pa": 1.5
            },
            "texto": "La velocidad mínima real en colectores debe ser de 0,75 m/s para el caudal de diseño. De no alcanzarse dicha velocidad, debe garantizarse una tensión tractiva mínima de 1,0 Pa en alcantarillado sanitario y 1,5 Pa en alcantarillado pluvial."
        },
        "135": {
            "titulo": "Velocidad máxima en redes de alcantarillado",
            "resolucion": "Resolución 0330 de 2017",
            "requisitos": {
                "velocidad_maxima_concreto_m_s": 4.5,
                "velocidad_maxima_termoplasticos_m_s": 5.0
            },
            "texto": "La velocidad máxima real permitida no debe superar 5,0 m/s para tuberías termoplásticas (PVC, PEAD) ni 4,5 m/s para tuberías de concreto, con el fin de prevenir erosión y abrasión."
        },
        "137": {
            "titulo": "Profundidad hidráulica máxima en colectores",
            "resolucion": "Resolución 0330 de 2017",
            "requisitos": {
                "relacion_tirante_diametro_max_sanitario": 0.85,
                "relacion_tirante_diametro_max_pluvial": 0.93
            },
            "texto": "Los colectores deben diseñarse a flujo libre con lámina de agua no superior al 85 % del diámetro interno para alcantarillado sanitario (y/D <= 0,85) y al 93 % para alcantarillado pluvial (y/D <= 0,93)."
        }
    },
    "RES_0631": {
        "14": {
            "titulo": "Parámetros fisicoquímicos en vertimientos de aguas residuales domésticas (ARD)",
            "resolucion": "Resolución 0631 de 2015 (Ministerio de Ambiente y Desarrollo Sostenible)",
            "limites_maximos_permisibles": {
                "dbo5_mg_l": 90.0,
                "dqo_mg_l": 180.0,
                "sst_mg_l": 90.0,
                "grasas_y_aceites_mg_l": 20.0,
                "ph_rango": [6.0, 9.0]
            },
            "texto": "Los vertimientos puntuales de aguas residuales domésticas a cuerpos de agua superficiales deben cumplir con los valores límites máximos permisibles de DBO5 <= 90 mg/L, DQO <= 180 mg/L, SST <= 90 mg/L y pH entre 6,00 y 9,00."
        }
    }
}


def tool_verificar_criterio_ras(diametro_mm: float, pendiente_m_m: float, caudal_l_s: float, tipo_flujo: str = "sanitario") -> dict:
    """Verifica criterios hidráulicos y normativos de la Resolución 0330 de 2017."""
    d_m = diametro_mm / 1000.0
    q_m3_s = caudal_l_s / 1000.0
    area_llena = (math.pi * (d_m ** 2)) / 4.0
    v_llena = q_m3_s / area_llena if area_llena > 0 else 0.0

    # Estimacion de fuerza tractiva aproximada tau = gamma * R * S
    gamma = 9810.0  # N/m3
    r_lleno = d_m / 4.0
    tau_pa = gamma * r_lleno * pendiente_m_m

    art134 = NORMATIVA_CANONICA["RAS_0330"]["134"]["requisitos"]
    art135 = NORMATIVA_CANONICA["RAS_0330"]["135"]["requisitos"]

    v_min = art134["velocidad_minima_sanitario_m_s"] if tipo_flujo == "sanitario" else art134["velocidad_minima_pluvial_m_s"]
    tau_min = art134["fuerza_tractiva_minima_sanitario_pa"] if tipo_flujo == "sanitario" else art134["fuerza_tractiva_minima_pluvial_pa"]
    v_max = art135["velocidad_maxima_termoplasticos_m_s"]

    cumple_v_min = (v_llena >= v_min)
    cumple_tau = (tau_pa >= tau_min)
    cumple_autolimpieza = cumple_v_min or cumple_tau
    cumple_v_max = (v_llena <= v_max)

    return {
        "diametro_mm": diametro_mm,
        "pendiente_m_m": pendiente_m_m,
        "pendiente_porcentaje": round(pendiente_m_m * 100.0, 3),
        "caudal_l_s": caudal_l_s,
        "velocidad_m_s": round(v_llena, 3),
        "tension_tractiva_pa": round(tau_pa, 2),
        "verificaciones": {
            "velocidad_minima": {
                "valor_calculado": round(v_llena, 3),
                "limite_normativo": v_min,
                "cumple": cumple_v_min,
                "norma": "Res. 0330/2017 Art. 134"
            },
            "tension_tractiva": {
                "valor_calculado": round(tau_pa, 2),
                "limite_normativo": tau_min,
                "cumple": cumple_tau,
                "norma": "Res. 0330/2017 Art. 134"
            },
            "autolimpieza_global": {
                "cumple": cumple_autolimpieza,
                "criterio": "Cumple velocidad mínima (>= 0,75 m/s) o tensión tractiva (>= 1,0 Pa)"
            },
            "velocidad_maxima": {
                "valor_calculado": round(v_llena, 3),
                "limite_normativo": v_max,
                "cumple": cumple_v_max,
                "norma": "Res. 0330/2017 Art. 135"
            }
        },
        "estado_general": "CONFORME" if (cumple_autolimpieza and cumple_v_max) else "NO_CONFORME"
    }


def tool_calcular_perdidas_hw(caudal_l_s: float, longitud_m: float, diametro_mm: float, c_hw: float = 150.0) -> dict:
    """Calcula pérdidas de carga continuas por fricción mediante Hazen-Williams."""
    d_m = diametro_mm / 1000.0
    q_m3_s = caudal_l_s / 1000.0

    # Formula Hazen-Williams: hf = 10.674 * L * Q^1.852 / (C^1.852 * D^4.871)
    hf = 10.674 * longitud_m * (q_m3_s ** 1.852) / ((c_hw ** 1.852) * (d_m ** 4.871))
    gradiente_j = hf / longitud_m if longitud_m > 0 else 0.0

    area = (math.pi * (d_m ** 2)) / 4.0
    vel = q_m3_s / area if area > 0 else 0.0

    return {
        "caudal_l_s": caudal_l_s,
        "longitud_m": longitud_m,
        "diametro_mm": diametro_mm,
        "coeficiente_c": c_hw,
        "perdida_friccion_mca": round(hf, 3),
        "gradiente_hidraulico_m_m": round(gradiente_j, 5),
        "gradiente_por_mil_m_km": round(gradiente_j * 1000.0, 2),
        "velocidad_flujo_m_s": round(vel, 3)
    }


def tool_consultar_norma(norma: str, articulo: int | str) -> dict:
    """Devuelve el contenido técnico y límites reglamentarios exactos de una norma."""
    norma_key = norma.upper().replace("-", "_").replace(" ", "_")
    art_str = str(articulo)

    catalogo = NORMATIVA_CANONICA.get(norma_key)
    if not catalogo:
        return {"error": f"Norma '{norma}' no encontrada en el catalogo local. Normas disponibles: {list(NORMATIVA_CANONICA.keys())}"}

    contenido = catalogo.get(art_str)
    if not contenido:
        return {"error": f"Articulo '{art_str}' no registrado en la norma '{norma}'. Articulos disponibles: {list(catalogo.keys())}"}

    return {
        "norma": norma_key,
        "articulo": art_str,
        "datos": contenido
    }


def handle_rpc_line(line: str):
    """Manejador basico de peticiones JSON-RPC para MCP."""
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "verificar_criterio_ras",
                            "description": "Verifica criterios de velocidad y tension tractiva de la Resolucion 0330 de 2017 (RAS).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "diametro_mm": {"type": "number"},
                                    "pendiente_m_m": {"type": "number"},
                                    "caudal_l_s": {"type": "number"},
                                    "tipo_flujo": {"type": "string", "enum": ["sanitario", "pluvial"]}
                                },
                                "required": ["diametro_mm", "pendiente_m_m", "caudal_l_s"]
                            }
                        },
                        {
                            "name": "calcular_perdidas_hw",
                            "description": "Calcula perdidas por friccion en tuberias a presion usando Hazen-Williams.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "caudal_l_s": {"type": "number"},
                                    "longitud_m": {"type": "number"},
                                    "diametro_mm": {"type": "number"},
                                    "c_hw": {"type": "number", "default": 150}
                                },
                                "required": ["caudal_l_s", "longitud_m", "diametro_mm"]
                            }
                        },
                        {
                            "name": "consultar_norma",
                            "description": "Consulta articulos y parametros oficiales de la Resolucion 0330 de 2017 y Resolucion 0631 de 2015.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "norma": {"type": "string"},
                                    "articulo": {"type": "string"}
                                },
                                "required": ["norma", "articulo"]
                            }
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "verificar_criterio_ras":
                res = tool_verificar_criterio_ras(**args)
            elif name == "calcular_perdidas_hw":
                res = tool_calcular_perdidas_hw(**args)
            elif name == "consultar_norma":
                res = tool_consultar_norma(**args)
            else:
                res = {"error": f"Herramienta desconocida: {name}"}

            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2, ensure_ascii=False)}]
                }
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

    except Exception as e:
        sys.stderr.write(f"Error procesando RPC: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Servidor de calculo normativo e hidraulico")
    parser.add_argument("--tool", help="Nombre de la herramienta a invocar directamente")
    parser.add_argument("--args", default="{}", help="Argumentos en formato JSON")
    parser.add_argument("--server", action="store_true", help="Iniciar en modo servidor stdio JSON-RPC")

    args = parser.parse_args()

    if args.server:
        for line in sys.stdin:
            handle_rpc_line(line.strip())
        return

    if args.tool:
        raw = args.args.strip()
        try:
            params = json.loads(raw)
        except Exception:
            try:
                params = json.loads(raw.replace("'", "\""))
            except Exception as e:
                print(f"[ERROR] JSON de argumentos inválido: {e}")
                sys.exit(1)

        if args.tool == "verificar_criterio_ras":
            res = tool_verificar_criterio_ras(**params)
        elif args.tool == "calcular_perdidas_hw":
            res = tool_calcular_perdidas_hw(**params)
        elif args.tool == "consultar_norma":
            res = tool_consultar_norma(**params)
        else:
            print(f"[ERROR] Herramienta desconocida: {args.tool}")
            sys.exit(1)

        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
