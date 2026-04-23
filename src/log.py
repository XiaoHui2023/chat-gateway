from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(
    *,
    log_dir: str,
    level: str | int = logging.INFO,
) -> None:
    """用 Rich 打到控制台，并在 log_dir 下按启动时间写入一份文本日志。"""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    dir_path = Path(log_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(dir_path / f"{stamp}.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_path=True,
        markup=False,
    )
    console.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(level=level, handlers=[console, file_handler], force=True)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
