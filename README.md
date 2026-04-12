# IPTV Player

Reproductor de IPTV de escritorio gratuito y de código abierto para Windows. Permite cargar listas de reproducción M3U desde archivos locales o URLs remotas y reproducir canales de streaming con VLC embebido.

## Características

- Carga de listas M3U (`.m3u` / `.m3u8`) desde archivo local o URL remota
- Búsqueda de canales en tiempo real con filtrado por nombre
- Agrupación automática de canales por categoría (`group-title`)
- Reproducción de video con VLC embebido en la ventana principal
- Controles de reproducción: slider de volumen (0–100), botón de silencio con estado visual y botón de detención
- Barra de estado con información del canal en reproducción y mensajes de carga
- Persistencia de configuración: geometría de la ventana, tamaño del panel lateral y última lista cargada

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

### Cargar una lista de canales

1. Ir a **File > Open Playlist** para cargar un archivo M3U local (`.m3u` o `.m3u8`)
2. O ir a **File > Open URL...** para cargar desde una URL remota
3. Hacer clic en un canal de la lista para iniciar la reproducción

La descarga desde URL se realiza en un hilo de fondo para mantener la interfaz responsiva.

### Buscar canales

Escribir en el campo de búsqueda ubicado sobre la lista de canales. El filtrado es instantáneo y no distingue mayúsculas de minúsculas. Los encabezados de grupo se ocultan automáticamente cuando ningún canal del grupo coincide con la búsqueda.

### Controles de reproducción

| Control | Función |
|---------|---------|
| Slider **Vol** | Ajusta el volumen entre 0 y 100 |
| Botón **Mute / Unmute** | Activa o desactiva el silencio |
| Botón **Stop** | Detiene la reproducción actual |
| **Playback > Stop** | Detiene la reproducción desde el menú |

## Desarrollo

### Configuración del entorno de desarrollo

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
├── main.py                  # Punto de entrada
├── pyproject.toml           # Configuración del proyecto y dependencias
├── src/
│   ├── models/
│   │   └── channel.py       # Modelo de datos Channel
│   ├── parser/
│   │   └── m3u.py           # Parser de listas M3U
│   └── ui/
│       ├── app_settings.py  # Persistencia de configuración (QSettings)
│       ├── channel_list.py  # Lista de canales, agrupación y búsqueda
│       ├── control_bar.py   # Controles de reproducción (volumen, silencio, stop)
│       ├── main_window.py   # Ventana principal y menús
│       └── player_widget.py # Reproductor VLC embebido
└── tests/                   # Suite de pruebas (pytest)
    ├── models/
    ├── parser/
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
