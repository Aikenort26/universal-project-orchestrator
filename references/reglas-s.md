# Reglas S0 a S11 (resumen portable)

Las cifras (modelos, techos de aviso y relevo) no se fijan aquí: las pone el perfil de cada usuario en `~/.claude/upo/REGLAS_PERSONALES.md`. `<SES>` es `~/.claude/upo/sesiones/`.

| Regla | Nombre | Qué exige |
|---|---|---|
| S0 | Orquestadora desde el primer turno | Toda sesión sin padre es principal: presenta el plan de reparto y las preguntas que cambian el alcance, abre las hijas, audita cada reporte y presenta los veredictos antes de cerrar. No hace el trabajo ella misma salvo tareas de 1 a 3 llamadas. |
| S1 | Sesión principal | Guarda solo el tablero, las decisiones, los briefs y los reportes. Nada de lecturas largas, PDF, ofimática, imágenes ni ediciones en más de 2 archivos. Al llegar a su techo de relevo escribe `HANDOFF.md` (60 líneas o menos: objetivo, decisiones, hijas activas con su id, siguiente paso) y continúa en una sesión nueva. |
| S2 | Umbrales de delegación | Va a una hija si basta uno: más de 3 archivos, un archivo de más de 200 líneas, PDF, ofimática, imagen o navegador, más de 8 llamadas previstas, más de 25k tokens previstos o una fase de más de un turno. |
| S3 | Modelo y esfuerzo | Principal con el modelo más alto del perfil y esfuerzo alto; hijas con esfuerzo medio; obreros con el modelo de ejecución del perfil. Audita un agente distinto del ejecutor. |
| S4 | Sesión hija | Siempre contexto fresco, nunca bifurcado. Brief con `plantillas/PLANTILLA_BRIEF.md`. En su techo escribe `HANDOFF.md` y lo reporta a la principal, que abre la reemplazante. Una subtarea independiente se propone a la principal. |
| S5 | Profundidad | Máximo 2 niveles bajo la principal (hija y nieta). La nieta no abre más sesiones. |
| S6 | Reporte | Cada nivel reporta a quien lo creó por `SendMessage` al id `local_...` de su padre, en 150 palabras o menos, y deja el reporte en `<SES>/activas/<nombre>.md`. |
| S7 | Registro | Un solo escritor por archivo: `<SES>/INDICE.md` solo la principal; cada `activas/<nombre>.md` solo su sesión. |
| S8 | Límites | Máximo 4 hijas simultáneas. Cada hija declara los archivos que posee y nadie más los edita. En repositorios git, cada hija en su propio worktree. Nunca push, merge, publicación ni envíos externos sin visto bueno del usuario. |
| S9 | Compactación | La autocompactación es solo red de seguridad; si ocurre, se anota como incidente en el estado. |
| S10 | Planificar, Ejecutar, Auditar | Planificar con el modelo y esfuerzo más altos disponibles, ejecutar con el inmediatamente inferior y esfuerzo medio, auditar con el mismo nivel que planificó. |
| S11 | Cadena de tres niveles | Principal, hijas por especialidad, obreros dentro de cada hija. La hija recorre `01_HANDSHAKE.md` (lo aprueba la principal), `02_SCAVENGE.md`, `03_MAPPING.md` y `04_EJECUCION.md` (los aprueba la hija), califica a cada obrero y cierra con `## Resultado` validado. Lectura masiva con agy (si está instalado) sin orden expresa; ejecución con obreros de Claude. |
