---
name: universal-project-orchestrator
description: >
  Meta-skill universal de orquestacion, calidad y gestion de ciclo de vida para
  cualquier proyecto (ingenieria, investigacion cientifica, desarrollo de software,
  consultoria empresarial o gestion contractual). Integra el ecosistema completo:
  protocolo de exclusion mutua (cerrojos mutex), delegacion agéntica paralela
  (patron Superpowers), conectores MCP (civil, matlab, qgis), plugins/mods (ponytail,
  watermarks-remover, token-meter), recuperacion quirurgica de contexto (3 capas
  anti-context-rot), desacoplamiento de modelos de dominio y control de calidad
  Zero-AI con el estandar de estilo AHOH.
---

# Universal Project Orchestrator (UPO): Sistema Operativo de Proyectos y Calidad

> **Marco Metodológico Universal:** Esta meta-skill establece el estándar operativo para la ejecución rigurosa, eficiente y auditable de cualquier proyecto o tarea técnica en el ecosistema de Aiken Ortega-Heredia. Desacopla la lógica metodológica respecto a disciplinas específicas, permitiendo orquestar proyectos de ingeniería física, desarrollo informático, producción científica o gestión contractual bajo una misma disciplina de calidad y economía de tokens.

---

## 1. Mapa de Integración Ecosistémica

La meta-skill actúa como el director de orquesta que conecta y articula los cuatro pilares del entorno:

| Pilar | Componentes Integrados | Función Operativa en la Tarea |
| :--- | :--- | :--- |
| **Gobernanza Canónica** | `REGLAS_GOBERNANZA_MI_UNIDAD.xml`, `afiliaciones_canonicas_autores.xml`, `ESTANDAR_ESTILO_REDACCION_AHOH.xml`, `ESTANDAR_GESTION_CONTEXTO_TOKENS.xml`, `AGENTS.md` | Invariantes duras, políticas de no-alucinación, reglas léxicas y restricciones éticas/institucionales. |
| **Conectividad MCP** | `civil` (`mcp_civil_server.py`), `matlab` (MATLAB R2026a), `qgis` (QGIS MCP) | Ejecución determinista de cálculos analíticos, modelaciones numéricas y geoprocesamiento desatendido sin depender de razonamiento aproximado del LLM. |
| **Plugins y Mods** | `watermarks-remover` (Turnitout), `ponytail` (Lazy dev mode), `token-meter`, `commit`, `image-preview` (HUD flotante) | Sanitización de marcas de IA, simplicidad técnica sin sobreingeniería, control presupuestario y visualización gráfica inmediata. |
| **Biblioteca de Habilidades** | 86 skills curadas en `BRAIN/skills/` (`writing-plans`, `executing-plans`, `dispatching-parallel-agents`, `systematic-debugging`, `docx`, `xlsx`, `latex-equation-hud`) | Libros de jugadas especializados cargados bajo demanda sin sobrecargar el contexto inicial. |

---

## 2. El Ciclo de Vida Operativo en 5 Fases

Toda tarea o proyecto orquestado mediante esta meta-skill debe transitar obligatoriamente por cinco fases estructuradas:

```
[Fase 1: Pre-vuelo y Bloqueo]
       │
       ▼
[Fase 2: Recuperación Quirúrgica de Contexto]
       │
       ▼
[Fase 3: Despacho y Delegación Agéntica]
       │
       ▼
[Fase 4: Ejecución Desacoplada de Dominio]
       │
       ▼
[Fase 5: Auditoría de Calidad, Sanitización y Cierre]
```

---

### Fase 1: Pre-Vuelo y Exclusión Mutua (Prevención de Colisiones)

Antes de modificar cualquier archivo de trabajo o entregable en Google Drive:

