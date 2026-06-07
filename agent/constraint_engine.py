"""Constraint engine skeleton.

Hard constraints are applied before rating/ad/coupon sorting. Phase 1 exposes
the structure and basic extraction; existing catalog/planner can consume the
same request safety flags without changing external APIs.
"""
from __future__ import annotations

from typing import Any


def build_constraints(request: dict[str, Any], intent_frame: dict[str, Any] | None = None) -> dict[str, Any]:
    frame = intent_frame or request.get("intent_frame") or {}
    safety = set(request.get("safety_flags") or [])
    safety.update(frame.get("safety_flags") or [])
    negative = set(request.get("negative_intents") or [])
    negative.update(frame.get("negative_intents") or [])
    diet = set(request.get("diet_limits") or [])
    diet.update((frame.get("confirmed_fields") or {}).get("diet_limits") or [])

    hard: list[dict[str, Any]] = []
    safety_constraints: list[dict[str, Any]] = []
    blocked_categories: set[str] = set()
    required_capabilities: set[str] = set()
    notes: list[str] = []

    if "cannot_ice" in safety:
        hard.append({"type": "drink_temperature", "value": "no_ice"})
        required_capabilities.add("hot_available")
    if "not_too_sweet" in safety:
        hard.append({"type": "drink_sugar", "value": "low_or_zero"})
    if "body_uncomfortable" in safety:
        safety_constraints.append({"type": "body_uncomfortable", "prefer": ["hot_drink", "light_food"]})
        required_capabilities.add("body_uncomfortable")
    if "kid_safe" in safety:
        safety_constraints.append({"type": "kid_safe"})
        blocked_categories.update({"酒吧", "成人向", "恐怖密室"})
    if "no_alcohol" in safety or "no_alcohol" in diet or "no_alcohol" in negative:
        hard.append({"type": "no_alcohol"})
        blocked_categories.update({"酒吧"})
    if "no_spicy" in safety or "no_spicy" in diet:
        hard.append({"type": "no_spicy"})
        required_capabilities.update({"no_spicy", "番茄锅", "鸳鸯锅"})
    if "caffeine_free" in safety or "caffeine_free" in negative:
        hard.append({"type": "caffeine_free"})
        required_capabilities.add("caffeine_free")
    if "no_meal" in negative:
        blocked_categories.update({"餐厅", "火锅", "海鲜", "江浙菜", "烧烤", "简餐"})
    if "no_outdoor" in negative:
        notes.append("用户表达了不想出门，除非后续明确选择线下活动，否则不安排线下商户。")

    return {
        "hard_constraints": hard,
        "soft_preferences": request.get("preferences") or [],
        "safety_constraints": safety_constraints,
        "group_constraints": [],
        "blocked_categories": sorted(blocked_categories),
        "required_capabilities": sorted(required_capabilities),
        "notes": notes,
    }


def violates_constraints(merchant: dict[str, Any], constraints: dict[str, Any]) -> bool:
    category = merchant.get("category")
    if category in set(constraints.get("blocked_categories") or []):
        return True
    flags = set(merchant.get("flags") or [])
    diet_support = set(merchant.get("diet_support") or [])
    body = merchant.get("body_suitability") or {}
    drink = merchant.get("drink_options") or {}
    for item in constraints.get("hard_constraints") or []:
        t = item.get("type")
        if t == "no_alcohol" and ("alcohol" in flags or category == "酒吧"):
            return True
        if t == "no_spicy" and category == "火锅" and not (diet_support & {"no_spicy", "不辣", "番茄锅", "鸳鸯锅", "清汤锅"}):
            return True
        if t == "drink_temperature" and category in {"奶茶", "咖啡"} and not (drink.get("hot_available") or body.get("cannot_ice")):
            return True
        if t == "drink_sugar" and category in {"奶茶", "咖啡"} and not (body.get("not_too_sweet") or "少糖" in drink.get("sugar_levels", [])):
            return True
        if t == "caffeine_free" and category in {"奶茶", "咖啡"} and drink.get("caffeine") not in {"none", "free", "caffeine_free"}:
            return True
    return False
