# Cuestionario de primera instalación de UPO

Instrucciones para el agente. Se sigue una sola vez, cuando no existe `~/.claude/upo/perfil.json`, antes de cualquier fase de UPO. El resultado son dos archivos en `~/.claude/upo/`: `perfil.json` (respuestas) y `REGLAS_PERSONALES.md` (reglas que el agente carga desde entonces junto con la skill).

## Cómo preguntar
- Usar la herramienta de preguntas del agente (en Claude Code, `AskUserQuestion`). Si no existe, hacer las mismas preguntas en texto, una ronda por mensaje.
- Cuatro rondas, máximo cuatro preguntas por ronda, de dos a cuatro opciones por pregunta, con la opción recomendada primero y marcada "(Recomendada)".
- Toda pregunta admite texto libre (la opción "Otro" de la herramienta). Si la persona escribe texto libre en una pregunta de opciones, guardarlo como `"otro: <texto>"`. La única excepción es el plan (ver ronda 3).
- Antes de la ronda 1, explicar en dos frases para qué es el cuestionario y que se puede rehacer cuando quiera.
- Las respuestas se quedan en la máquina de la persona. No enviarlas a ningún servicio externo.
- Detectar lo que se pueda sin preguntar (idioma del sistema, si la carpeta actual es un repositorio git, herramientas instaladas como `ollama`) y usarlo para elegir la opción recomendada, nunca para saltarse la pregunta.

## Ronda 1: quién eres y qué produces
| Clave | Pregunta | Opciones (la primera es la recomendada) | Multi |
|---|---|---|---|
| `idioma` | ¿En qué idioma y variante regional quieres que escriba? | Variante del sistema detectada (por ejemplo `es-ES`); `es-MX`; `en-US`; `pt-BR` | no |
| `dominio` | ¿Cuál es tu profesión o dominio de trabajo? | Ingeniería; Investigación o docencia; Desarrollo de software; Consultoría o gestión | no |
| `entregables` | ¿Qué entregables produces con más frecuencia? | `informes`; `codigo`; `articulos`; `presentaciones` (si elige "Otro", ofrecer también `hojas_calculo`) | sí |
| `formalidad` | ¿Qué registro de redacción prefieres? | `tecnica` (neutra y precisa); `formal`; `cercana` | no |

`dominio` es texto: guardar la opción elegida tal cual o el texto libre. En `entregables`, la herramienta solo admite cuatro opciones: si la persona marca "Otro" y menciona hojas de cálculo, guardar `hojas_calculo`; cualquier otro texto va como `"otro: <texto>"`.

## Ronda 2: estilo y orden
| Clave | Pregunta | Opciones | Multi |
|---|---|---|---|
| `signos_prohibidos` | ¿Hay signos o construcciones que nunca quieras ver en tus textos? | Ninguno; raya larga en prosa; emojis; comillas tipográficas curvas | sí |
| `formato_numeros` | ¿Cómo escribes los números grandes y los decimales? | `punto_miles` (1.234,5); `coma_miles` (1,234.5); `espacio_miles` (1 234,5, estilo SI). Recomendar primero el habitual de la variante elegida en la ronda 1 | no |
| `formato_fecha` | ¿Qué formato de fecha usas? | `iso` (AAAA-MM-DD); `dia_mes_anio`; `mes_dia_anio` | no |
| `ubicacion_trabajo` | ¿Dónde vive tu trabajo? | `nube_sincronizada` (carpeta de Drive, OneDrive, Dropbox); `repositorio` (git); `local` | no |

`signos_prohibidos` es una lista de textos libres: "Ninguno" se guarda como lista vacía; cualquier otro texto se añade tal cual. Después de esta ronda, pedir en texto (sin herramienta) la ruta raíz del trabajo (`raiz_trabajo`, por ejemplo `~/Proyectos`) y la convención de nombres (`convencion_nombres`: `minusculas_guiones`, `prefijo_numerico`, `fecha_prefijo` u `"otro: <texto>"`); si la persona no responde, quedan los valores por defecto.

