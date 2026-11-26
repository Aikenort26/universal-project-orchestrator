[SESION-HIJA nivel=<1 o 2> padre=<id local_...>]   <- primera línea del prompt, obligatoria (regla S0)
# Brief: <nombre-corto>
- Principal: <id local_...> | Padre: <id> | Nivel: <1 o 2>
- Objetivo (una frase):
- Archivos que posees (solo tú los editas):
- Archivos de solo lectura:
- Prohibido tocar:
- Hecho cuando (verificable):
- Modelo / esfuerzo / techo de contexto: <modelo de hija del perfil> / medium / relevo en <techo de hija del perfil> (S3; sus obreros van con el modelo de ejecución del perfil)
- Reglas: references/reglas-s.md de la skill; en el techo, HANDOFF.md y reporte a la principal; subtarea independiente, propuesta a la principal; profundidad máxima 2; sin push, merge ni envíos externos.
- Estado: escribir en ~/.claude/upo/sesiones/activas/<nombre-corto>.md (copia de plantillas/PLANTILLA_ESTADO.md).
- Cierre: bloque Resultado de plantillas/PLANTILLA_RESULTADO.md en el estado, validado con scripts/resultado_purgado.py, y reporte de 150 palabras o menos al padre. Mensajes intermedios al padre: prefijo [HANDSHAKE], [HANDOFF] o [CONSULTA], 150 palabras o menos.
- Fases S11: 01_HANDSHAKE.md a 04_EJECUCION.md en ~/.claude/upo/sesiones/<nombre-corto>/.
