"""dnfola — TUI estilo nala, pero para dnf.

Uso:
    python app.py

Requiere: pip install textual
Las acciones de instalar/eliminar/actualizar corren `sudo dnf`, así que
la primera vez que ejecutes una transacción te pedirá la contraseña
en la terminal donde lanzaste la app.
"""

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    TabbedContent,
    TabPane,
)

import dnf_backend as dnf
import libs as libs
import confirm_screen as confirm_screen

def fill_table(table: DataTable, packages: list[dnf.Package]) -> None:
    table.clear()
    for pkg in packages:
        table.add_row(pkg.name, pkg.version, pkg.repo, pkg.summary, key=f"{pkg.name}@{pkg.version}")

class DnfTUI(App):
    TITLE = libs.TITLE
    BINDINGS = libs.BINDINGS
    is_first_update = True

    def _set_tabs_disabled(self, disabled: bool) -> None:
        tabbed = self.query_one(TabbedContent)
        for tab_id in ("search", "installed", "upgrades"):
            tabbed.get_tab(tab_id).disabled = disabled

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="search"):
            with TabPane(libs.TAB_SEARCH_TEXT, id="search"):
                yield Input(placeholder=libs.INPUT_SEARCH_PLACE_HOLDER, id="search-input")
                yield DataTable(id="search-table")
            with TabPane(libs.TAB_INSTALLED_TEXT, id="installed"):
                yield DataTable(id="installed-table")
            with TabPane(libs.TAB_UPDATE_TEXT, id="upgrades"):
                yield DataTable(id="upgrades-table")
        yield Footer()

    def on_mount(self) -> None:
        for table_id in ("search-table", "installed-table", "upgrades-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns(*libs.COLUMNS)
            table.cursor_type = "row"
        self.action_refresh()

    def action_refresh(self) -> None:
        active = self.query_one(TabbedContent).active
        if active == "installed":
            self.run_worker(self._load_installed(), exclusive=True)
        elif active == "upgrades":
            self.run_worker(self._load_upgrades(), exclusive=True)

    async def _load_installed(self) -> None:
        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)
        table = self.query_one("#installed-table", DataTable)
        table.clear()
        packages = await dnf.list_installed()
        fill_table(self.query_one("#installed-table", DataTable), packages)
        table.loading = False
        self._set_tabs_disabled(False)

    async def _load_upgrades(self) -> None:
        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)
        packages = await dnf.list_upgrades(self.is_first_update)
        fill_table(self.query_one("#upgrades-table", DataTable), packages)
        table.loading = False
        self.is_first_update = False
        self._set_tabs_disabled(False)

    async def on_tabbed_content_tab_activated(self, event) -> None:
        self.action_refresh()

    async def on_input_submitted(self, event: Input.Submitted) -> None:

        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)

        if event.input.id != "search-input":
            return
        packages = await dnf.search(event.value)
        fill_table(self.query_one("#search-table", DataTable), packages)

        table.loading = False
        self._set_tabs_disabled(False)

    def _current_table_and_action(self) -> tuple[DataTable, str] | None:
        active = self.query_one(TabbedContent).active
        mapping = {
            "search": ("search-table", "install"),
            "installed": ("installed-table", "remove"),
            "upgrades": ("upgrades-table", "upgrade"),
        }
        if active not in mapping:
            return None
        table_id, action = mapping[active]
        return self.query_one(f"#{table_id}", DataTable), action

    def _selected_package_name(self, table: DataTable) -> str | None:
        if table.cursor_row is None:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(row_key.value) if row_key.value else None

    async def _do_transaction(self, action: str, package: str) -> None:
        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)

        preview = await dnf.transaction_preview(action, package)
        title = f"{action.upper()} · {package}"
        confirmed = await self.push_screen_wait(confirm_screen.ConfirmScreen(title, preview))
        if not confirmed:
            self.notify("Cancelado", severity="warning")
            return
        code, output = await dnf.run_transaction(action, package)
        if code == 0:
            self.notify(f"{action} de {package} completado", severity="information")
        else:
            self.notify(f"Falló {action} de {package}: {output[-200:]}", severity="error")
        self.action_refresh()

        table.loading = False
        self._set_tabs_disabled(True)

    def action_install_selected(self) -> None:
        info = self._current_table_and_action()
        if not info:
            return
        table, _ = info
        name = self._selected_package_name(table)
        if name:
            self.run_worker(self._do_transaction("install", name), exclusive=True)

    def action_remove_selected(self) -> None:
        info = self._current_table_and_action()
        if not info:
            return
        table, _ = info
        name = self._selected_package_name(table)
        if name:
            self.run_worker(self._do_transaction("remove", name), exclusive=True)

    def action_upgrade_selected(self) -> None:
        info = self._current_table_and_action()
        if not info:
            return
        table, _ = info
        name = self._selected_package_name(table)
        if name:
            self.run_worker(self._do_transaction("upgrade", name), exclusive=True)

    async def _load_installed(self) -> None:
        table = self.query_one("#installed-table", DataTable)
        table.loading = True
        self._set_tabs_disabled(True)
        try:
            packages = await dnf.list_installed()
            fill_table(table, packages)
        finally:
            table.loading = False
            self._set_tabs_disabled(False)

if __name__ == "__main__":
    DnfTUI().run()
