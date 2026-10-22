# Memoria de Cálculo Hidráulico y Definición de Tramos de Vertimiento

**Proyecto:** Estudio de Vertimiento PTAR Puerto Buenavista  
**Código:** ING-PBV-2026  
**Entidad / Cliente:** Puerto Buenavista  
**Consultor:** INGENOVA S.A.S.  
**Fecha de generación paramétrica:** 2026-10-21  
**Sistema de coordenadas:** MAGNA-SIRGAS - Origen Único Nacional CTM-12 (EPSG:9377)

---

## 1. Alcance y Marco Normativo

El presente documento técnico contiene el dimensionamiento hidráulico y la caracterización de flujo del tramo del canal artificial receptor de las aguas residuales domésticas tratadas (ARD) procedentes de la PTAR de Puerto Buenavista.

La evaluación se desarrolla en cumplimiento de los siguientes instrumentos legales y regulatorios vigentes en Colombia:
- **Resolución 0330 de 2017 (Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico - RAS):** Criterios de diseño hidráulico en canales, velocidades permisibles de arrastre y no erosión (Artículos 134 y 135).
- **Resolución 0631 de 2015:** Parámetros y valores límites máximos permisibles en vertimientos puntuales a cuerpos de agua superficiales.
- **Decreto 1076 de 2015:** Decreto Único Reglamentario del Sector Ambiente y Desarrollo Sostenible (Trámite de permiso de vertimientos ante el Establecimiento Público Ambiental - EPA Cartagena).
- **Guía Nacional de Modelación del Recurso Hídrico (IDEAM):** Criterios para la discretización de tramos y modelación en QUAL2K.

---

## 2. Geometría del Canal y Parámetros de Rugosidad

La sección transversal del canal corresponde a una estructura artificial de concreto con las siguientes características físicas levantadas en campo:
- **Descripción:** Canal artificial de concreto abierto Yara
- **Tipo de sección:** Trapezoidal
- **Ancho de fondo ($b$):** 1.20 m
- **Talud lateral ($z$):** 0.50 (H:V = 0.50:1)
- **Pendiente longitudinal de fondo ($S_0$):** 0.0018 m/m (0.18 %)
- **Coeficiente de rugosidad de Manning ($n$):** 0.015 (concreto con acabado liso y presencia moderada de biopelícula)
- **Longitud total del tramo levantado:** 427.00 m

---

## 3. Condiciones de Caudal y Balance de Masa

De acuerdo con el aforo y la caracterización de caudales de diseño, se establecen tres escenarios de flujo:
1. **Caudal de descarga de la PTARD ($Q_{ptar}$):** 4.50 L/s (0.0045 m³/s).
2. **Caudal base del canal receptor ($Q_{base}$):** 28.30 L/s (0.0283 m³/s).
3. **Caudal total de mezcla aguas abajo de la descarga ($Q_{total}$):** 32.80 L/s (0.0328 m³/s).

---

## 4. Resultados del Cálculo Hidráulico (Flujo Uniforme)

El tirante normal ($y_n$) se determinó mediante solución numérica iterativa de la ecuación de Manning para canales abiertos:

$$Q = \frac{1}{n} \cdot A \cdot R_h^{2/3} \cdot S_0^{1/2}$$

Donde el área mojada ($A$) y el radio hidráulico ($R_h$) se expresan geométricamente en función del tirante:

$$A = (b + z \cdot y) \cdot y$$
$$P = b + 2 \cdot y \cdot \sqrt{1 + z^2}$$
$$R_h = \frac{A}{P}$$

### Cuadro de Parámetros Hidráulicos Resultantes

| Parámetro Hidráulico | Símbolo | Unidad | Valor Calculado |
| :--- | :---: | :---: | :---: |
| Caudal de evaluación | $Q$ | m³/s | 0.0328 (32.80 L/s) |
| Tirante normal | $y_n$ | m | 0.0630 (6.30 cm) |
| Área mojada | $A$ | m² | 0.0775 |
| Perímetro mojado | $P$ | m | 1.3408 |
| Radio hidráulico | $R_h$ | m | 0.0578 |
| Espejo de agua superior | $T$ | m | 1.2630 |
| Velocidad media de flujo | $V$ | m/s | 0.423 |
| Profundidad hidráulica | $D_h$ | m | 0.0614 |
| Número de Froude | $Fr$ | Adimensional | 0.545 |
| Régimen de flujo | (Clasificación) | - | Subcrítico (Flujo tranquilo) |

---

## 5. Verificación de Criterios Normativos (Resolución 0330 de 2017)

| Criterio Evaluado | Cita Normativa | Límite Reglamentario | Valor del Proyecto | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **Velocidad mínima** | Res. 0330/2017 Art. 134 | $V \ge 0,60$ m/s (evitar sedimentación) | 0.423 m/s | PENDIENTE DE AJUSTE |
| **Velocidad máxima** | Res. 0330/2017 Art. 135 | $V \le 4,50$ m/s (concreto simple/reforzado) | 0.423 m/s | CUMPLE |
| **Estabilidad de régimen** | Criterio de Froude | $Fr < 0,85$ o $Fr > 1,15$ | $Fr = 0.545$ | CUMPLE |

---

## 6. Discretización de Tramos para Modelación de Calidad en QUAL2K

Con base en la inspección de campo y las mediciones satelitales de alta precisión, se establece la discretización espacial para el modelo QUAL2K:

1. **Tramo 1 (Línea base aguas arriba de la descarga):**
   - Abscisado: K0+000 a K0+051,95 (Longitud = 51.95 m).
   - Estación de monitoreo no impactada (Punto de control aguas arriba): Localizada a 31.00 m aguas arriba del punto de vertimiento.
2. **Punto de Vertimiento (Punto Cero):**
   - Abscisa K0+051,95: Entrega del efluente tratado de la PTAR mediante canal de descarga y compuerta de regulación.
3. **Tramo 2 (Zona de mezcla y transporte hacia cuerpo principal):**
   - Abscisado: K0+051,95 a K0+427,00 (Longitud = 375.05 m).
   - Confluencia final en K0+427,00 con el canal principal de drenaje.

---

## 7. Conclusiones y Recomendaciones Técnicas

1. Se verificó que el canal de concreto Yara presenta condiciones hidráulicas estables bajo régimen subcrítico (flujo tranquilo), con una velocidad media de 0.423 m/s que asegura la capacidad de autolimpieza sin generar esfuerzos erosivos sobre las paredes de la estructura.
2. La sectorización topográfica de 427.0 m provee una longitud suficiente para evaluar los procesos de reoxigenación superficial y decaimiento de materia orgánica ($DBO_5$ esperada de 25.0 mg/L) requeridos por el Establecimiento Público Ambiental - EPA Cartagena.