1. **Auditoría de sincronización:**
   Verificar que no existan conflictos o archivos duplicados generados por sincronización de red:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "G:\Mi unidad\00-scripts_admin\test-sync-health.ps1"
   ```
2. **Adquisición de cerrojo exclusivo:**
   Adquirir el cerrojo del proyecto mediante [`agent_mutex.py`](file:///G:/Mi%20unidad/BRAIN/.brain/tools/agent_mutex.py):
   ```bash
   python "G:\Mi unidad\BRAIN\.brain\tools\agent_mutex.py" acquire "<nombre_proyecto>" --agent "<ID_Agente>" --reason "<descripcion_tarea>" --ttl 15
   ```
   * **Regla de bloqueo:** Si el comando devuelve código de salida `1` (`[BLOQUEADO]`), el agente DEBE detenerse de inmediato y notificar al usuario el nombre del agente titular y el tiempo restante de retención. Queda terminantemente prohibido sobreescribir archivos bloqueados.

---

### Fase 2: Recuperación Quirúrgica de Contexto (Anti-Context Rot)

Para evitar la degradación de la atención del LLM y mantener el consumo por debajo de 150 000 tokens:

1. **Pirámide de 3 Capas de Recuperación:**
   * **Capa 1 (0 tokens LLM):** Búsqueda de alta velocidad en SQLite FTS5 local:
     ```bash
     python "G:\Mi unidad\BRAIN\.brain\search\cli.py" search "<termino_clave>" -n 5
     ```
   * **Capa 2 (~1 500 tokens):** Consulta relacional acotada en el grafo de conocimiento:
     ```bash
     graphify query "<pregunta>" --budget 1500
     ```
   * **Capa 3 (Lectura quirúrgica con rangos):** Prohibido volcar archivos completos de más de 100 líneas. Emplear siempre `StartLine` y `EndLine` para leer únicamente la sección requerida.

---

### Fase 3: Despacho y Delegación Agéntica (Patrón Superpowers)

Cuando una tarea requiera múltiples operaciones complejas o independientes:

1. **Criterio de bifurcación:**
   * Si las subtareas son **independientes** (no comparten estado ni orden estricto, como auditar 3 memorias de cálculo diferentes o generar 4 figuras vectoriales en paralelo), se delegan a **subagentes paralelos** mediante `dispatching-parallel-agents`.
   * Si las subtareas son **secuenciales** (el paso B depende estrictamente de la salida del paso A), se ejecutan paso a paso validando cada entregable antes de continuar.

2. **Protocolo de despacho de subagentes:**
   Cada subagente debe inicializarse con un contexto aislado y estrictamente delimitado:
   * **Objetivo atómico:** Expresado en una sola frase concisa.
   * **Insumos necesarios:** Rutas absolutas a los archivos específicos de entrada.
   * **Condición de parada clara:** Definición verificable de éxito (ej. "el archivo X existe y pasa la auditoría Y").
   * **Prohibición de contexto residual:** No inyectar historiales de conversación pasados innecesarios.

---

### Fase 4: Ejecución Desacoplada y Adaptadores de Dominio

La lógica de datos se desacopla completamente de la presentación del documento final mediante **Adaptadores de Dominio**:

```
[DATOS_CANONICOS (JSON / XML)] ──> [MOTOR DE CÁLCULO / MCP] ──> [GENERADOR DE VISTA (LaTeX/MD/DOCX)]
```

#### Adaptadores Estándar Disponibles:
1. **Dominio de Ingeniería Civil e Hidráulica:**
   * Fuente canónica: `DATOS_TECNICOS.json`.
   * Motores de cálculo: `mcp_civil_server.py` (RAS 0330, Hazen-Williams, Manning) o librerías `WNTR` / `pyswmm`.
   * Renderizado: `generar_memoria_tecnica.py` generando memorias en Markdown o LaTeX.
2. **Dominio Científico y Tesis Doctoral:**
   * Fuente canónica: `afiliaciones_canonicas_autores.xml` y datos de modelación numérica.
   * Motores de cálculo: MATLAB R2026a (`run_matlab_file`), Simulink Quasi-2D y OpenFOAM.
   * Renderizado: Plantillas LaTeX con estándar de compilación y verificación de figuras en HUD.
3. **Dominio de Desarrollo de Software:**
   * Fuente canónica: Archivos de configuración de arquitectura (`package.json`, `pyproject.toml`).
   * Motores de cálculo: Pruebas unitarias TDD (PyTest, Jest) y reglas de `ponytail` (soluciones mínimas sin sobreingeniería).
   * Renderizado: Código modular y confirmaciones semánticas (`commit`).
4. **Dominio Contractual y de Consultoría:**
   * Fuente canónica: Fichas de proyecto en `wiki/projects/` y expedientes PR-EX-003.
   * Motores de cálculo: Verificación de cronogramas y cuadro de actividades mensuales.
   * Renderizado: Informes de supervisión contractual en formato institucional.

---

### Fase 5: Auditoría de Calidad, Sanitización Zero-AI y Cierre Atómico

Ninguna tarea se da por concluida sin superar los puntos de control de calidad:

1. **Auditoría de estilo y léxico AHOH:**
   * Voz impersonal con "se".
   * Cero símbolos de sección (escribir siempre "Sección" o "Apartado").
   * Cero rayas largas (usar comas, paréntesis o dos puntos).
   * Cero clichés de IA vetados ("robusto", "holístico", "sinergia", "paradigma", "potenciar", "crucial", "asimismo").
2. **Sanitización programática Zero-AI:**
   Ejecutar [`turnitout_humanizer.py`](file:///G:/Mi%20unidad/00-scripts_admin/turnitout_humanizer.py) sobre el archivo generado para purgar caracteres invisibles Unicode (zero-width) y sanitizar comentarios:
   ```bash
   python "G:\Mi unidad\00-scripts_admin\turnitout_humanizer.py" --file "<ruta_archivo>" --check
   ```
3. **Registro en el bus continuo y liberación atómica:**
   * Registrar el evento en el bus continuo:
     ```bash
     python "G:\Mi unidad\BRAIN\.brain\tools\agent_mutex.py" log --agent "<ID_Agente>" --action "tarea_completada" --target "<proyecto>"
     ```
   * Liberar el cerrojo del recurso:
     ```bash
     python "G:\Mi unidad\BRAIN\.brain\tools\agent_mutex.py" release "<nombre_proyecto>" --agent "<ID_Agente>"
     ```
   * Actualizar la bitácora diaria (`wiki/daily/AAAA-MM-DD.md`) y el catálogo maestro (`index.md`) si se crearon notas permanentes.

---

## 3. Ejemplo Rápido de Invocación Multidisciplinar

### Caso A: Estudio de Ingeniería Civil (Vertimiento)
```bash
# 1. Bloqueo
python .brain/tools/agent_mutex.py acquire "PTO_BUENAVISTA" --agent "Antigravity" --reason "Memoria hidraulica"
# 2. Calculo y generacion
python 00-scripts_admin/generar_memoria_tecnica.py --project "02-empresas/ingenova/PROYECTOS/PTO_BUENAVISTA/02_ESTUDIOS_TECNICOS/04_VERTIMIENTO"
# 3. Control de calidad
python 00-scripts_admin/turnitout_humanizer.py --file "02-empresas/.../MEMORIA_CALCULO_HIDRAULICO_VERTIMIENTO.md" --check
# 4. Liberacion
python .brain/tools/agent_mutex.py release "PTO_BUENAVISTA" --agent "Antigravity"
```

### Caso B: Manuscrito Científico Doctoral
```bash
# 1. Bloqueo
python .brain/tools/agent_mutex.py acquire "TESIS_QUASI2D" --agent "ClaudeCode" --reason "Seccion metodologia"
# 2. Verificacion de autores y calculos
python 00-scripts_admin/mcp_civil_server.py --tool consultar_norma --args "{'norma': 'RAS_0330', 'articulo': 134}"
# 3. Sanitizacion Zero-AI
python 00-scripts_admin/turnitout_humanizer.py --file "manuscrito.tex" --inplace
# 4. Liberacion
python .brain/tools/agent_mutex.py release "TESIS_QUASI2D" --agent "ClaudeCode"
```
