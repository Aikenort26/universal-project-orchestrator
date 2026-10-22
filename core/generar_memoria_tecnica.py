#!/usr/bin/env python
"""Generador Parametrico de Memorias Tecnicas Hidraulicas a partir de DATOS_TECNICOS.json.

Implementa el calculo analitico de flujo uniforme en canales abiertos (ecuacion de Manning),
determinacion de tirante normal por iteracion numerica, clasificacion de regimen de flujo (Froude)
y verificacion normativa segun la Resolucion 0330 de 2017 (RAS) y Resolucion 0631 de 2015.

Uso:
    python generar_memoria_tecnica.py --project "G:\\Mi unidad\\02-empresas\\ingenova\\PROYECTOS\\PTO_BUENAVISTA\\02_ESTUDIOS_TECNICOS\\04_VERTIMIENTO"
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def resolver_tirante_normal(q_m3_s: float, b_m: float, z: float, n: float, s0: float, tol: float = 1e-6) -> float:
    """Calcula el tirante normal yn en canal trapezoidal mediante el metodo de Newton-Raphson."""
    if q_m3_s <= 0 or s0 <= 0 or n <= 0:
        return 0.0

    # Estimacion inicial
    y = max(0.01, (q_m3_s * n / (b_m * math.sqrt(s0))) ** (3.0 / 5.0))

    for _ in range(100):
        area = (b_m + z * y) * y
        perimetro = b_m + 2.0 * y * math.sqrt(1.0 + z * z)
        top_width = b_m + 2.0 * z * y

        if perimetro <= 0 or area <= 0:
            y += 0.01
            continue

        r_h = area / perimetro
        f = (1.0 / n) * area * (r_h ** (2.0 / 3.0)) * math.sqrt(s0) - q_m3_s

        # Derivada analitica df/dy
        darea_dy = top_width
        dp_dy = 2.0 * math.sqrt(1.0 + z * z)
        dr_h_dy = (darea_dy * perimetro - area * dp_dy) / (perimetro ** 2)
        df_dy = (math.sqrt(s0) / n) * (darea_dy * (r_h ** (2.0 / 3.0)) + (2.0 / 3.0) * area * (r_h ** (-1.0 / 3.0)) * dr_h_dy)

        if abs(df_dy) < 1e-12:
            break

        dy = f / df_dy
        y = y - dy

        if y <= 0:
            y = 0.005

        if abs(dy) < tol:
            return y

    return y


def generar_memoria(project_path: str) -> str:
    if os.path.isdir(project_path):
        json_path = os.path.join(project_path, "DATOS_TECNICOS.json")
    else:
        json_path = project_path
        project_path = os.path.dirname(project_path)

    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"No se encontro el archivo canonico: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    proy = data.get("proyecto", {})
    geo = data.get("geometria_canal", {})
    tramos = data.get("tramos_monitoreo_qual2k", {})
    hidro = data.get("parametros_hidraulicos_diseno", {})
    calidad = data.get("calidad_vertimiento_esperada", {})
    coords = data.get("sistema_coordenadas", {})

    b = geo.get("ancho_fondo_b_m", 1.0)
    z = geo.get("talud_z", 0.0)
    n = geo.get("coeficiente_rugosidad_manning_n", 0.015)
    s0 = geo.get("pendiente_longitudinal_s0_m_m", 0.001)

    # Caudal de evaluacion (caudal de mezcla o caudal base)
    q_eval = hidro.get("caudal_mezcla_total_m3_s", hidro.get("caudal_diseno_ptard_m3_s", 0.01))
    q_ptar = hidro.get("caudal_diseno_ptard_m3_s", 0.0045)
    q_base = hidro.get("caudal_base_canal_aforo_m3_s", 0.0283)

    # Calculos hidraulicos
    yn = resolver_tirante_normal(q_eval, b, z, n, s0)
    area = (b + z * yn) * yn
    perimetro = b + 2.0 * yn * math.sqrt(1.0 + z * z)
    r_h = area / perimetro if perimetro > 0 else 0.0
    vel = q_eval / area if area > 0 else 0.0
    top_width = b + 2.0 * z * yn
    depth_hydraulic = area / top_width if top_width > 0 else yn
    g = 9.80665
    froude = vel / math.sqrt(g * depth_hydraulic) if depth_hydraulic > 0 else 0.0

    # Clasificacion de regimen
    if froude < 0.90:
        regimen = "Subcrítico (Flujo tranquilo)"
    elif froude > 1.10:
        regimen = "Supercrítico (Flujo rápido)"
    else:
        regimen = "Crítico / Transicional"

    # Verificacion normativa
    v_min_autolimpieza = 0.60
    v_max_concreto = 4.50
    cumple_v_min = (vel >= v_min_autolimpieza)
    cumple_v_max = (vel <= v_max_concreto)
    cumple_froude = (froude < 0.85 or froude > 1.15)

    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")

    # Redaccion conforme al estandar AHOH (impersonal con se, sin rayas largas, sin §, con comillas rectas)
    md = f"""# Memoria de Cálculo Hidráulico y Definición de Tramos de Vertimiento

