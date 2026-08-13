"""Wrapper asíncrono sobre dnf / dnf repoquery."""

import asyncio
from dataclasses import dataclass
import libs as libs


@dataclass
class Package:
    name: str
    version: str
    repo: str
    summary: str = ""


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
 


async def search(query: str) -> list[Package]:
    if not query.strip():
        return []
    _, out, _ = await _run("dnf", "repoquery", "-q", "--qf", libs.QF, query)
    return _parse_repoquery(out)


async def list_installed() -> list[Package]:
    _, out, _ = await _run("dnf", "repoquery", "-q", "--installed", "--qf", libs.QF)
    return _parse_repoquery(out)


async def list_upgrades() -> list[Package]:
    _, out, _ = await _run("dnf", "repoquery", "-q", "--upgrades", "--qf", libs.QF)
    return _parse_repoquery(out)


async def transaction_preview(action: str, package: str) -> str:
    """action: 'install' | 'remove' | 'upgrade'. Devuelve el resumen de la transacción."""
    _, out, err = await _run("dnf", action, "-y", "--assumeno", package)
    return out or err


async def run_transaction(action: str, package: str) -> tuple[int, str]:
    """Ejecuta de verdad la transacción (requiere permisos de root)."""
    code, out, err = await _run("sudo", "dnf", action, "-y", package)
    return code, out + err
