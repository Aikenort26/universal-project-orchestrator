# Universal Project Orchestrator (UPO) v2

Skill de Claude Code con un método de trabajo multiagente para proyectos de varias fases (estudios, diseños, informes, artículos):

- **Ciclo con puertas (S10):** Arranque, Planificar, Ejecutar, Auditar y Cerrar; ninguna fase avanza sin una verificación por comando.
- **Cadena de tres niveles (S11):** la sesión principal planifica y audita; reparte el trabajo en sesiones hijas, una por especialidad; cada hija recorre handshake, scavenge, mapping y ejecución con sus propios obreros y cierra con un bloque `## Resultado` validado.
- **Perfil personal:** la primera vez, un cuestionario corto genera tus reglas (idioma, redacción, carpetas, modelos, techos de contexto, delegación y autonomía).

La versión 1 queda en la etiqueta `v1`.

## Instalación

Requisitos: Claude Code y Python 3.9 o superior (solo biblioteca estándar; pytest para las pruebas).

```bash
git clone https://github.com/Aikenort26/universal-project-orchestrator.git ~/.claude/skills/universal-project-orchestrator
```

Para un solo proyecto, clona en `<proyecto>/.claude/skills/universal-project-orchestrator`. Para actualizar: `git pull` dentro de esa carpeta.

Comprobar la instalación:

```bash
cd ~/.claude/skills/universal-project-orchestrator
python scripts/validar_upo.py
python -m pytest onboarding/test_generar_perfil.py -q -p no:cacheprovider
```

Los avisos del validador sobre skills o agentes no instalados son informativos: esas piezas son opcionales.

## Primer uso

1. Abre Claude Code y pide, por ejemplo, "orquesta este proyecto" o "usa UPO".
2. Si no existe `~/.claude/upo/perfil.json`, el agente sigue `onboarding/CUESTIONARIO.md`: cuatro rondas de preguntas.
3. Quedan `~/.claude/upo/perfil.json` (respuestas) y `~/.claude/upo/REGLAS_PERSONALES.md` (reglas que el agente carga desde entonces). Nada sale de tu equipo.
4. Para rehacerlo: "rehaz mi perfil de UPO" o `python onboarding/generar_perfil.py --respuestas mis_respuestas.json --forzar`.

El estado de las sesiones (tablero, estado de cada hija, carpetas de trabajo) se guarda en `~/.claude/upo/sesiones/`.

## Estructura

| Ruta | Contenido |
|---|---|
| `SKILL.md` | El método: arranque de principal e hija, ciclo, dominios, delegación |
| `references/` | Reglas S0 a S11, criterio de cada puerta, roles de agentes, contrato de delegación y economía de tokens |
| `plantillas/` | Brief de hija, brief de obrero, estado y bloque Resultado |
| `dominios/` | Adaptadores por especialidad (incluye `investigacion.json`); `adapter_schema.json` define su forma |
| `workflow.json` | Máquina de estados del ciclo |
| `onboarding/` | Cuestionario, generador del perfil y sus pruebas |
| `scripts/` | `validar_upo.py` (valida la skill) y `resultado_purgado.py` (valida el Resultado de una hija) |

Para añadir un dominio: copia `dominios/investigacion.json`, ajústalo a `adapter_schema.json`, añade su fila en la sección 3 de `SKILL.md` y corre el validador.

## Licencia

MIT. Ver `LICENSE`.
