"""LongCat LLM adapter.

Only parser.py and tools.py::compose_share_card should call ask_llm.
When LONGCAT_API_KEY is absent, invalid, or the SDK/network fails, this module
returns None so the deterministic local parser/template fallback continues.
"""
from __future__ import annotations

import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional SDK boundary
    OpenAI = None


def ask_llm(prompt: str, system: str = "", timeout: int = 8) -> str | None:
    """Call LongCat through the OpenAI-compatible SDK; never raise."""
    if OpenAI is None:
        return None
    api_key = getattr(config, "LONGCAT_API_KEY", "") or ""
    if not api_key or "YOUR_APP_KEY" in api_key:
        return None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=getattr(config, "LONGCAT_BASE_URL", ""),
            timeout=timeout,
        )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=getattr(config, "LONGCAT_MODEL", "LongCat-2.0-Preview"),
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return resp.choices[0].message.content
    except Exception:
        return None


if __name__ == "__main__":
    print("=== LongCat smoke test ===")
    print(f"LONGCAT_API_KEY configured: {'YES' if bool(getattr(config, 'LONGCAT_API_KEY', '')) else 'NO'}")
    result = ask_llm("用一句话介绍南京。")
    if result:
        print(f"OK: {result.strip()}")
    else:
        print("Fallback: LongCat unavailable; deterministic local rules remain active.")
