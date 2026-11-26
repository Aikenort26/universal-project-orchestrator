# Roles de agentes (UPO v2)

El método es el mismo para todos los agentes; cambia el rol que cada uno puede ocupar. Las reglas comunes están en `reglas-s.md`; las cifras, en el perfil del usuario. Aquí solo el reparto de trabajo.

## Matriz

| Agente | Cómo recibe el trabajo | Rol permitido | Usar para | No usar para |
|---|---|---|---|---|
| Claude Code, sesión principal | el usuario | Conductor y auditor | Plan, decisiones, tablero, revisión | Ejecución pesada (va a hijas o ejecutores) |
| Claude Code, sesión hija | `start_session` fresh con `plantillas/PLANTILLA_BRIEF.md` | Ejecutor; propone nietas según S4 | Una fase de varios turnos o que edita archivos | Abrir nietas sin cumplir S4 |
| Obrero (subagente de Claude o agy) | `Agent` o agy-bridge, con `plantillas/PLANTILLA_BRIEF_OBRERO.md`, siempre dentro de una hija (S11) | Ejecutor; auditor de segunda opinión | Lectura masiva, ejecución y edición, revisado por la hija | Trabajo lanzado desde la principal |
| Antigravity (agy), si está instalado | `mcp__agy-bridge__delegate`, `analyze_files`, `web_lookup` | Ejecutor; revisor adversarial | Lotes mecánicos de un plan aprobado: JSON, scripts, copias, ediciones masivas; segunda opinión con `adversarial_review` | Decisiones, redacción en nombre del usuario, autores |
| Otro modelo vía OpenCode o Codex | CLI en la carpeta del proyecto con el brief XML como prompt | Ejecutor | Código y transformaciones de datos con criterio verificable | Igual que agy |
| Modelo local (Ollama u otro) | comando local que indique el perfil | Ejecutor menor | Resumir, clasificar, borradores | Fórmulas de dominio y cifras finales |

**Todo ejecutor externo (agy, OpenCode, Codex, Ollama) se usa solo por orden expresa del usuario en el mensaje; también `delegate`, `follow_up` y `adversarial_review` de agy. Excepción S11: la lectura masiva con agy (`analyze_files`, `deep_search`, `web_lookup`) no exige orden dentro de la cadena de tres niveles.** Sin orden, el ejecutor es Claude (hija, u obrero dentro de ella).

## Reglas de reparto

1. **Conductor único.** En una familia de sesiones solo la principal decide y lleva `~/.claude/upo/sesiones/INDICE.md`.
2. **Un dueño por archivo** (regla S8), declarado en el brief. Si dos agentes distintos deben escribir a la vez en el mismo proyecto, se reparten carpetas distintas; si no es posible, se detiene y se consulta al usuario.
3. **Modelos.** Cascada S10 (planificar alto, ejecutar inferior, auditar alto) con el nivel de ejecución que fija S3. Quien audita no es quien ejecutó.
4. **Elección del ejecutor** (en este orden):
   - 1 a 3 llamadas de trabajo: la propia sesión (excepción de S0).
   - Todo lo demás: sesión hija por especialidad (S11); dentro de ella, obrero de lectura para lectura masiva y obrero de Claude para ejecutar.
   - El usuario ordenó delegar fuera de Claude: agy para lotes y análisis de archivos grandes; OpenCode o Codex para código cuando el usuario lo nombre; modelo local solo para resumir o clasificar.
5. **Fallos de un ejecutor externo** se informan al usuario; no se absorben en silencio (lista de control en `contrato-delegacion.md`).