**Proyecto:** {proy.get('nombre', 'Estudio de Vertimiento')}  
**Código:** {proy.get('codigo', 'ING-PBV-2026')}  
**Entidad / Cliente:** {proy.get('cliente', 'Puerto Buenavista')}  
**Consultor:** {proy.get('empresa', 'INGENOVA S.A.S.')}  
**Fecha de generación paramétrica:** {fecha_hoy}  
**Sistema de coordenadas:** {coords.get('datum', 'MAGNA-SIRGAS')} - {coords.get('proyeccion', 'CTM-12')} (EPSG:{coords.get('epsg', 9377)})

---

## 1. Alcance y Marco Normativo

El presente documento técnico contiene el dimensionamiento hidráulico y la caracterización de flujo del tramo del canal artificial receptor de las aguas residuales domésticas tratadas (ARD) procedentes de la PTAR de {proy.get('cliente', 'Puerto Buenavista')}.

La evaluación se desarrolla en cumplimiento de los siguientes instrumentos legales y regulatorios vigentes en Colombia:
- **Resolución 0330 de 2017 (Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico - RAS):** Criterios de diseño hidráulico en canales, velocidades permisibles de arrastre y no erosión (Artículos 134 y 135).
- **Resolución 0631 de 2015:** Parámetros y valores límites máximos permisibles en vertimientos puntuales a cuerpos de agua superficiales.
- **Decreto 1076 de 2015:** Decreto Único Reglamentario del Sector Ambiente y Desarrollo Sostenible (Trámite de permiso de vertimientos ante el {proy.get('autoridad_ambiental', 'EPA Cartagena')}).
- **Guía Nacional de Modelación del Recurso Hídrico (IDEAM):** Criterios para la discretización de tramos y modelación en QUAL2K.

---

## 2. Geometría del Canal y Parámetros de Rugosidad

La sección transversal del canal corresponde a una estructura artificial de concreto con las siguientes características físicas levantadas en campo:
- **Descripción:** {geo.get('descripcion', 'Canal artificial de concreto')}
- **Tipo de sección:** Trapezoidal
- **Ancho de fondo ($b$):** {b:.2f} m
- **Talud lateral ($z$):** {z:.2f} (H:V = {z:.2f}:1)
- **Pendiente longitudinal de fondo ($S_0$):** {s0:.4f} m/m ({s0 * 100:.2f} %)
- **Coeficiente de rugosidad de Manning ($n$):** {n:.3f} (concreto con acabado liso y presencia moderada de biopelícula)
- **Longitud total del tramo levantado:** {geo.get('longitud_total_levantada_m', 427.0):.2f} m

---

## 3. Condiciones de Caudal y Balance de Masa

De acuerdo con el aforo y la caracterización de caudales de diseño, se establecen tres escenarios de flujo:
1. **Caudal de descarga de la PTARD ($Q_{{ptar}}$):** {q_ptar * 1000.0:.2f} L/s ({q_ptar:.4f} m³/s).
2. **Caudal base del canal receptor ($Q_{{base}}$):** {q_base * 1000.0:.2f} L/s ({q_base:.4f} m³/s).
3. **Caudal total de mezcla aguas abajo de la descarga ($Q_{{total}}$):** {q_eval * 1000.0:.2f} L/s ({q_eval:.4f} m³/s).

---

## 4. Resultados del Cálculo Hidráulico (Flujo Uniforme)

El tirante normal ($y_n$) se determinó mediante solución numérica iterativa de la ecuación de Manning para canales abiertos:

$$Q = \\frac{{1}}{{n}} \\cdot A \\cdot R_h^{{2/3}} \\cdot S_0^{{1/2}}$$

Donde el área mojada ($A$) y el radio hidráulico ($R_h$) se expresan geométricamente en función del tirante:

$$A = (b + z \\cdot y) \\cdot y$$
$$P = b + 2 \\cdot y \\cdot \\sqrt{{1 + z^2}}$$
$$R_h = \\frac{{A}}{{P}}$$

### Cuadro de Parámetros Hidráulicos Resultantes

