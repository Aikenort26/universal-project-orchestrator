# Contrato de delegación portable (UPO v2)

Qué formato usa cada ejecutor:

| Ejecutor | Formato del encargo |
|---|---|
| Sesión hija o nieta de Claude | `plantillas/PLANTILLA_BRIEF.md` (regla S4: marcador, padre, nivel, modelo, techos, estado, reporte al padre). No usar el XML. |
| Subagente de Claude, agy, OpenCode, Codex, modelo local | Brief XML de este archivo |
| Obrero de una hija (regla S11) | `plantillas/PLANTILLA_BRIEF_OBRERO.md`; agy solo para lectura masiva sin orden (`analyze_files`, `deep_search`, `web_lookup`); `delegate`, `follow_up` y `adversarial_review` solo por orden expresa del usuario |

El XML es texto plano para que lo entienda cualquier modelo sin herramientas propias.

## 1. Brief XML

```xml
<brief>
  <objetivo>Una frase con el resultado esperado.</objetivo>
  <insumos>Rutas absolutas de solo lectura. Nada de rutas relativas.</insumos>
  <posee>Archivos o carpeta que solo este ejecutor escribe (regla S8).</posee>
  <prohibido>Qué no tocar; siempre: decisiones, redacción en nombre del usuario, autores, envíos externos, push, saltar hooks.</prohibido>
  <pasos>Opcional: pasos numerados cuando el orden importa.</pasos>
  <hecho_cuando>Condición verificable por comando o inspección (archivo existe, JSON válido, total cuadra).</hecho_cuando>
  <respaldo>Ruta del respaldo previo, si el ejecutor escribe sobre archivos existentes.</respaldo>
  <presupuesto>Tiempo o tamaño máximo; para agy, trozos pequeños (unos 20 a 25 KB por llamada).</presupuesto>
  <reporte>Extensión máxima del reporte (la de S6 salvo que se pida menos): resultado, archivos tocados, verificación hecha, pendientes, riesgos.</reporte>
</brief>
```

Reglas del brief:
- Una tarea por brief. Si hay dos entregables independientes, dos briefs.
- El brief se basta solo: el ejecutor no ve la conversación.
- Los datos de cálculo se pasan por ruta al archivo canónico (`DATOS_*.json`, hoja, plano), nunca copiados en el prompt.

## 2. Reporte y canal de retorno

| Ejecutor | Retorno | Corrección |
|---|---|---|
| Sesión hija | `SendMessage` con `to` = id `local_...` de la marca `padre=` ("parent" no resuelve); intermedios con prefijo `[HANDSHAKE]`, `[HANDOFF]` o `[CONSULTA]` en 150 palabras o menos; final tras validar `## Resultado` | `SendMessage` de la principal al id de la hija |
| Obrero subagente | resultado de `Agent` | `SendMessage` al mismo subagente |
| agy | respuesta de `delegate` con `session_id` | `mcp__agy-bridge__follow_up` con ese `session_id` |
| OpenCode, Codex | salida del CLI o archivo de reporte que pida el brief | nuevo brief con el reporte anterior como insumo |
| Modelo local | salida estándar | nueva llamada; nunca se aprueba sin revisión de Claude |

## 3. Puerta de revisión (la aplica el conductor o el auditor)

1. Antes de delegar escritura: respaldo en una ruta que vea el auditor (carpeta `_respaldo_<agente>_<fecha>/` del proyecto) y declararla en `<respaldo>`.
2. Al recibir: comprobar `hecho_cuando` con un comando propio, no con la palabra del ejecutor.
3. La sesión principal no lee el diff: recibe solo el veredicto y la evidencia del comando de `hecho_cuando`. El auditor (distinto del ejecutor) revisa el diff completo si es corto; si es largo, muestreo dirigido (cálculos, totales, nombres propios, rutas). Para scripts, sembrar un error en una copia y ver que lo detectan.
4. Veredicto escrito en el estado, contrastado contra el contrato de aceptación de la fase 1: **Aprobada**, **Con corrección** (qué se corrigió) o **No aprobada** (se devuelve o se reasigna).
5. Criterio del UPO: quien audita no es quien ejecutó (refuerza la auditoría de S10 con un segundo par de ojos).

## 4. Lista de control de fallos conocidos

| Fallo | Señal | Acción |
|---|---|---|
| El ejecutor agota tiempo | respuesta cortada o vacía | partir la tarea; reintentar una vez |
| Cuota agotada (429) | error 429 en el log del ejecutor | cambiar de modelo; si no hay otro, informar al usuario, no absorber en silencio |
| MCP de agy sin conectar | "MCP still connecting" | revisar el log de agy |
| Afirma una verificación que no se puede reproducir | p. ej. dice usar una librería que no está instalada | repetir la verificación con un comando propio |
| Datos personales en la salida | correos o documentos de identidad de personas naturales | borrar antes de aprobar |
| Inventa rutas o cifras | rutas inexistentes, totales que no cuadran | No aprobada; rehacer con insumos explícitos |
| Escribe fuera de `posee` | archivos tocados no declarados | revertir desde el respaldo |
| Encuentra cambios ajenos en un repo | `git status` sucio | detenerse y consultar al usuario; no descartar |
