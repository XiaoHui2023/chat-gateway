from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field

import yaml


@dataclass
class AgentConfig:
    url: str = "http://localhost:8000"


@dataclass
class BotConfig:
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass
class AppConfig:
    agent: AgentConfig = field(default_factory=AgentConfig)
    bots: list[BotConfig] = field(default_factory=list)

    @staticmethod
    def load(path: str = "config.yaml") -> AppConfig:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        agent = AgentConfig(**raw.get("agent", {}))
        bots = [BotConfig(**b) for b in raw.get("bots", [])]
        return AppConfig(agent=agent, bots=bots)
