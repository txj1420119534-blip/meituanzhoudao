"""Local Mock checkout engine for Phase 2B Slice 4.

This module never calls real payment, coupon, member, order, map, merchant,
inventory, delivery, account, or customer-service APIs.
"""
from __future__ import annotations

import uuid
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def _money(value: Any) -> float:
    try:
        return float(Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        return 0.0


def _mock_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _step_index(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for step in plan.get("steps") or []:
        mid = step.get("id") or step.get("merchant_id")
        if mid:
            out[mid] = step
    return out


def _price_for(segment: dict[str, Any], step: dict[str, Any] | None = None) -> float:
    step = step or {}
    fields = segment.get("prefilled_fields") or {}
    for value in (step.get("cost"), step.get("price"), fields.get("price"), segment.get("price")):
        if value not in (None, ""):
            return _money(value)
    return 0.0


def _group_deal_price(step: dict[str, Any], fallback: float) -> float:
    deal = step.get("group_deal") or {}
    if isinstance(deal, dict) and deal.get("price") not in (None, ""):
        return _money(deal.get("price"))
    return fallback


def _line_item_from_segment(segment: dict[str, Any], step: dict[str, Any] | None = None) -> dict[str, Any]:
    step = step or {}
    price = _price_for(segment, step)
    group_price = _group_deal_price(step, price)
    return {
        "item_id": segment.get("merchant_id") or segment.get("segment_id") or _mock_id("item"),
        "name": segment.get("merchant_name") or step.get("name") or segment.get("category") or "Mock item",
        "category": segment.get("category") or step.get("category"),
        "role": segment.get("role"),
        "booking_type": segment.get("booking_type"),
        "quantity": 1,
        "unit_price": price,
        "subtotal": price,
        "group_coupon_price": group_price,
        "member_price": max(0.0, group_price - 5.0) if group_price else 0.0,
        "mock_coupon_id": _mock_id("coupon"),
        "booking_ref": (segment.get("mock_booking") or {}).get("order_id"),
        "mock_only": True,
    }


def _line_item_from_addon(addon: dict[str, Any]) -> dict[str, Any]:
    price = _money(addon.get("price") or addon.get("cost"))
    return {
        "item_id": addon.get("id") or addon.get("merchant_id") or _mock_id("addon"),
        "name": addon.get("name") or addon.get("category") or "Accepted add-on",
        "category": addon.get("category"),
        "role": "ADDON",
        "booking_type": "accepted_addon",
        "quantity": 1,
        "unit_price": price,
        "subtotal": price,
        "group_coupon_price": price,
        "member_price": max(0.0, price - 3.0) if price else 0.0,
        "mock_coupon_id": _mock_id("coupon"),
        "booking_ref": None,
        "mock_only": True,
    }


def _round_split(total: float, count: int) -> list[float]:
    count = max(1, int(count or 1))
    base = Decimal(str(total)) / Decimal(count)
    rounded = base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    shares = [rounded for _ in range(count)]
    diff = Decimal(str(total)).quantize(Decimal("0.01")) - sum(shares)
    shares[-1] = (shares[-1] + diff).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return [float(x) for x in shares]


def _strategy(label: str, strategy_id: str, total: float, baseline: float, rules: list[str], reason: str) -> dict[str, Any]:
    return {
        "strategy_id": strategy_id,
        "label": label,
        "total": _money(total),
        "savings": _money(max(0.0, baseline - total)),
        "rules": rules,
        "risk_notes": ["Local Mock only; no real coupon, payment, or member verification."],
        "recommended": False,
        "reason": reason,
    }


def build_checkout_preview(
    plan: dict[str, Any] | None,
    booking_review: dict[str, Any] | None,
    booking_result: dict[str, Any] | None,
    accepted_addons: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    plan = plan or {}
    booking_review = booking_review or {}
    booking_result = booking_result or {}
    accepted_addons = deepcopy(accepted_addons or [])
    steps = _step_index(plan)
    booked = {b.get("merchant_id"): b for b in booking_result.get("bookings") or []}
    billable_items: list[dict[str, Any]] = []
    non_billable_items: list[dict[str, Any]] = []

    for segment in booking_review.get("segments") or []:
        mid = segment.get("merchant_id")
        if not segment.get("bookable"):
            non_billable_items.append({
                "item_id": segment.get("segment_id") or mid or _mock_id("nonbill"),
                "name": segment.get("merchant_name") or segment.get("category"),
                "reason": "not bookable",
                "mock_only": True,
            })
            continue
        enriched = deepcopy(segment)
        if mid in booked:
            enriched["mock_booking"] = booked[mid]
        billable_items.append(_line_item_from_segment(enriched, steps.get(mid)))

    for transit in booking_review.get("transit_segments") or []:
        non_billable_items.append({
            "item_id": transit.get("segment_index"),
            "name": "Transit suggestion",
            "category": "transit",
            "estimated_cost": _money((transit.get("prefilled_fields") or {}).get("estimated_cost")),
            "reason": "Traffic/navigation suggestion only; not merchant payment.",
            "mock_only": True,
        })

    for item in booking_review.get("optional_addons_excluded") or []:
        non_billable_items.append({
            "item_id": item.get("merchant_id"),
            "name": item.get("name"),
            "category": item.get("category"),
            "reason": "Optional add-on not accepted by user.",
            "mock_only": True,
        })

    accepted_items = [_line_item_from_addon(addon) for addon in accepted_addons]
    billable_items.extend(accepted_items)

    subtotal = _money(sum(item.get("subtotal", 0) for item in billable_items))
    group_total = _money(sum(item.get("group_coupon_price", item.get("subtotal", 0)) for item in billable_items))
    member_total = _money(sum(item.get("member_price", item.get("subtotal", 0)) for item in billable_items))
    one_click_total = _money(max(0.0, subtotal - min(12.0, subtotal * 0.03)))
    separate_total = group_total
    best_combo_total = min([x for x in (separate_total, one_click_total, member_total, group_total) if x >= 0], default=subtotal)

    strategies = [
        _strategy("分开购买", "separate_purchase", separate_total, subtotal, [
            "Use best local Mock coupon/deal per merchant item.",
            "May be cheaper than one-click checkout when group deals differ by merchant.",
        ], "分开买会逐项套用 Mock 团券。"),
        _strategy("Mock 一键买单", "one_click_checkout", one_click_total, subtotal, [
            "Creates a local mock_order_id only after user clicks Mock pay.",
            "No real payment link, QR code, or external payment API.",
        ], "一键买单更省事，但不一定最低价。"),
        _strategy("Mock 会员价", "member_price", member_total, subtotal, [
            "Local member-price simulation.",
            "No real membership verification.",
        ], "模拟会员价，适合展示会员权益。"),
        _strategy("Mock 团券", "group_coupon", group_total, subtotal, [
            "Same-day usable: Mock.",
            "Refundable: Mock.",
            "Shared by party: Mock.",
            "No real coupon claim.",
        ], "优先展示美团团券/套餐券味道。"),
        _strategy("综合最优", "best_combo", best_combo_total, subtotal, [
            "Chooses the cheapest local Mock strategy result.",
            "If separate purchase is cheaper, do not force one-click checkout.",
        ], "综合比较后给出最低 Mock 总价。"),
    ]
    recommended = None
    if strategies and separate_total < one_click_total:
        recommended = next((s for s in strategies if s["strategy_id"] == "separate_purchase"), None)
    if recommended is None and strategies:
        recommended = min(strategies, key=lambda x: (x["total"], -x["savings"]))
    if recommended:
        recommended["recommended"] = True
    warnings = [
        "Demo Mock only: no real payment, coupon claim, member verification, collection link, or merchant settlement.",
    ]
    if recommended and recommended["strategy_id"] == "separate_purchase":
        warnings.append("分开买更便宜，建议不要强制一键付款。")
    return {
        "checkout_id": _mock_id("checkout"),
        "mode": "mock_checkout",
        "status": "preview",
        "currency": "CNY",
        "billable_items": billable_items,
        "non_billable_items": non_billable_items,
        "optional_addons": booking_review.get("optional_addons_excluded") or [],
        "accepted_addons": accepted_addons,
        "price_strategies": strategies,
        "recommended_strategy": recommended,
        "coupon_summary": {
            "mock_coupon_count": len([i for i in billable_items if i.get("mock_coupon_id")]),
            "best_coupon_total": group_total,
            "rules": ["Local Mock coupons only.", "No real coupon inventory or claiming."],
        },
        "member_summary": {
            "member_total": member_total,
            "rules": ["Local Mock member price only.", "No real account or member verification."],
        },
        "subtotal": subtotal,
        "payable_total": recommended["total"] if recommended else subtotal,
        "warnings": warnings,
        "mock_only": True,
        "real_payment": False,
        "real_coupon": False,
        "real_member": False,
    }


def apply_checkout_strategy(preview: dict[str, Any] | None, strategy_id: str | None) -> dict[str, Any]:
    preview = deepcopy(preview or {})
    strategies = preview.get("price_strategies") or []
    chosen = None
    for strategy in strategies:
        strategy["recommended"] = False
        if strategy.get("strategy_id") == strategy_id:
            chosen = strategy
    if chosen is None and strategies:
        chosen = preview.get("recommended_strategy") or strategies[0]
    if chosen:
        chosen["recommended"] = True
        preview["recommended_strategy"] = chosen
        preview["payable_total"] = chosen.get("total", preview.get("subtotal", 0))
    preview["status"] = "strategy_applied"
    preview["mock_only"] = True
    return preview


def pay_mock_checkout(preview: dict[str, Any] | None, strategy_id: str | None = None) -> dict[str, Any]:
    preview = apply_checkout_strategy(preview, strategy_id)
    strategy = preview.get("recommended_strategy") or {}
    paid_items = preview.get("billable_items") or []
    return {
        "mock_payment_id": _mock_id("pay"),
        "mock_order_id": _mock_id("order"),
        "status": "mock_paid",
        "paid_total": _money(strategy.get("total", preview.get("payable_total", 0))),
        "strategy_id": strategy.get("strategy_id"),
        "paid_items": paid_items,
        "mock_only": True,
        "real_payment": False,
        "message": "Demo Mock 支付结果：没有真实扣款、没有真实支付链接、没有真实二维码。",
    }


def split_mock_checkout(
    preview: dict[str, Any] | None,
    *,
    mode: str = "aa",
    members: list[str] | None = None,
    host: str = "发起人",
    exempted_members: list[str] | None = None,
) -> dict[str, Any]:
    preview = preview or {}
    total = _money(preview.get("payable_total") or (preview.get("recommended_strategy") or {}).get("total") or 0)
    members = list(members or ["发起人", "朋友A", "朋友B", "朋友C"])
    if host not in members:
        members.insert(0, host)
    exempted = set(exempted_members or [])
    payer_summary: dict[str, float] = {}
    if mode == "host_treat":
        payer_summary = {m: 0.0 for m in members}
        payer_summary[host] = total
    elif mode == "custom_exemptions":
        payers = [m for m in members if m not in exempted]
        shares = _round_split(total, len(payers))
        payer_summary = {m: 0.0 for m in members}
        for m, amount in zip(payers, shares):
            payer_summary[m] = amount
    else:
        mode = "aa"
        shares = _round_split(total, len(members))
        payer_summary = {m: amount for m, amount in zip(members, shares)}
    return {
        "mock_split_id": _mock_id("split"),
        "mode": mode,
        "payer_summary": payer_summary,
        "per_person": _money(total / max(1, len([m for m, v in payer_summary.items() if v > 0]))),
        "host_pays": _money(payer_summary.get(host, 0)),
        "exempted_members": list(exempted),
        "mock_collect_links": {
            member: f"/mock/split/{{mock_split_id}}?member={member}".replace("{mock_split_id}", _mock_id("splitlink"))
            for member in members
        },
        "message": "Demo Mock 分账：没有真实收款链接、没有真实扣款。",
        "mock_only": True,
        "real_collection": False,
    }
