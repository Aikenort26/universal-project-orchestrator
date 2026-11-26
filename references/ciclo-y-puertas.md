# Ciclo de trabajo y puertas (UPO v2)

Aplicación de la regla S10 (Planificar, Ejecutar, Auditar) a proyectos técnicos. La máquina de estados está en `workflow.json`; aquí, el criterio de cada fase. Ninguna fase avanza sin pasar su puerta. Quién hace cada fase y con qué archivo de la cadena S11 (handshake, scavenge, mapping, ejecución): tabla de la sección 2 de `SKILL.md`. La principal no lanza subagentes para el trabajo (S11): donde abajo se dice "hija", sus obreros viven dentro de ella. `<SES>` es `~/.claude/upo/sesiones/`.

## Fase 0. Arranque
- Leer, en este orden y sin releer lo ya resumido: `HANDOFF.md` de la carpeta del proyecto, el archivo de la sesión en `<SES>/activas/` y las notas del proyecto que el usuario indique.
- Si falta contexto: Grep o Glob puntual en la carpeta del proyecto; después lectura por rangos.
- Elegir el adaptador de dominio en `dominios/` por sus `disparadores`. Si coinciden dos, uno es el principal (el del entregable final) y del secundario solo se suman sus `puertas_dominio`.
- **Puerta:** estado previo leído, alcance en una frase y dominio elegido. **Si falla:** preguntar al usuario.

## Fase 1. Planificar (conductor, modelo alto)
- Partir el trabajo en fases con entregable propio. Fases típicas:
  | Fase | Entregable | Ejecutor habitual |
  |---|---|---|
  | Recopilación | inventario de insumos, `DATOS_*.json` | scavenge de la hija, con obrero de lectura |
  | Cálculo o modelación | modelo, resultados, figuras | sesión hija de análisis |
  | Cantidades y presupuesto | xlsx trazable | sesión hija de cantidades |
  | Redacción | informe o artículo | sesión hija de Claude (nunca un ejecutor externo) |
  | Auditoría | dictamen | hija auditora distinta de la ejecutora |
- Para cada fase: dueño único de archivos (S8), `hecho_cuando`, hija que la ejecuta (según `roles-agentes.md` y S11) y nivel de modelo (S3, con los modelos del perfil).
- Contrato de aceptación: una sola lista numerada de parámetros verificables del proyecto, presentada junto con el plan. Cada `hecho_cuando` remite a ella y el auditor final la recorre punto por punto; el trabajo no se cierra hasta cumplirlos todos.
- **Puerta:** plan y contrato de aceptación presentados al usuario y preguntas respondidas. **Si falla:** replanificar.

## Fase 2. Ejecutar (modelo inferior, esfuerzo medio)
- Cada fase sale con su encargo: hijas con `plantillas/PLANTILLA_BRIEF.md`; obreros de la hija con `plantillas/PLANTILLA_BRIEF_OBRERO.md`; ejecutores externos, por orden del usuario, con el brief XML de `contrato-delegacion.md`.
- Relevo: de la principal, `HANDOFF.md` y sesión nueva (S1); de una hija, `HANDOFF.md` reportado a la principal (S4).
- Datos desacoplados de la vista: `DATOS_*.json` (fuente de verdad), luego motor de cálculo (script o MCP), luego generador del documento. Ninguna cifra del entregable se escribe a mano.
- **Puerta:** `hecho_cuando` comprobado por comando y reporte en formato. **Si falla:** informar y reasignar.

## Fase 3. Auditar (mismo nivel que planificó, otro agente)
- Puerta de revisión de `contrato-delegacion.md` más las `puertas_dominio` del adaptador.
- Para entregables a cliente o firma: un agente auditor distinto del ejecutor; segunda opinión de otra familia de modelos solo si el usuario lo pidió.
- **Puerta:** veredicto escrito. **Si falla:** devolver al ejecutor.

## Fase 4. Cerrar
La principal no edita más de 2 archivos (S1): si el cierre toca más, lo hace la hija de la última fase. Cada hija cierra con su bloque `## Resultado` validado (sección 1 de `SKILL.md`).
- Reglas de redacción y entregables del perfil en todo texto para terceros.
- Tablero (`<SES>/INDICE.md` y archivo de estado); `HANDOFF.md` si queda trabajo.
- **Puerta:** todo lo anterior hecho. **Si falla:** corregir antes de cerrar.
