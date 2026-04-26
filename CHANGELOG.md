# Registro de cambios

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [0.3.0] - 2026-04-26

### Añadido

- **Interfaz Libre IPTV v2** (`main_v2.py`): nueva experiencia de usuario estilo Netflix con navegación por pantallas (`ScreenNavigator`) basada en `QStackedWidget`; el entry point original (`main.py`) se conserva como fallback
- **HomeScreen**: pantalla de inicio con filas horizontales de canales (*Continuar viendo*, *En vivo*) con scroll horizontal; cada fila se oculta automáticamente si no tiene contenido
- **LiveTvScreen**: pantalla de TV en vivo con distribución 70/30 (lista de canales | reproductor VLC), zapping con teclas ↑↓, búsqueda por texto en tiempo real, etiqueta EPG "ahora/siguiente" y Escape para volver
- **Sistema de temas**: 4 temas visuales — Midnight (oscuro azul), Ocean (oscuro teal), Ember (oscuro naranja), Abyss (oscuro púrpura) — aplicados a toda la aplicación vía `QPalette` + stylesheet global; el tema se guarda por perfil
- **Soporte EPG (Guía Electrónica de Programas)**: parser XMLTV con streaming iterparse y soporte gzip; worker `EpgService` en `QThread`; caché JSON por canal; visualización de programa actual y siguiente en la lista de canales
- **Internacionalización (i18n)**: sistema de traducción JSON con función `t()`, cambio de idioma en tiempo de ejecución, locales `es.json` y `en.json` con más de 105 claves; scanner AST para detectar cadenas hardcodeadas
- **Control parental**: PIN con hash SHA-256 salted, bloqueo por canal y por grupo, `PinDialog` con campo enmascarado, panel de administración `ParentalControlsPanel`
- **Logos de canales**: carga asíncrona con `QThread`, caché LRU en memoria (200 entradas), caché en disco, delegado `QStyledItemDelegate` con círculo de color como fallback
- **Overlay de carga**: spinner animado sobre el reproductor durante la carga de la lista; estado del menú deshabilitado mientras carga
- **Notificaciones toast**: mensajes de confirmación/error con auto-dismiss (3 s)
- **Instancia VLC compartida**: `VlcManager` singleton que gestiona el ciclo de vida de libvlc; inyectado por dependencia en `PlayerWidget` y `GridPlayerWidget`
- **SourceManager**: gestión de múltiples fuentes M3U por perfil (tipo URL/archivo, activar/desactivar); reemplaza el modelo de una sola playlist por perfil
- **SettingsManager**: configuración en JSON con escritura atómica y lock de hilo; reemplaza `QSettings`; soporta migración de valores por defecto
- **CacheSystem**: caché de canales (24 h), EPG (12 h) y logos (disco); validación por TTL y escritura thread-safe
- **Detección VOD/Series**: el parser M3U clasifica automáticamente canales como live, VOD o serie por palabras clave en nombre/grupo; soporte para `tvg-chno`
- **Refactorización de ventana principal**: extracción de `MenuBuilder`, `PlaylistService` y `ProfileController` como servicios independientes en `src/services/`
- **Soporte multiplataforma**: abstracción `src/platform.py` con `platformdirs` para rutas de config/cache/datos; detección automática de VLC en Windows/macOS/Linux; specs PyInstaller para las 3 plataformas; matrix CI en GitHub Actions
- **Proyecto open source**: licencia MIT, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant), `SECURITY.md`, `AboutDialog` con enlaces de donación

### Cambiado

- Los specs de PyInstaller apuntan ahora a `main_v2.py` e incluyen los archivos de localización i18n
- El ejecutable se distribuye como **Libre-IPTV** en las tres plataformas
- Versión del proyecto actualizada a `0.3.0`

### Corregido

- `src/models/channel.py` requiere `from __future__ import annotations` para evitar `NameError` en referencias hacia adelante en dataclasses frozen con Python 3.12
- `main_v2.py`: `manager.save_profile()` incorrecto reemplazado por `manager.save_active()`; lambda override de métodos de instancia reemplazado por subclase `_PersistentNavigator`; firma de `eventFilter` corregida para mypy strict
- `LiveTvScreen`: propagación de Esc corregida mediante event filter en `_search` (el widget padre no recibe eventos de teclado cuando el hijo `QLineEdit` tiene foco)
- 9 errores mypy strict en `main_v2.py`, `home_screen.py` y `live_tv_screen.py` resueltos

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