## Ronda 3: plan, modelos y herramientas
| Clave | Pregunta | Opciones | Multi |
|---|---|---|---|
| `plan` | ¿Qué presupuesto de tokens quieres usar? | `medio` (principal opus, hijas y obreros sonnet; relevo 150.000 y 120.000); `basico` (sonnet y haiku; relevo 120.000 y 100.000); `alto` (principal e hijas opus, obreros sonnet; relevo 300.000 y 240.000); `personalizado` | no |
| `herramientas_externas` | ¿Qué herramientas externas tienes disponibles? | Ninguna; `segundo_agente` (otro asistente de código o CLI); `modelo_local` (por ejemplo vía Ollama) | sí |
| `delegacion_automatica` | ¿Puede el agente delegar en esas herramientas sin pedírtelo? | `solo_lectura` (solo leer y resumir); `nunca`; `siempre` | no |

`plan` no admite texto libre: si la persona elige "Otro" o `personalizado`, preguntar en texto los tres modelos (`modelos`: `principal`, `hijas`, `obreros`) y los dos techos de relevo en tokens (`techos`: `relevo_principal`, `relevo_hija`, enteros), y guardar `"plan": "personalizado"`. Los techos deben quedar por debajo de la ventana de contexto del modelo, con margen para la respuesta. "Ninguna" en herramientas se guarda como lista vacía; si no hay herramientas, guardar `delegacion_automatica: "nunca"` sin preguntar.

## Ronda 4: autonomía
| Clave | Pregunta | Opciones | Multi |
|---|---|---|---|
| `puertas_humanas` | ¿En qué momentos quieres aprobar tú antes de que el agente siga? | `plan`; `entrega`; `borrado`; `redaccion_en_mi_nombre` (si elige "Otro" y menciona dinero, guardar `gasto`) | sí |
| `acciones_externas` | ¿Qué hace el agente con acciones hacia afuera (push, envíos, publicaciones)? | `siempre_preguntar`; `push_libre` (push a ramas propias sin preguntar); `todo_libre` | no |
| `alias` | ¿Cómo quieres que te nombre en las reglas? | Sin nombre; texto libre | no |

`puertas_humanas` necesita al menos una opción; si la persona no marca ninguna, recomendar `borrado` y volver a preguntar una vez.

## Qué hacer con las respuestas
1. Escribir `respuestas.json` en la carpeta temporal de la sesión con las claves de arriba. Ejemplo completo: `onboarding/ejemplos/respuestas_ejemplo.json`.
2. Ejecutar:
   ```
   python onboarding/generar_perfil.py --respuestas <ruta>/respuestas.json
   ```
   Por defecto escribe en `~/.claude/upo/`. Si responde con `error:`, corregir la clave que nombra (preguntando de nuevo solo esa) y repetir.
3. Mostrar a la persona un resumen de cinco líneas de `REGLAS_PERSONALES.md` y su ruta. No pegar el archivo entero.
4. Desde entonces, cargar `~/.claude/upo/REGLAS_PERSONALES.md` al empezar cualquier fase de UPO.

## Rehacer o ajustar
- Rehacer todo: repetir el cuestionario y ejecutar el generador con `--forzar`.
- Ajustar una respuesta: editar `perfil.json` (bloque `respuestas`), copiarlo como `respuestas.json` y ejecutar con `--forzar`.
- Editar a mano `REGLAS_PERSONALES.md` también vale, pero se pierde al rehacer el perfil.

## Qué no se pregunta
Las reglas de contexto y tokens, de honestidad y de verificación son iguales para todos y van siempre (plantilla `10_universal.md`). Nunca preguntar ni guardar datos sensibles: contraseñas, claves de API, correos de terceros ni nombres de clientes.
