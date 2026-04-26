# Guía de contribución

¡Gracias por tu interés en contribuir a IPTV Player! Este documento describe las pautas para participar en el proyecto.

## Cómo contribuir

### Reportar errores

- Revisa los [issues existentes](https://github.com/gerardbourguett/iptv/issues) para evitar duplicados.
- Abre un nuevo issue con un título descriptivo y una explicación clara del problema.
- Incluye los pasos para reproducir el error, el comportamiento esperado y el comportamiento observado.
- Especifica la versión de Python, el sistema operativo y la versión de VLC que utilizas.

### Proponer mejoras

- Abre un issue con el prefijo `[Feature]` en el título.
- Describe la mejora, el problema que resuelve y posibles alternativas.

### Enviar cambios de código

1. Haz un fork del repositorio.
2. Crea una rama descriptiva: `git checkout -b feature/nombre-de-la-mejora`.
3. Realiza tus cambios siguiendo el estilo de código existente.
4. Asegúrate de que todas las pruebas pasen ejecutando `pytest`.
5. Ejecuta `ruff check src tests` y `mypy src` para verificar calidad.
6. Escribe mensajes de commit claros y descriptivos en español neutro o inglés.
7. Abre un pull request vinculando el issue correspondiente si aplica.

## Estilo de código

- Python 3.12+ con anotaciones de tipo en funciones públicas.
- Usa dataclasses para modelos de datos.
- Sigue las convenciones de formato de `ruff`.
- Mantén las funciones puras cuando sea posible; minimiza los efectos secundarios.

## Código de conducta

Este proyecto se rige por nuestro [Código de conducta](CODE_OF_CONDUCT.md). Al participar, se espera que respetes estas normas.
