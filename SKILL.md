---
name: universal-project-orchestrator
description: "Método multiagente con puertas (S10) y cadena S11: la principal reparte en sesiones hijas por especialidad. Usar al orquestar, repartir en hijas, handshake, scavenge, mapping, ejecución o [SESION-HIJA]."
---

## Cuándo usar

Método de trabajo multiagente: ciclo Arranque, Planificar, Ejecutar, Auditar, Cerrar con puertas verificables (S10) y cadena S11 (la principal reparte en sesiones hijas por especialidad; cada hija recorre handshake, scavenge, mapping y ejecución con obreros y cierra con Resultado validado). Usar cuando el usuario pida orquestar, repartir en sesiones o en hijas, o diga handshake, scavenge, mapping o ejecución; al iniciar o retomar un proyecto de varias fases (estudio, diseño, cantidades, informe, artículo); al abrir una sesión con [SESION-HIJA ...].

# Universal Project Orchestrator (UPO) v2.2

Un solo método: el ciclo UPO dice qué se decide; la cadena S11 dice quién lo hace y con qué archivo. Las reglas S0 a S11 se citan por identificador y se resumen en `references/reglas-s.md`. Las cifras (modelos y techos de relevo) salen del perfil del usuario, `~/.claude/upo/REGLAS_PERSONALES.md`.

Carpeta de sesiones (`<SES>`): `~/.claude/upo/sesiones/`, con `INDICE.md` (tablero), `activas/<nombre>.md` (estado de cada hija) y `<nombre>/` (carpeta de trabajo de cada hija). Plantillas en `plantillas/` de esta skill.

## 0. Paso cero (fijo)

Primera vez: si no existe `~/.claude/upo/perfil.json`, seguir `onboarding/CUESTIONARIO.md` antes de cualquier fase. Si existe, leer `~/.claude/upo/REGLAS_PERSONALES.md` una vez al arrancar y aplicarlas en todas las fases; si una regla del proyecto las contradice, gana la del proyecto.

## 1. Arranque inmediato (primer turno)

Papel: hija si la primera línea del prompt es `[SESION-HIJA nivel=N padre=local_...]`; si no, principal (S0).

**Principal** (modelo principal del perfil, esfuerzo alto, S3):
1. Umbral (S2, S11): 1 a 3 llamadas, hacerlo directo. Todo lo demás va a hijas; la principal no lanza subagentes ni obreros para el trabajo.
2. Partir la tarea por especialidad o dominio (sección 3): una hija por parte, máximo 4 a la vez (S8), cada archivo con un solo dueño. En este paso el reparto es solo una propuesta.
3. Plan y preguntas (puerta del usuario). Antes de abrir cualquier hija, presentar al usuario en el chat: (a) el plan, con una fila por hija (especialidad, objetivo, archivos que posee, `hecho_cuando`) y el contrato de aceptación del conjunto; (b) las preguntas que cambian el alcance, el reparto o el entregable, con `AskUserQuestion` (de 1 a 4, con la opción recomendada primero; si no hay dudas, se dice). Respondidas las preguntas (o si no hay ninguna), la principal abre las hijas en ese mismo turno sin esperar un "aprobado" del plan, y el usuario corrige sobre la marcha. El plan y las respuestas van al brief de cada hija, que arranca sin preguntas pendientes. Para preparar el plan la principal usa solo Grep puntual y lecturas cortas (S1).
4. Por hija, copiar `plantillas/PLANTILLA_BRIEF.md` con primera línea `[SESION-HIJA nivel=1 padre=<id local_... propio>]` (el id real, nunca "parent"; se ve con `mcp__ccd_session_mgmt__list_sessions` y `linked:true`) y abrirla con `mcp__ccd_session__start_session` (`context:"fresh"`, `name`, `model` y `effort` de hija según el perfil, `initiation:"user_asked"`, `background` con el brief).
5. Registrar la fila en `<SES>/INDICE.md` (solo la principal lo escribe, S7).
6. Al llegar `[HANDSHAKE]`: leer `01_HANDSHAKE.md` de la hija, compararlo con el plan y responder aprobado o con corrección por `SendMessage` a su id. `[CONSULTA]`: responder o preguntar al usuario. `[HANDOFF]`: abrir la reemplazante (S4).
7. Recibir solo el reporte purgado y el bloque `## Estado` de `<SES>/activas/<nombre>.md`; no leer diffs.
8. Auditar (puerta 3, obligatoria; recibir un reporte no es aprobarlo). Por cada hija: (a) correr `python scripts/resultado_purgado.py <SES>/activas/<nombre>.md`; (b) correr el comando de verificación de su `hecho_cuando` con salida filtrada y comprobar que el entregable existe en la ruta declarada; (c) dar veredicto Aprobada, Con corrección o No aprobada contra el contrato de aceptación. Entregable de riesgo (dinero, norma, envío externo, artículo): abrir una hija auditora distinta de la ejecutora y recibir solo su veredicto (S3). Una hija Con corrección o No aprobada recibe la corrección por `SendMessage` y se vuelve a auditar. No se cierra ni se dice "hecho" sin presentar al usuario la tabla de veredictos (hija, comando corrido, veredicto, pendiente).

