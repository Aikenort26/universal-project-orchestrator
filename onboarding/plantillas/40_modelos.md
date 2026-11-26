## Modelos, sesiones y techos de contexto
- Sesión principal: modelo `$modelo_principal`. Orquesta: reparte el trabajo pesado en sesiones hijas, una por especialidad, y no lanza obreros por su cuenta.
- Sesiones hijas: modelo `$modelo_hijas`. Cada una dirige y revisa a sus obreros (`$modelo_obreros`) y entrega un bloque `## Resultado` validado.
- Fases de cada hija, con un archivo por fase: handshake (objetivo, alcance y criterio de terminado), scavenge (inventario de insumos), mapping (plan verificable) y ejecución (lo construido y su verificación).
- Techos de relevo: principal a $relevo_principal tokens; hija a $relevo_hija tokens. Al llegar, escribir `HANDOFF.md` y continuar en una sesión nueva.
- Profundidad máxima de dos niveles por debajo de la principal.
