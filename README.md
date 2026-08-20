# dnf-tui

Una TUI para `dnf` — buscar, instalar, eliminar y actualizar paquetes en Fedora sin salir de la terminal.

```
+-----------------------------------------------------------------------------------------+
| dnf-tui                                                          λ lelouch              |
|-----------------------------------------------------------------------------------------|
| Buscar   | Instalados |  Historial | Actualizaciones                                    |
|-----------------------------------------------------------------------------------------|
| / quick                                                                                 |
|-----------------------------------------------------------------------------------------|
| Paquete        | Versión         | Repo          | Resumen                              |
|----------------+-----------------+---------------+--------------------------------------|
| quickshell     | 0.2.1-3.fc44    | updates       | QtQuick desktop shell                |
| brave-browser  | 1.93.136-1      | brave-browser | Web browser                          |
| flatpak        | 1.18.1-1.fc44   | updates       | App sandboxing                       |
| warp-terminal  | v2026.08.12-1   | warpdotdev    | Terminal app                         |
+-----------------------------------------------------------------------------------------+
| i instalar  I historial  r eliminar  u actualizar  U actualizar todo  / buscar  q salir |
+-----------------------------------------------------------------------------------------+
```

## Instalación

```bash
git clone https://github.com/jsierrab3991/dnf-tui.git
cd dnf-tui
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
python app.py
```

Las transacciones (`instalar`, `eliminar`, `actualizar`) corren `sudo dnf`, así que la primera vez que dispares una te va a pedir la contraseña en la terminal donde lanzaste la app.

## Atajos

| Tecla | Acción                             |
| ----- | ---------------------------------- |
| `i`   | Instalar el paquete seleccionado   |
| `I`   | Info del historial / paquete       |
| `r`   | Eliminar el paquete seleccionado   |
| `u`   | Actualizar el paquete seleccionado |
| `U`   | Actualizar todo el sistema         |
| `F5`  | Refrescar la pestaña actual        |
| `/`   | Buscar (filtro en Instalados)      |
| `F4`  | Siguiente coincidencia             |
| `F3`  | Coincidencia anterior              |
| `q`   | Salir                              |

## Pestañas

- **Buscar** — busca paquetes disponibles en los repos.
- **Instalados** — lista los paquetes instalados, con filtro por nombre.
- **Actualizaciones** — paquetes con una versión más nueva disponible.
- **Historial** — transacciones pasadas de `dnf history`.

## Requisitos

- Fedora con `dnf`
- Python 3.11+
- [textual](https://github.com/Textualize/textual)
- [plyer](https://github.com/kivy/plyer)

## Licencia

GPL v3 — ver [LICENSE](LICENSE).
