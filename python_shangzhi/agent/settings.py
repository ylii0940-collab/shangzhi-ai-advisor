"""应用配置：所有密钥只从后端环境变量读取。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://shangzhi-ai-advisor.aft15679ty.chatgpt.site",
)
# 项目本地 .env 优先，保证“配置模型.command”写入的 Key 能覆盖旧的终端变量。
load_dotenv(ROOT / ".env", override=True)


@dataclass(slots=True)
class Settings:
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    reasoning_effort: str = "low"
    agent_mode: str = "auto"
    host: str = "127.0.0.1"
    port: int = 8000
    db_path: str = str(ROOT / "data" / "shangzhi.db")
    allowed_origins: tuple[str, ...] = DEFAULT_ALLOWED_ORIGINS

    @classmethod
    def from_env(cls) -> "Settings":
        raw_db_path = os.getenv("SHANGZHI_DB_PATH", "data/shangzhi.db")
        db_path = Path(raw_db_path)
        if not db_path.is_absolute():
            db_path = ROOT / db_path
        mode = os.getenv("SHANGZHI_AGENT_MODE", "auto").strip().lower()
        if mode not in {"auto", "live", "demo"}:
            mode = "auto"
        raw_origins = os.getenv(
            "SHANGZHI_ALLOWED_ORIGINS",
            ",".join(DEFAULT_ALLOWED_ORIGINS),
        )
        allowed_origins = tuple(
            origin.strip().rstrip("/")
            for origin in raw_origins.split(",")
            if origin.strip()
        )
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip(),
            reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "low").strip(),
            agent_mode=mode,
            host=os.getenv("SHANGZHI_HOST", "127.0.0.1").strip(),
            port=int(os.getenv("SHANGZHI_PORT", "8000")),
            db_path=str(db_path),
            allowed_origins=allowed_origins,
        )

    @property
    def live_enabled(self) -> bool:
        if self.agent_mode == "demo":
            return False
        return bool(self.openai_api_key)
