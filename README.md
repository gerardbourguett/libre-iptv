# IPTV Player

Reproductor de IPTV de escritorio gratuito y de código abierto para Windows. Permite cargar listas de reproducción M3U desde archivos locales o URLs remotas y reproducir canales de streaming con VLC embebido.

## Características

### Reproducción
- Carga de listas M3U (`.m3u` / `.m3u8`) desde archivo local o URL remota
- Reproducción con VLC embebido directamente en la ventana principal
- Modos de visualización: pantalla única, doble o cuádruple (teclas `1`, `2`, `4`)
- Modo pantalla completa de video (solo el área de reproducción, tecla `F11`)
- Controles: volumen (0–100), silencio (`M`) y detención (`Espacio`)

### Lista de canales
- Agrupación automática por `group-title` con categorías colapsables
- Canales sin grupo agrupados bajo "Uncategorized"
- Secciones fijas de **Favoritos** (⭐) y **Recientes** (🕐) en la parte superior
- Búsqueda en tiempo real insensible a mayúsculas; los grupos vacíos se ocultan
- Menú contextual (clic derecho) para agregar o quitar de favoritos

### Perfiles
- Pantalla de selección de perfil al iniciar la aplicación
- Creación de múltiples perfiles con nombre y color de avatar
- Cada perfil guarda de forma independiente: lista M3U, favoritos y canales recientes
- Cambio de perfil desde la barra superior sin reiniciar
- Opciones de perfil: renombrar, cambiar color y eliminar

### Parser M3U
- Soporte de directivas intermedias (`#EXTGRP`, `#KODIPROP`, `#EXTVLCOPT`) entre `#EXTINF` y la URL
- Compatibilidad con archivos en codificación UTF-8 y latin-1 / cp1252
- Auto-mejora de URL `/m3u` a `/m3u_plus` cuando los canales no tienen grupo

## Requisitos

| Requisito | Versión mínima |
|-----------|----------------|
| Python | 3.12 |
| VLC Media Player | 3.x |
| Sistema operativo | Windows 10 / 11 |

VLC debe estar instalado en el sistema antes de ejecutar la aplicación. Descarga disponible en [videolan.org](https://www.videolan.org/).

## Instalación

```bash
# 1. Clonar el repositorio
git clone <URL del repositorio>
cd iptv

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -e .
```

## Uso

```bash
# Con el entorno virtual activado
python main.py
```

Al iniciar, aparece la pantalla de selección de perfil. Si es la primera vez, se solicita crear uno.

### Cargar una lista de canales

1. Ir a **File > Open Playlist** para cargar un archivo M3U local
2. O ir a **File > Open URL...** para cargar desde una URL remota
3. Hacer clic en un canal de la lista para iniciar la reproducción

La lista se guarda en el perfil activo y se carga automáticamente en la próxima sesión.

### Atajos de teclado

| Tecla | Acción |
|-------|--------|
| `F11` | Activar / desactivar pantalla completa de video |
| `Esc` | Salir de pantalla completa |
| `1` | Modo de vista única |
| `2` | Modo de vista doble |
| `4` | Modo de vista cuádruple |
| `M` | Silenciar / activar sonido |
| `Espacio` | Detener reproducción |

### Favoritos y recientes

- **Clic derecho** sobre cualquier canal → "Agregar a Favoritos" / "Quitar de Favoritos"
- Los últimos 20 canales reproducidos aparecen automáticamente en la sección Recientes

## Desarrollo

### Configuración del entorno

```bash
pip install -e ".[dev]"
```

### Ejecutar pruebas

```bash
pytest
```

### Verificar calidad de código

```bash
ruff check src tests   # linting
mypy src               # verificación de tipos
```

## Estructura del proyecto

```
iptv/
├── main.py                    # Punto de entrada
├── pyproject.toml             # Configuración del proyecto y dependencias
├── src/
│   ├── models/
│   │   ├── channel.py         # Modelo de datos Channel
│   │   └── profile.py         # Modelo de datos Profile y colores de avatar
│   ├── parser/
│   │   └── m3u.py             # Parser M3U con soporte de codificación y directivas intermedias
│   ├── profiles/
│   │   └── manager.py         # Gestión de perfiles con persistencia JSON
│   └── ui/
│       ├── app_settings.py    # Persistencia de geometría y splitter (QSettings)
│       ├── channel_list.py    # Lista de canales: grupos, favoritos, recientes, búsqueda
│       ├── control_bar.py     # Barra de controles de reproducción
│       ├── grid_player_widget.py # Grilla de reproductores (1/2/4 pantallas)
│       ├── main_window.py     # Ventana principal, menús y atajos de teclado
│       ├── player_widget.py   # Reproductor VLC embebido individual
│       ├── profile_bar.py     # Barra de perfiles y diálogos de gestión
│       ├── profile_chooser.py # Pantalla de selección de perfil al inicio
│       └── welcome_dialog.py  # Diálogo de bienvenida (primer uso)
└── tests/                     # Suite de pruebas (pytest + pytest-qt)
    ├── models/
    ├── parser/
    ├── profiles/
    └── ui/
```

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| [Python 3.12+](https://python.org) | Lenguaje principal |
| [PyQt6](https://riverbankcomputing.com/software/pyqt/) | Interfaz gráfica |
| [python-vlc](https://pypi.org/project/python-vlc/) | Integración con VLC |
| [pytest](https://pytest.org) + [pytest-qt](https://pytest-qt.readthedocs.io) | Pruebas |
| [ruff](https://docs.astral.sh/ruff/) | Linting y formateo |
| [mypy](https://mypy-lang.org) | Verificación de tipos estática |

## Licencia

MIT — ver archivo [LICENSE](LICENSE) para más detalles.
