from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

import yaml


class AgentConfig(BaseModel):
    url: str = "http://localhost:8000"


class BotConfig(BaseModel):
    server_url: str

class AppConfig(BaseModel):
    agent: AgentConfig = Field(default_factory=AgentConfig)
    bots: list[BotConfig] = Field(default_factory=list)
    log: str | None = None

    @classmethod
    def load(cls, path: str) -> AppConfig:
        if not Path(path).exists():
            raise FileNotFoundError(f"配置文件 {path} 不存在")
        with open(path, "r", encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))
