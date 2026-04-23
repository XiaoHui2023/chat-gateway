from __future__ import annotations

import argparse
import asyncio
from collections.abc import Mapping

from configlib import load_config
from patch_bay import LoggingPatchBayListener, PatchBay
from log import setup_logging


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Chat gateway: jacks + patch bay.")
    p.add_argument(
        "config",
        nargs="?",
        default="config.yaml",
        help="YAML 配置文件路径（可省略，默认 config.yaml）",
    )
    p.add_argument(
        "--log-dir",
        default="logs",
        help="日志文件目录（默认 logs，目录下按启动时间生成 .log）",
    )
    return p

async def main() -> None:
    args = _build_arg_parser().parse_args()
    setup_logging(log_dir=args.log_dir)

    raw = load_config(args.config)
    config: Mapping[str, object] = raw if isinstance(raw, Mapping) else dict(raw)

    pb = PatchBay(dict(config), listeners=[LoggingPatchBayListener()])
    await pb.run()


if __name__ == "__main__":
    asyncio.run(main())
