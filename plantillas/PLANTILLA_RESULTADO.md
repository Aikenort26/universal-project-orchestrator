## Resultado
- veredicto: logrado | parcial | fallido
- resumen: <80 palabras o menos>
- fases: handshake=aprobada; scavenge=aprobada; mapping=aprobada; ejecucion=aprobada
- entregables: <rutas absolutas separadas por ";", o "ninguno">
- verificacion: <comando o evidencia que lo prueba>
- pendientes: <texto o "ninguno">
- riesgos: <texto o "ninguno">

| obrero | modelo | fase | intentos | revision |
|---|---|---|---|---|
| extraccion-datos | subagente de lectura | scavenge | 1 | Aprobada |

Reglas que valida `scripts/resultado_purgado.py`:
- Los siete campos van presentes y no vacíos.
- `veredicto` es logrado, parcial o fallido.
- `resumen` tiene 80 palabras o menos.
- Cada fase vale `aprobada` u `omitida(<motivo>)`.
- Hay al menos una fila de obrero, con `fase` en handshake, scavenge, mapping o ejecucion.
- `intentos` es un entero de 1 a 3.
- `revision` es Aprobada, Con corrección o No aprobada.
- Con una fila No aprobada, el veredicto no puede ser logrado.
- Con veredicto distinto de fallido, cada entregable debe existir en disco; con fallido vale `ninguno`.
