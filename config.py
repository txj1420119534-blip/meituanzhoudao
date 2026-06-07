"""Configuration loaded from `.env`; never hard-code API keys."""

import os

from dotenv import load_dotenv


load_dotenv(encoding="utf-8-sig")

# LongCat model API. When the key is absent, the local rule fallback remains active.
LONGCAT_API_KEY = os.getenv("LONGCAT_API_KEY", "")
LONGCAT_BASE_URL = os.getenv("LONGCAT_BASE_URL", "https://api.longcat.chat/openai")
LONGCAT_MODEL = os.getenv("LONGCAT_MODEL", "LongCat-2.0-Preview")

# Product copy.
BRAND_NAME = "美团周到"
BRAND_TAGLINE = "说一句，我帮你把这场局安排到能出门"

# Meituan-like theme colors.
THEME_PRIMARY = "#FFD000"
THEME_INK = "#191919"
THEME_PROMO_RED = "#FF4D27"
