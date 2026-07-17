"""
配置模块：集中读取环境变量。

实验 10-1 使用 OpenAI 官方 SDK，所有可调项都通过环境变量注入，
方便切换到兼容 OpenAI 协议的其他厂商（Kimi / Doubao 等）。
"""

import os

try:
    # 允许把配置写在 .env 里（可选依赖）
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv 不是硬性依赖
    pass


class Config:
    """运行时配置。"""

    # 必填：OpenAI API Key（本实验默认用 OPENAI_API_KEY）
    API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    # 可选：兼容 OpenAI 协议的 base_url，默认官方地址
    BASE_URL: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # 可选：模型名，默认用便宜的 gpt-4o-mini 控制演示成本
    MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # 采样温度，稍低一些让行为更稳定可复现
    TEMPERATURE: float = float(os.environ.get("OPENAI_TEMPERATURE", "0.3"))

    @classmethod
    def validate(cls) -> None:
        if not cls.API_KEY:
            raise SystemExit(
                "错误：未检测到 OPENAI_API_KEY 环境变量。\n"
                "请先 `export OPENAI_API_KEY=...` 或复制 env.example 为 .env 并填写。"
            )
