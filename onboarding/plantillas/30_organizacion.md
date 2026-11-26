## Organización de archivos
- El trabajo vive en `$raiz_trabajo`. No listar ni indexar la raíz completa: trabajar solo en la subcarpeta del proyecto.
- Los entregables se escriben en su carpeta final del proyecto, nunca en carpetas temporales, y se enlazan con ruta absoluta.
- Lo temporal (borradores, salidas intermedias) va a la carpeta temporal de la sesión.

<!-- bloque: nube_sincronizada -->
- La carpeta está sincronizada con la nube: abrir los archivos por la ruta local montada, no por un conector web.
- Cachés y dependencias (`node_modules`, `__pycache__`, `.pytest_cache`, entornos virtuales) no viven en la carpeta sincronizada; pytest con `-p no:cacheprovider`.
<!-- bloque: local -->
- La carpeta es local: antes de borrar o mover en bloque, confirmar que existe una copia de respaldo.
<!-- bloque: repositorio -->
- El trabajo vive en repositorios git: una rama por tarea, commits pequeños y nunca saltar los hooks.
<!-- bloque: otro_ubicacion_trabajo -->
- Ubicación del trabajo indicada por la persona: $texto.
<!-- bloque: minusculas_guiones -->
- Nombres de archivos y carpetas en minúsculas, sin tildes ni espacios, con guiones: `informe-final-v2.md`.
<!-- bloque: prefijo_numerico -->
- Carpetas con prefijo numérico de dos cifras para fijar el orden (`01-entrada`, `02-calculos`, `99-inbox`); archivos sin espacios.
<!-- bloque: fecha_prefijo -->
- Archivos con la fecha ISO al inicio (`2026-01-31_acta.md`) para que el orden alfabético sea cronológico.
<!-- bloque: otro_convencion_nombres -->
- Convención de nombres indicada por la persona: $texto.
