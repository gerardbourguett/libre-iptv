# Registro de cambios

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

## [0.1.0] - 2026-04-12

### Añadido

- **Parser M3U**: lectura de archivos `.m3u` y `.m3u8` con soporte para metadatos `#EXTINF` (nombre, grupo, logo, tvg-id); disponible también como `parse_m3u_url` para descarga directa desde una URL
- **Ventana principal**: interfaz con panel lateral de canales y reproductor VLC embebido, conectados mediante un splitter horizontal redimensionable; tamaño mínimo de 900 × 600 px
- **Agrupación de canales**: la lista agrupa automáticamente los canales por `group-title`; los canales sin grupo se colocan bajo la categoría "Uncategorized"
- **Búsqueda de canales**: campo de texto con filtrado en tiempo real por nombre de canal, insensible a mayúsculas y minúsculas; los encabezados de grupo se ocultan automáticamente cuando ningún canal del grupo coincide con la búsqueda
- **Carga desde URL**: opción **File > Open URL...** para ingresar una URL de lista M3U; la descarga se realiza en un hilo de fondo (`QThread`) para mantener la interfaz responsiva durante la obtención
- **Carga desde archivo**: opción **File > Open Playlist** con diálogo de selección de archivo filtrado a extensiones `.m3u` y `.m3u8`
- **Controles de reproducción**: slider de volumen (0–100), botón de silencio con texto alternante ("Mute" / "Unmute") y botón de detención integrados en una barra fija bajo el área de video
- **Barra de estado**: muestra el nombre del canal en reproducción, el número de canales cargados y mensajes de error de descarga
- **Persistencia de configuración**: la aplicación recuerda el tamaño y posición de la ventana, el ancho del panel lateral y la ruta de la última lista local cargada, usando `QSettings` en formato INI en el perfil del usuario
- **Suite de pruebas**: 76 pruebas automatizadas con pytest y pytest-qt, cobertura configurada con `--cov=src`
