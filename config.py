from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel

import yaml

class Bridge(BaseModel):
    hub_url: str = "http://localhost:8000"
    bot_url: str = "http://localhost:8080"


class Config(BaseModel):
    bridges: list[Bridge]
    log_dir: str | None = None

    @classmethod
    def load(cls, path: str) -> Config:
        if not Path(path).exists():
            raise FileNotFoundError(f"配置文件 {path} 不存在")
        with open(path, "r", encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))
