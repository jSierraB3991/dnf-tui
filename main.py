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
from textual.coordinate import Coordinate
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
from plyer import notification


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
                yield Input(placeholder="/ buscar...", id="vim-search-input")
                yield DataTable(id="installed-table")
                yield Button("↑ Ir arriba", id="scroll-top-btn")
            with TabPane(libs.TAB_UPDATE_TEXT, id="upgrades"):
                yield DataTable(id="upgrades-table")
        yield Footer()

    def on_mount(self) -> None:
        self._search_matches: list[int] = []
        self._search_index: int = -1
        self.query_one("#vim-search-input", Input).display = False
        for table_id in ("search-table", "installed-table", "upgrades-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns(*libs.COLUMNS)
            table.cursor_type = "row"
        self.action_refresh()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "scroll-top-btn":
            table = self.query_one("#installed-table", DataTable)
            table.cursor_coordinate = (0, 0)
            table.scroll_home(animate=False)


    async def on_key(self, event) -> None:
        search_input = self.query_one("#vim-search-input", Input)
        if event.key == "escape" and search_input.has_focus:
            search_input.display = False
            self.query_one("#installed-table", DataTable).focus()

    def action_start_search(self) -> None:
        if self.query_one(TabbedContent).active != "installed":
            return
        search_input = self.query_one("#vim-search-input", Input)
        search_input.display = True
        search_input.value = ""
        search_input.focus()

    
    def _run_vim_search(self, query: str) -> None:
        query = query.strip().lower()
        table = self.query_one("#installed-table", DataTable)
        if not query:
            self._search_matches = []
            return
        matches = [
            row for row in range(table.row_count)
            if query in str(table.get_cell_at(Coordinate(row, 0))).lower()
        ]
        self._search_matches = matches
        self._search_index = -1
        if matches:
            self._jump_to_match(table, step=1)
        else:
            self.notify(f"Sin coincidencias para '{query}'", severity="warning")
 
    def _jump_to_match(self, table: DataTable, step: int) -> None:
        if not self._search_matches:
            self.notify("No hay búsqueda activa", severity="warning")
            return
        self._search_index = (self._search_index + step) % len(self._search_matches)
        row = self._search_matches[self._search_index]
        table.cursor_coordinate = Coordinate(row, 0)
 
    def action_next_match(self) -> None:
        if self.query_one(TabbedContent).active != "installed":
            return
        self._jump_to_match(self.query_one("#installed-table", DataTable), step=1)
 
    def action_prev_match(self) -> None:
        if self.query_one(TabbedContent).active != "installed":
            return
        self._jump_to_match(self.query_one("#installed-table", DataTable), step=-1)

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
        if self.is_first_update:
            self.is_first_update = False
            self.send_system_notify(
                "Los paquetes a actualización sin caché a finalizado",
                "Actualización de paquetes"
            )
        self._set_tabs_disabled(False)
    
    def send_system_notify(self, message: str, title: str) -> None:
        notification.notify(
            title=title,
            message=message,
            app_name="LazyDNF",
            timeout=5
        )

    async def on_tabbed_content_tab_activated(self, event) -> None:
        self.action_refresh()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)
        if event.input.id == "search-input":
            packages = await dnf.search(event.value)
            fill_table(self.query_one("#search-table", DataTable), packages)
            table.loading = False
            self._set_tabs_disabled(False)
            return
        if event.input.id == "vim-search-input":
            self._run_vim_search(event.value)
            event.input.display = False
            self.query_one("#installed-table", DataTable).focus()
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
        if not row_key.value:
            return None
        name, _, _version = str(row_key.value).partition("@")
        return name

    async def _do_transaction(self, action: str, package: str) -> None:
        table, _ = self._current_table_and_action()
        table.loading = True
        self._set_tabs_disabled(True)

        code, preview = await dnf.transaction_preview(action, package)
        if code == 0:
            self.notify(f"{package}: {preview}", severity="information")
            table.loading = False
            self._set_tabs_disabled(False)
            return
        title = f"{action.upper()} · {package}"
        confirmed = await self.push_screen_wait(confirm_screen.ConfirmScreen(title, preview))
        if not confirmed:
            self.notify("Cancelado", severity="warning")
            table.loading = False
            self._set_tabs_disabled(False)
            return
        code, output = await dnf.run_transaction(action, package)
        if code == 0:
            self.notify(f"{action} de {package} completado", severity="information")
        else:
            self.notify(f"Falló {action} de {package}: {output[-200:]}", severity="error")
        self.action_refresh()
        table.loading = False
        self._set_tabs_disabled(False)

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
    
    def action_upgrade_all(self) -> None:
        self.run_worker(self._do_transaction("upgrade", ""), exclusive=True)


if __name__ == "__main__":
    DnfTUI().run()
