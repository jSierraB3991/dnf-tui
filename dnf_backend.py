"""Wrapper asíncrono sobre dnf / dnf repoquery."""

import asyncio
from dataclasses import dataclass
import libs as libs
import json

@dataclass
class Package:
    name: str
    version: str
    repo: str
    summary: str = ""

@dataclass
class History:
    def __init__(self, id, command_line, start_time, end_time, user_id, status, releasever, altered_count):
        self.id = id
        self.command_line = command_line
        self.start_time = start_time
        self.end_time = end_time
        self.user_id = user_id
        self.status = status
        self.releasever = releasever
        self.altered_count = altered_count


async def _run(*args: str) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")

def _parse_repoquery(output: str) -> list[Package]:
    packages = []
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split(libs.FIELD_SEP, 3)
        if len(parts) < 3:
            continue
        name, version, repo = parts[0], parts[1], parts[2]
        summary = parts[3] if len(parts) > 3 else ""
        packages.append(Package(name=name, version=version, repo=repo, summary=summary))
    return packages

def _parse_history(output: str) -> list[History]:
    data_list = json.loads(output)
    result = [History(**item) for item in data_list]
    return  result
    
 
async def search(query: str) -> list[Package]:
    if not query.strip():
        return []
    _, out, _ = await _run("dnf", "repoquery", "-q", "--qf", libs.QF, f'*{query}*')
    return _parse_repoquery(out)

async def list_installed() -> list[Package]:
    _, out, _ = await _run("dnf", "repoquery", "-q", "--installed", "--qf", libs.QF)
    return _parse_repoquery(out)

async def list_upgrades(is_first_update: bool) -> list[Package]:
    if is_first_update:
        _, out, _ = await _run("dnf", "repoquery", "-q", '--refresh', "--upgrades", "--qf", libs.QF)
        return _parse_repoquery(out)
    else:
        _, out, _ = await _run("dnf", "repoquery", "-q",  "--upgrades", "--qf", libs.QF)
        return _parse_repoquery(out)

async def transaction_preview(action: str, package: str) -> tuple[int, str]:
    """action: 'install' | 'remove' | 'upgrade'. Devuelve el resumen de la transacción."""
    if package == '':
        code, out, err = await _run("dnf", action, "-y", "--assumeno")
    else:
        code, out, err = await _run("dnf", action, "-y", "--assumeno", package)
    return code, out or err

async def run_transaction(action: str, package: str) -> tuple[int, str]:
    """Ejecuta de verdad la transacción (requiere permisos de root)."""
    if package == '':
        code, out, err = await _run("pkexec", "dnf", action, "-y")
    else:
        code, out, err = await _run("pkexec", "dnf", action, "-y", package)
    return code, out + err

async def list_history() -> list[History]:
    _, out, _ = await _run("dnf", "history", "list", "--json")
    return _parse_history(out)

async def list_history_by_version_id(id_version: str) -> str:
    _, out, _ = await _run("dnf", "history", "info", id_version, "--json")
    return out

async def info_by_package(package: str) -> str:
    _, out, _ = await _run("dnf",  "info", package)
    return out