**Hija** (modelo de hija del perfil, esfuerzo medio, S3):
1. `<nombre>` es el nombre corto de la línea `# Brief:`. Copiar `plantillas/PLANTILLA_ESTADO.md` a `<SES>/activas/<nombre>.md`, rellenar su cabecera (`id`, `nombre`, `padre` con el id de la marca, `nivel`, `objetivo`, `modelo`, `carpeta`, `posee`, `estado: en curso`) y crear la carpeta de trabajo `<SES>/<nombre>/`.
2. Escribir en orden, cada uno con su puerta (ninguna espera al usuario):
   - `01_HANDSHAKE.md`: objetivo, alcance, archivos que posee, hecho cuando. Enviar `[HANDSHAKE]` al padre y seguir sin esperar; si la principal corrige, ajustar.
   - `02_SCAVENGE.md`: fuentes y datos reunidos, con ruta. Lectura masiva con un obrero de lectura (subagente o, si está instalado, agy por S11).
   - `03_MAPPING.md`: qué cambia, en qué archivo y con qué fuente. Mapping de riesgo (dinero, norma, envío externo, artículo): dos obreros independientes y la hija resuelve las diferencias.
   - `04_EJECUCION.md`: lo hecho y el comando que lo verifica. Obreros con el modelo de obrero del perfil (`Agent` con `model`) para ejecutar y editar.
3. Obreros: brief con `plantillas/PLANTILLA_BRIEF_OBRERO.md`. Calificar cada salida Aprobada, Con corrección o No aprobada; una No aprobada se rehace hasta 2 veces y al tercer fallo sube como fallo. Si un ejecutor externo falla, pasa un obrero de Claude y se anota en `Incidentes`.
4. Cierre: bloque `## Resultado` de `plantillas/PLANTILLA_RESULTADO.md` en el estado, con una fila por obrero. Validar:
   `python scripts/resultado_purgado.py <SES>/activas/<nombre>.md`
   Luego reporte final de 150 palabras o menos. Veredicto `fallido` es válido.
5. Mensajes al padre: `SendMessage` con `to` = el id `local_...` de la marca `padre=`; "parent" no resuelve. Los intermedios llevan prefijo `[HANDSHAKE]`, `[HANDOFF]` o `[CONSULTA]` y 150 palabras o menos.
6. Techos de hija (S4): los del perfil; en el relevo, `HANDOFF.md` y mensaje `[HANDOFF]`. Nietas solo según S5.

## 2. Ciclo UPO y cadena S11

| Etapa UPO | Puerta UPO | Quién y fase S11 | Archivo |
|---|---|---|---|
| 0 Arranque | estado previo leído, alcance en una frase, dominio elegido | principal (paso cero y umbral); en cada hija, handshake | `01_HANDSHAKE.md` |
| 1 Planificar | plan y contrato de aceptación presentados y preguntas respondidas antes de abrir hijas (sección 1, paso 3; las puertas de la hija no esperan al usuario) | principal reparte por especialidad; cada hija hace scavenge y mapping de su parte | `02_SCAVENGE.md`, `03_MAPPING.md` |
| 2 Ejecutar | `hecho_cuando` comprobado por comando | hija con obreros | `04_EJECUCION.md` |
| 3 Auditar | veredicto Aprobada, Con corrección o No aprobada; auditor distinto del ejecutor | hija revisa cada obrero; principal audita cada hija y presenta los veredictos (sección 1, paso 8) | tabla de obreros del Resultado |
| 4 Cerrar | reglas de redacción del perfil, tablero, HANDOFF si queda trabajo | hija valida Resultado y reporta; principal actualiza `INDICE.md` | `activas/<nombre>.md` |

Criterio de cada puerta: `references/ciclo-y-puertas.md`. Máquina de estados: `workflow.json` (campo `cadena_s11`).

## 3. Especialidad o dominio

Cada hija carga solo el adaptador cuyos `disparadores` coinciden con su parte:

| Dominio | Adaptador |
|---|---|
| Artículos, tesis, revisiones de literatura | `dominios/investigacion.json` |

Si coinciden dos, el del entregable final es el principal y del otro solo se suman sus `puertas_dominio`. Dominio nuevo (por ejemplo, hidráulica, presupuesto o contratación): copiar `dominios/investigacion.json`, ajustarlo a `adapter_schema.json`, añadir su fila a esta tabla y correr el validador.

## 4. Skills de apoyo

| Necesidad | Skill |
|---|---|
| Plan escrito de varias fases | skill:superpowers:writing-plans |

## 5. Agentes y delegación

- Quién hace qué: `references/roles-agentes.md`. Cómo se pide y se revisa: `references/contrato-delegacion.md`.
- Modelos: S3. Un dueño por archivo: S8.
- Ejecutores externos (agy, OpenCode, Codex, Ollama) solo por orden del usuario; la excepción es la lectura masiva con agy de S11.
- Nunca se delega: decisiones, redacción en nombre del usuario, autores y afiliaciones, envíos, push.

## 6. Tokens e invariantes

- Cifras: el perfil; aplicación por fase: `references/tokens.md`.
- Autores, estilo y entregables: las reglas del perfil (`~/.claude/upo/REGLAS_PERSONALES.md`); autor desconocido, detenerse y preguntar.
- Sin símbolo de sección ni rayas largas en los textos de la skill (lo comprueba el validador).
- Entregables en la carpeta del proyecto, nunca en temporales.

## 7. Verificación y mantenimiento

- `python scripts/resultado_purgado.py <estado.md>`: valida el bloque `## Resultado` de una hija (sale con 1 si hay errores).
- Tras cualquier cambio a la skill: `python scripts/validar_upo.py --quiet`.
- Pruebas del cuestionario: `python -m pytest onboarding/test_generar_perfil.py -q -p no:cacheprovider`.
- Versión 1 de la skill: etiqueta `v1` del repositorio.
