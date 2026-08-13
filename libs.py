PACKAGE =  "Paquete"
VERSION = "Versión"
REPO = "Repo"
RESUMEN = "Resumen"
TITLE = "lazydnf"
FIELD_SEP = "\x1f"

BTN_CONFIRM_TEXT = "Confirmar (y)"
BTN_CANCEL_TEXT = "Cancelar (n)"
TAB_SEARCH_TEXT = "Buscar"
TAB_INSTALLED_TEXT = "Instalados"
TAB_UPDATE_TEXT = "Actualizaciones"
INPUT_SEARCH_PLACE_HOLDER = "Buscar paquete y Enter..."

BTN_CONFIRM_ID = "confirm"
BTN_CANCEL_ID = "cancel"

Y_CONST = "y"

COLUMNS = (PACKAGE, VERSION, REPO, RESUMEN)

BINDINGS = [
    ("i", "install_selected", "Instalar"),
    ("r", "remove_selected", "Eliminar"),
    ("u", "upgrade_selected", "Actualizar"),
    ("f5", "refresh", "Refrescar"),
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