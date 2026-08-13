from textual.app import  ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Static,
)

import libs as libs

class ConfirmScreen(ModalScreen[bool]):
    """Modal que muestra el resumen de la transacción antes de ejecutarla."""

    CSS = libs.CSS

    def __init__(self, title: str, preview: str) -> None:
        super().__init__()
        self._title = title
        self._preview = preview

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(self._title, id="title")
            yield Static(self._preview, id="preview")
            with Vertical(id="buttons"):
                yield Button(libs.BTN_CONFIRM_TEXT, id=libs.BTN_CONFIRM_ID, variant="success")
                yield Button(libs.BTN_CANCEL_TEXT, id=libs.BTN_CANCEL_ID, variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == libs.BTN_CONFIRM_ID)

    def on_key(self, event) -> None:
        if event.key == libs.Y_CONST:
            self.dismiss(True)
        elif event.key in ("n", "escape"):
            self.dismiss(False)
