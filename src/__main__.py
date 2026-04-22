from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping

from configlib import load_config
from patch_bay import LoggingPatchBayListener, PatchBay
from patch_bay.peer import parse_host_port
from patch_jack import Jack, LoggingJackListener
from rich import print as rprint
from rich.logging import RichHandler

CONFIG_PATH = "config.yaml"


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_time=True,
                show_path=True,
                markup=False,
            )
        ],
        force=True,
    )
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)


def _local_bind_address(address: str) -> bool:
    s = address.strip().lower()
    return s.startswith("127.0.0.1:") or s.startswith("localhost:") or s.startswith("[::1]:")


def _register_bypass(jack: Jack, label: str) -> None:
    @jack
    async def _handler(payload: dict) -> None:
        rprint(f"[bold cyan]bypass[/bold cyan] {label}", payload)
        await jack.send(payload)


async def main() -> None:
    _configure_logging()

    raw = load_config(CONFIG_PATH)
    config: Mapping[str, object] = raw if isinstance(raw, Mapping) else dict(raw)

    jacks: list[Jack] = []
    try:
        for entry in config.get("jacks", ()):
            if not isinstance(entry, Mapping):
                continue
            addr = str(entry.get("address", "")).strip()
            if not addr or not _local_bind_address(addr):
                continue
            name = str(entry.get("name", addr)).strip() or addr
            host, port = parse_host_port(addr)
            j = Jack(port, host=host, listeners=[LoggingJackListener()])
            _register_bypass(j, name)
            jacks.append(j)

        for j in jacks:
            await j.start()

        pb = PatchBay(dict(config), listeners=[LoggingPatchBayListener()])
        await pb.run()
    finally:
        for j in reversed(jacks):
            await j.aclose()


if __name__ == "__main__":
    asyncio.run(main())
