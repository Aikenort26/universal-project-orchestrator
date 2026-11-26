# Primera instalación de UPO

UPO trae un método de trabajo multiagente con reglas por defecto. La primera vez que se usa, el agente hace un cuestionario corto (cuatro rondas) y genera reglas personales: idioma, estilo de redacción, organización de carpetas, modelos y techos de contexto, delegación y autonomía.

## Instalar
1. Clonar el repositorio directamente como skill (la raíz del repositorio es la skill):
   - Para todos los proyectos: `git clone https://github.com/Aikenort26/universal-project-orchestrator.git ~/.claude/skills/universal-project-orchestrator`
   - Solo para un proyecto: el mismo clon en `<proyecto>/.claude/skills/universal-project-orchestrator/`
2. Requisito: Python 3.9 o superior (solo biblioteca estándar). Las pruebas usan pytest.

## Cómo se dispara el cuestionario
Al invocar la skill, el agente comprueba si existe `~/.claude/upo/perfil.json`. Si no existe, sigue `onboarding/CUESTIONARIO.md` antes de cualquier fase. Al terminar quedan:
- `~/.claude/upo/perfil.json`: las respuestas.
- `~/.claude/upo/REGLAS_PERSONALES.md`: las reglas que el agente carga desde entonces.

Nada sale de la máquina: el cuestionario no envía las respuestas a ningún servicio.

## Rehacer el perfil
- Pedirle al agente "rehaz mi perfil de UPO", o bien:
  ```
  python onboarding/generar_perfil.py --respuestas mis_respuestas.json --forzar
  ```
- Sin `--forzar`, el generador nunca sobrescribe un perfil existente.
- Para otra carpeta destino: `--salida <carpeta>`.

## Contenido
| Archivo | Para qué |
|---|---|
| `CUESTIONARIO.md` | Instrucciones para el agente: rondas, preguntas, opciones y qué hacer con cada respuesta |
| `generar_perfil.py` | Valida las respuestas y escribe los dos archivos |
| `plantillas/` | Fragmentos de regla; el generador elige los bloques según las respuestas |
| `ejemplos/respuestas_ejemplo.json` | Respuestas de una persona ficticia |
| `test_generar_perfil.py` | Pruebas: `python -m pytest onboarding/test_generar_perfil.py -q -p no:cacheprovider` |

## Adaptar las plantillas
Cada archivo de `plantillas/` tiene una parte fija (antes del primer marcador) y bloques `<!-- bloque: nombre -->` que se eligen por respuesta. Para añadir una opción: crear el bloque con el nombre de la opción, añadir el valor a `OPCIONES` en `generar_perfil.py` y una prueba.
