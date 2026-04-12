# Registro de cambios

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [0.2.0] - 2026-04-12

### Añadido

- **Perfiles de usuario**: pantalla de selección de perfil al iniciar; cada perfil guarda su propia lista M3U, favoritos y canales recientes de forma independiente
- **Gestión de perfiles**: crear, renombrar, cambiar color de avatar y eliminar perfiles desde la barra superior; cambio de perfil sin reiniciar la aplicación
- **Favoritos y Recientes**: secciones fijas en la parte superior de la lista de canales; los favoritos se gestionan con clic derecho; los últimos 20 canales reproducidos se añaden automáticamente a Recientes
- **Modo pantalla completa de video** (`F11`): oculta la lista de canales, barra de herramientas y barra de estado para maximizar el área de reproducción; `Esc` restaura la vista normal
- **Modos de visualización múltiple**: grilla de 1, 2 o 4 reproductores simultáneos; accesibles por teclas `1`, `2`, `4` o desde la barra de herramientas
- **Atajos de teclado**: `M` para silenciar, `Espacio` para detener, `1`/`2`/`4` para cambiar el modo de vista
- **Auto-carga de lista**: al seleccionar un perfil, su lista M3U se carga automáticamente sin intervención del usuario
- **Auto-mejora de URL** `/m3u` a `/m3u_plus`: si la lista original no tiene grupos, se reintenta con la variante `m3u_plus` para obtener metadatos de grupo

### Corregido

- **Parser M3U**: las directivas intermedias (`#EXTGRP`, `#KODIPROP`, `#EXTVLCOPT`) entre `#EXTINF` y la URL de stream ya no provocan que el canal sea descartado
- **Codificación de archivos M3U**: los archivos en latin-1 o cp1252 (comunes en proveedores latinoamericanos) se decodifican correctamente; antes fallaban silenciosamente dejando la lista vacía
- **Persistencia de lista**: abrir una lista vía File > Open Playlist o File > Open URL ahora guarda correctamente la ruta/URL en el perfil activo para la próxima sesión
- **Panel de canales desaparecía entre sesiones**: al cerrar la aplicación con pantalla completa activa, los tamaños del splitter se guardaban como `[0, X]`; al reiniciar el panel izquierdo quedaba con ancho 0 e invisible; corregido guardando siempre el estado normal (pre-fullscreen)
- **Botones `+` y `⚙` del perfil**: no realizaban ninguna acción; ahora abren los diálogos de nuevo perfil y configuración de perfil respectivamente
- **Encabezados de grupos colapsables**: al colapsar un grupo, el encabezado desaparecía; ahora permanece visible para permitir expandirlo nuevamente
- **Cursor del puntero**: al cerrar el diálogo de selección de perfil en Windows, el cursor quedaba como mano (PointingHandCursor); se fuerza el reset al pasar a la ventana principal

### Cambiado

- El panel de canales ahora tiene ancho mínimo garantizado; el splitter no puede colapsar el panel a 0
- El texto de la interfaz usa español neutro en lugar de voseo rioplatense

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
