"""Mock price optimizer.

Phase 1 compares simple totals and exposes restrictions. It deliberately does
not perform payment or call coupon APIs.
"""
from __future__ import annotations

from typing import Any


def _step_price(step: dict[str, Any]) -> int:
    for key in ("price", "cost"):
        value = step.get(key)
        if value not in (None, ""):
            try:
                return int(value or 0)
            except Exception:
                pass
    candidates = step.get("merchant_candidates") or []
    if candidates:
        try:
            return int(candidates[0].get("price", 0) or 0)
        except Exception:
            return 0
    return 0


def _billable_steps(plan: dict[str, Any]) -> list[dict[str, Any]]:
    steps = [s for s in plan.get("steps", []) if s.get("kind") in {"activity", "restaurant", "stayin", "delivery", "addon"}]
    if steps:
        return steps
    itinerary = plan.get("itinerary") or {}
    out = []
    for seg in itinerary.get("segments", []) or []:
        if not seg.get("is_core", True):
            continue
        selected = {}
        candidates = seg.get("merchant_candidates") or []
        if candidates:
            selected = dict(candidates[0])
        out.append({**selected, **seg})
    return out


def optimize_price(plan: dict[str, Any] | None, request: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan or {}
    request = request or {}
    steps = _billable_steps(plan)
    original = sum(_step_price(s) for s in steps)
    deal_saving = sum(12 for s in steps if s.get("group_deal"))
    separate_best = max(0, original - deal_saving)
    bundle = max(0, original - (18 if len(steps) >= 2 else 0))
    member = max(0, separate_best - 10) if request.get("member_enabled") else separate_best + 999

    candidates = {
        "separate": separate_best,
        "bundle": bundle,
        "member": member,
        "pay_at_store": original,
    }
    recommended = min(candidates, key=candidates.get)
    warnings: list[str] = []
    if separate_best < bundle:
        warnings.append(f"建议分开买，比一键买单省 ¥{bundle - separate_best}。")

    return {
        "original_total": original,
        "separate_best_total": separate_best,
        "bundle_total": bundle,
        "member_total": member if request.get("member_enabled") else separate_best,
        "recommended_payment": recommended,
        "saving_amount": original - candidates[recommended],
        "coupon_notes": ["Mock：优先计算团购券和会员券，不调用真实支付。"],
        "restrictions": [
            {"name": "周末可用", "usable": True},
            {"name": "是否可退", "usable": True},
            {"name": "是否需预约", "usable": any(s.get("can_reserve") for s in steps)},
            {"name": "不可与其它优惠同享", "usable": False},
        ],
        "warnings": warnings,
    }
