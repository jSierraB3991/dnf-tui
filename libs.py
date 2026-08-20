PACKAGE =  "Paquete"
VERSION = "Versión"
REPO = "Repo"
RESUMEN = "Resumen"
ID = "Id"
COMMAND = "Comando"
START_TIME = "Hora de inicio"
END_TIME = "Hora final"
STATUS = "Estado"
RELEASE_VER = "Versión en la que se realizo"
ALTERED_COUNT = "Paquetes cambiados"

TITLE = "dnf-tui"
FIELD_SEP = "\x1f"

BTN_CONFIRM_TEXT = "Confirmar (y)"
BTN_CANCEL_TEXT = "Cancelar (n)"
TAB_SEARCH_TEXT = "Buscar"
TAB_INSTALLED_TEXT = "Instalados"
TAB_UPDATE_TEXT = "Actualizaciones"
TAB_HISTORY_TEXT = "Historial"
INPUT_SEARCH_PLACE_HOLDER = "Buscar paquete y Enter..."

BTN_CONFIRM_ID = "confirm"
BTN_CANCEL_ID = "cancel"

Y_CONST = "y"

COLUMNS_PACKAGES = (PACKAGE, VERSION, REPO, RESUMEN)
COLUMNS_HISTORY = (ID, STATUS, RELEASE_VER, ALTERED_COUNT, COMMAND)

BINDINGS = [
    ("i", "install_selected", "Instalar"),
    ("I", "info_history_selected", "Info del historial/Paquete"),
    ("r", "remove_selected", "Eliminar"),
    ("u", "upgrade_selected", "Actualizar"),
    ("U", "upgrade_all", "Actualizar TODO"),
    ("f5", "refresh", "Refrescar"),
    ("/", "start_search", "Buscar"),
    ("f4", "next_match", "Sig. coincidencia"),
    ("f3", "prev_match", "Coincidencia anterior"),
    ("q", "quit", "Salir"),
]

CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #dialog {
        width: 80%;
        height: 70%;
        border: thick $accent;
        background: $panel;
        padding: 1 2;
    }
    #preview {
        height: 1fr;
        overflow-y: auto;
    }
    #buttons {
        height: 3;
        align: center middle;
    }
    """

QF = f"%{{name}}{FIELD_SEP}%{{evr}}{FIELD_SEP}%{{reponame}}{FIELD_SEP}%{{summary}}\n"
