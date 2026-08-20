from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Static,
)
from dataclasses import fields
import libs as libs

class ShowDataScreen(ModalScreen[None]):
    """Modal de solo lectura con la info enviada'."""

    CSS = """
    ShowDataScreen {
        align: center middle;
    }
    #show-data-dialog {
        width: 90%;
        height: 85%;
        border: thick $accent;
        background: $panel;
        padding: 1 2;
    }
    #show-data-scroll {
        height: 1fr;
        overflow-y: auto;
    }
    #show-data-buttons {
        height: 3;
        align: center middle;
    }
    """

    def __init__(self, content: str, title: str) -> None:
        super().__init__()
        self._content = content
        self.title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="show-data-dialog"):
            yield Static(self.title, id="show-data-title")
            with VerticalScroll(id="show-data-scroll"):
                yield Static(self._content, id="show-data-content")
            with Vertical(id="show-data-buttons"):
                yield Button("Cerrar (esc)", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)