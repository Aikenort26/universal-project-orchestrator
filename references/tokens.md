# Economía de tokens (UPO v2)

Las cifras (techos y relevos) viven en el perfil del usuario (`~/.claude/upo/REGLAS_PERSONALES.md`) y los umbrales de delegación en S2 (`reglas-s.md`); aquí no se copian para que no deriven. Este archivo dice cómo aplicarlas en un proyecto.

## Divulgación progresiva de la skill
| Capa | Qué se carga | Cuándo |
|---|---|---|
| 1 | `SKILL.md` | siempre que se activa la skill |
| 2 | un `dominios/<dominio>.json` | al elegir el dominio en la fase 0 |
| 3 | un `references/*.md` | solo el de la fase en curso |
| 4 | skills del dominio (`skills` del adaptador) | solo la de la fase en curso |

Nunca cargar todos los dominios ni todas las referencias "por si acaso".

## Presupuesto por fase
| Fase | Dónde corre | Gasto que se acepta en la principal |
|---|---|---|
| 0 Arranque | principal | lectura de estado y Grep puntual; nada de PDF ni ofimática |
| 1 Planificar | principal; scavenge y mapping en cada hija | plan y preguntas; la exploración amplia va al scavenge de una hija |
| 2 Ejecutar | hijas con sus obreros (S11) o ejecutores externos por orden del usuario | solo briefs, mensajes con prefijo y reportes con la extensión de S6 |
| 3 Auditar | hija, que revisa a cada obrero | veredicto y bloque Resultado |
| 4 Cerrar | principal si edita 2 archivos o menos (S1); si no, la hija de la última fase | comandos de verificación con salida filtrada |

## Hábitos que más ahorran
- PDF y ofimática a texto o por script antes de leer (pdftotext, markitdown, openpyxl); nunca el binario en la principal.
- Planos y modelos: consultar por script o MCP e imprimir solo lo necesario.
- Datos en `DATOS_*.json` y el ejecutor recibe la ruta, no el contenido.
- Salidas de comandos filtradas (`Select-Object -Last N`, `head`) o a archivo con resumen.
- Figuras: guardar PNG y verificar por script antes de mirarlas.
- Lo mecánico y especificado va a un ejecutor externo cuando el usuario lo ordena: su consumo no cuenta en el contexto de Claude.
- Relevo en el techo con `HANDOFF.md`; la autocompactación es un incidente, no un método.