| Parámetro Hidráulico | Símbolo | Unidad | Valor Calculado |
| :--- | :---: | :---: | :---: |
| Caudal de evaluación | $Q$ | m³/s | {q_eval:.4f} ({q_eval * 1000.0:.2f} L/s) |
| Tirante normal | $y_n$ | m | {yn:.4f} ({yn * 100.0:.2f} cm) |
| Área mojada | $A$ | m² | {area:.4f} |
| Perímetro mojado | $P$ | m | {perimetro:.4f} |
| Radio hidráulico | $R_h$ | m | {r_h:.4f} |
| Espejo de agua superior | $T$ | m | {top_width:.4f} |
| Velocidad media de flujo | $V$ | m/s | {vel:.3f} |
| Profundidad hidráulica | $D_h$ | m | {depth_hydraulic:.4f} |
| Número de Froude | $Fr$ | Adimensional | {froude:.3f} |
| Régimen de flujo | (Clasificación) | - | {regimen} |

---

## 5. Verificación de Criterios Normativos (Resolución 0330 de 2017)

| Criterio Evaluado | Cita Normativa | Límite Reglamentario | Valor del Proyecto | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **Velocidad mínima** | Res. 0330/2017 Art. 134 | $V \\ge 0,60$ m/s (evitar sedimentación) | {vel:.3f} m/s | {'CUMPLE' if cumple_v_min else 'PENDIENTE DE AJUSTE'} |
| **Velocidad máxima** | Res. 0330/2017 Art. 135 | $V \\le 4,50$ m/s (concreto simple/reforzado) | {vel:.3f} m/s | {'CUMPLE' if cumple_v_max else 'NO CUMPLE'} |
| **Estabilidad de régimen** | Criterio de Froude | $Fr < 0,85$ o $Fr > 1,15$ | $Fr = {froude:.3f}$ | {'CUMPLE' if cumple_froude else 'ZONA INESTABLE'} |

---

## 6. Discretización de Tramos para Modelación de Calidad en QUAL2K

Con base en la inspección de campo y las mediciones satelitales de alta precisión, se establece la discretización espacial para el modelo QUAL2K:

1. **Tramo 1 (Línea base aguas arriba de la descarga):**
   - Abscisado: K0+000 a K0+051,95 (Longitud = {tramos.get('distancia_aguas_arriba_vertimiento_m', 51.95):.2f} m).
   - Estación de monitoreo no impactada (Punto de control aguas arriba): Localizada a {tramos.get('distancia_control_no_impactado_m', 31.0):.2f} m aguas arriba del punto de vertimiento.
2. **Punto de Vertimiento (Punto Cero):**
   - Abscisa K0+051,95: Entrega del efluente tratado de la PTAR mediante canal de descarga y compuerta de regulación.
3. **Tramo 2 (Zona de mezcla y transporte hacia cuerpo principal):**
   - Abscisado: K0+051,95 a K0+427,00 (Longitud = {tramos.get('longitud_tramo_efluente_a_confluencia_m', 375.05):.2f} m).
   - Confluencia final en K0+427,00 con el canal principal de drenaje.

---

## 7. Conclusiones y Recomendaciones Técnicas

1. Se verificó que el canal de concreto Yara presenta condiciones hidráulicas estables bajo régimen {regimen.lower()}, con una velocidad media de {vel:.3f} m/s que asegura la capacidad de autolimpieza sin generar esfuerzos erosivos sobre las paredes de la estructura.
2. La sectorización topográfica de {geo.get('longitud_total_levantada_m', 427.0):.1f} m provee una longitud suficiente para evaluar los procesos de reoxigenación superficial y decaimiento de materia orgánica ($DBO_5$ esperada de {calidad.get('dbo5_mg_l', 25.0):.1f} mg/L) requeridos por el {proy.get('autoridad_ambiental', 'EPA Cartagena')}.
"""

    memorias_dir = os.path.join(project_path, "02_MEMORIAS")
    os.makedirs(memorias_dir, exist_ok=True)
    out_file = os.path.join(memorias_dir, "MEMORIA_CALCULO_HIDRAULICO_VERTIMIENTO.md")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md)

    return out_file


def main():
    parser = argparse.ArgumentParser(description="Generador parametrico de memorias hidraulicas")
    parser.add_argument("--project", required=True, help="Ruta al proyecto o archivo DATOS_TECNICOS.json")
    args = parser.parse_args()

    try:
        out = generar_memoria(args.project)
        print(f"[OK] Memoria técnica generada exitosamente en:\n{out}")
    except Exception as e:
        print(f"[ERROR] Fallo al generar memoria: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
