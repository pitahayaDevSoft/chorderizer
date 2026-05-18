# QP Audit: Chorderizer
## Analysis of Robustness, Performance, and Quality

| Category | Critical Finding | Impact | Solution Reference |
| :--- | :--- | :--- | :--- |
| **Robustez** | **Falta de Fallback UI**: Si la dependencia `Textual` falla al importar, la aplicación se cierra inmediatamente. | **Alto**: Inutilizable en terminales antiguos o entornos restringidos sin soporte Unicode/Color. | Implementar un modo "Basic CLI" basado en texto plano si falla la carga de la TUI. |
| **Funcionamiento** | **Sanitización Insuficiente de Paths**: `_sanitize_path` fuerza el uso de `os.path.basename`. | **Medio**: Impide al usuario organizar sus MIDI en subcarpetas dentro del directorio de exportación. | Validar que el path final esté dentro del `base_dir` permitido en lugar de recortar el path a un solo nombre. |
| **Utilidad** | **Generación de MIDI Determinista**: Los nombres de archivo colisionan si se usa la misma tonalidad/escala. | **Medio**: El usuario pierde progresiones anteriores si genera una nueva en la misma tonalidad sin renombrar. | Incluir un timestamp o un sufijo incremental automático en el nombre de archivo sugerido. |

## General Codebase Audit (Deep Pass)

| Category | Finding | Impact | Recommendation |
| :--- | :--- | :--- | :--- |
| **Robustez** | **Excepciones Silenciosas en TUI**: Bloques `except Exception:` en el loop principal de `tui_app.py`. | **Crítico**: Si la interfaz falla por un error de lógica, el usuario solo verá el cierre de la app sin saber por qué. | Capturar excepciones específicas y registrarlas en un archivo de log local (`chorderizer.log`). |
| **Arquitectura** | **Lógica en el Script Principal**: `chorderizer.py` contiene tanto orquestación como lógica de helper. | **Bajo**: Dificulta las pruebas unitarias aisladas de las funciones de ayuda. | Mover los helpers de nombres de archivo y sanitización a un módulo `utils.py` separado. |
| **Rendimiento** | **Carga de Dependencias en Inicio**: La carga de librerías de teoría musical puede ser lenta. | **Bajo**: Retraso perceptible al abrir la aplicación. | Implementar lazy loading para los módulos de generación más pesados (ej. MIDI generator). |
