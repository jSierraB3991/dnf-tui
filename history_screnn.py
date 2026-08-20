import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Static,
)
from dataclasses import fields
import libs as libs


@dataclass
class HistoryPackage:
    nevra: str
    action: str
    reason: str
    repository: str

def _filtered(cls, data: dict) -> dict:
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


@dataclass
class HistoryPackage:
    nevra: str
    action: str
    reason: str
    repository: str


@dataclass
class HistoryTransaction:
    id: int
    start_time: int
    end_time: int
    user_name: str
    status: str
    releasever: str
    description: str
    comment: str
    packages: list[HistoryPackage] = field(default_factory=list)

    @classmethod
    def from_json(cls, raw: str) -> "HistoryTransaction":
        data = json.loads(raw)[0]
        packages = [HistoryPackage(**_filtered(HistoryPackage, p)) for p in data.get("packages", [])]
        fields_data = _filtered(cls, data)
        fields_data.pop("packages", None)
        return cls(**fields_data, packages=packages)
    @property
    def duration_seconds(self) -> int:
        return self.end_time - self.start_time

    @property
    def started_at(self) -> str:
        return datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")

class HistoryScreen(ModalScreen[None]):
    """Modal con el historial de 'dnf history info' como tabla, más descarga del JSON crudo."""

    CSS = """
    HistoryScreen {
        align: center middle;
    }
    #history-dialog {
        width: 90%;
        height: 85%;
        border: thick $accent;
        background: $panel;
        padding: 1 2;
    }
    #history-summary {
        height: auto;
    }
    #history-table {
        height: 1fr;
    }
    #history-buttons {
        height: 3;
        align: center middle;
    }
    """

    def __init__(self, content: str) -> None:
        super().__init__()
        self._raw = content
        try:
            self._transaction = HistoryTransaction.from_json(content)
        except (json.JSONDecodeError, KeyError, IndexError):
            self._transaction = None

    def compose(self) -> ComposeResult:
        with Vertical(id="history-dialog"):
            if self._transaction is None:
                yield Static("No se pudo interpretar el historial", id="history-summary")
                yield Static(self._raw, id="history-table")
            else:
                t = self._transaction
                status_style = "bold green" if t.status == "Ok" else "bold red"
                title = (
                    f"[bold]#{t.id}[/bold]  ·  {t.started_at}  ·  "
                    f"[{status_style}]{t.status}[/{status_style}]  ·  "
                    f"{t.duration_seconds}s  ·  {len(t.packages)} paquetes\n"
                    f"[dim]{t.description}[/dim]"
                )
                yield Static(title, id="history-summary")              
                yield DataTable(id="history-table")
            with Vertical(id="history-buttons"):
                yield Button("Guardar JSON", id="download")
                yield Button(libs.BTN_CANCEL_TEXT, id=libs.BTN_CANCEL_ID)

    def on_mount(self) -> None:
        if self._transaction is None:
            return
        table = self.query_one("#history-table", DataTable)
        table.add_columns("Paquete", "Acción", "Razón", "Repo")
        table.cursor_type = "row"
        for pkg in self._transaction.packages:
            table.add_row(pkg.nevra, pkg.action, pkg.reason, pkg.repository)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download":
            self._save_to_disk()
            return
        self.dismiss(None)

    def _save_to_disk(self) -> None:
        transaction_id = self._transaction.id if self._transaction else "raw"
        path = Path.home() / f"dnf-history-{transaction_id}.json"
        path.write_text(self._raw, encoding="utf-8")
        self.notify(f"Guardado en {path}")

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)