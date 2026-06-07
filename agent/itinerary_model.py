"""Closed-loop itinerary model for Phase 2A.

This module keeps the existing planner output compatible while adding a
structured, executable itinerary envelope. It does not call external APIs.
"""
from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from typing import Any

from agent.price_optimizer import optimize_price


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


BUSINESS_KINDS = {"activity", "restaurant", "stayin", "delivery", "addon"}


def _load_json(filename: str, fallback):
    try:
        with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if data is not None else fallback
    except Exception:
        return fallback


def _merchant_index() -> dict[str, dict[str, Any]]:
    merchants = _load_json("merchants.json", [])
    return {m.get("id"): m for m in merchants if isinstance(m, dict)}


def _travel_data() -> dict[str, dict[str, int]]:
    return _load_json("travel.json", {})


def _travel_between(from_area: str | None, to_area: str | None) -> dict[str, int]:
    if not from_area or not to_area:
        return {"walk": 0, "taxi": 0, "metro": 0}
    travel = _travel_data()
    key = f"{from_area}->{to_area}"
    rev = f"{to_area}->{from_area}"
    return travel.get(key) or travel.get(rev) or {"walk": 60, "taxi": 22, "metro": 30}


def _to_minutes(value: Any, default: int = 14 * 60) -> int:
    if isinstance(value, (int, float)):
        return int(value) * 60 if value < 24 else int(value)
    if not isinstance(value, str):
        return default
    text = value.strip()
    if ":" in text:
        h, m = text.split(":", 1)
        return int(h) * 60 + int(m)
    if text.isdigit():
        return int(text) * 60
    return default


def _to_time(minutes: int) -> str:
    minutes = max(0, int(round(minutes)))
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"


def _role_for_step(step: dict[str, Any]) -> str:
    if step.get("slot_role"):
        return step["slot_role"]
    return {
        "activity": "PLAY",
        "restaurant": "EAT",
        "stayin": "STAYIN",
        "delivery": "ADDON",
        "addon": "ADDON",
    }.get(step.get("kind"), "PLAY")


def _segment_source(step: dict[str, Any], role: str, request: dict[str, Any]) -> str:
    category = step.get("category")
    for item in (request.get("intent_frame") or {}).get("sequence", []) or []:
        if item.get("source") != "explicit_text":
            continue
        if item.get("role") != role:
            continue
        if item.get("category") in (None, category):
            return "explicit_text"
    for item in request.get("explicit_categories", []) or []:
        if item.get("role") == role and item.get("category") == category:
            return "explicit_text"
    if step.get("kind") == "addon":
        return "optional_addon"
    return "proposed_secondary"


def _coupon_summary(step: dict[str, Any]) -> dict[str, Any]:
    group_deal = step.get("group_deal") or {}
    raw_price = int(step.get("price", step.get("cost", 0)) or 0)
    if not raw_price:
        candidates = step.get("merchant_candidates") or []
        if candidates:
            raw_price = int(candidates[0].get("price", 0) or 0)
    deal_price = int(group_deal.get("price", raw_price) or raw_price) if isinstance(group_deal, dict) else raw_price
    return {
        "original_price": raw_price,
        "group_deal_price": deal_price,
        "member_price": max(0, deal_price - 5) if raw_price else 0,
        "same_day_usable": True,
        "weekend_usable": True,
        "refundable": True,
        "reservation_required": bool(step.get("can_reserve")),
        "not_stackable": True,
    }


def _booking_summary(step: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    category = step.get("category")
    party_size = int(request.get("party_size", 1) or 1)
    base = {
        "merchant": step.get("name"),
        "category": category,
        "people": party_size,
        "arrival_time": step.get("start"),
        "duration_minutes": step.get("duration_minutes")
        or (_to_minutes(step.get("end")) - _to_minutes(step.get("start"))),
        "mock_contact": "商家电话 Mock 400-000-0000",
        "action_label": "确认预约这一段",
    }
    if category == "剧本杀":
        status = step.get("script_status") or {}
        return {
            **base,
            "script_name": status.get("script_name") or step.get("name"),
            "style": status.get("style") or request.get("script_style"),
            "session_time": status.get("start") or step.get("start"),
            "assembling": bool(status.get("need_players") or status.get("status") == "assembling"),
            "newbie_friendly": step.get("newbie_friendly"),
            "horror_level": step.get("horror_level"),
        }
    if step.get("kind") == "restaurant":
        table = "小桌" if party_size <= 2 else ("中桌" if party_size <= 6 else "大桌")
        return {
            **base,
            "table_type": table,
            "use_group_deal": bool(step.get("group_deal")),
            "refundable": True,
        }
    if category == "电影院":
        return {
            **base,
            "movie": "影片/场次 Mock",
            "seats": "系统推荐连座 Mock",
            "refund_or_change": True,
        }
    return {
        **base,
        "item": step.get("name"),
        "usage_limits": step.get("flags", {}),
    }


def _support_options(segment_id: str) -> list[dict[str, str]]:
    return [
        {"type": "full_or_queue", "label": "商家满座/排队太久", "segment_id": segment_id},
        {"type": "cancel", "label": "想取消这一段", "segment_id": segment_id},
        {"type": "change_time", "label": "想换时间", "segment_id": segment_id},
        {"type": "mismatch", "label": "到店货不对板/项目缩水", "segment_id": segment_id},
        {"type": "coupon_failed", "label": "验券失败", "segment_id": segment_id},
        {"type": "contact_merchant", "label": "联系商家", "segment_id": segment_id},
        {"type": "contact_platform", "label": "联系平台客服", "segment_id": segment_id},
    ]


def build_support_case(segment_id: str, issue_type: str) -> dict[str, Any]:
    actions = {
        "full_or_queue": ["优先同商圈换一家", "保留后续行程", "必要时顺延时间线"],
        "cancel": ["展示 Mock 退款规则", "从主行程移除该段", "重算预算"],
        "change_time": ["查看同商家可改时间", "重算后续交通与到达时间"],
        "mismatch": ["联系平台客服", "保留证据", "按 Mock 规则发起补偿"],
        "coupon_failed": ["联系商家验券", "换用到店支付 Mock", "联系平台客服"],
        "contact_merchant": ["拨打商家电话 Mock", "发送预约信息 Mock"],
        "contact_platform": ["接入平台客服 Mock", "3 分钟内响应 Mock"],
    }
    return {
        "issue_type": issue_type,
        "segment_id": segment_id,
        "suggested_actions": actions.get(issue_type, ["联系平台客服", "保留当前行程"]),
        "refund_policy": "Mock：不执行真实退款，仅展示可解释规则。",
        "support_message": "已为你模拟接入美团客服，预计 3 分钟内响应。",
        "next_step": "replace_segment" if issue_type in {"full_or_queue", "change_time"} else "contact_merchant",
    }


def _replace_options() -> list[dict[str, str]]:
    return [
        {"type": "nearer", "label": "换同类更近的"},
        {"type": "cheaper", "label": "换同类更便宜的"},
        {"type": "higher_rating", "label": "换评分更高的"},
        {"type": "no_queue", "label": "换不排队的"},
    ]


def _candidate_from_merchant(merchant: dict[str, Any], selected: bool = False) -> dict[str, Any]:
    group_deal = merchant.get("group_deal") or {}
    coupon_notes = []
    if group_deal:
        coupon_notes.append(f"团购价 ¥{group_deal.get('price', merchant.get('price', 0))}")
    return {
        "merchant_id": merchant.get("id"),
        "name": merchant.get("name"),
        "category": merchant.get("category"),
        "area": merchant.get("area"),
        "price": merchant.get("price", merchant.get("cost", 0)),
        "rating": merchant.get("rating", 0),
        "review_count": merchant.get("review_count", 0),
        "review_tags": merchant.get("review_tags", merchant.get("tags", [])) or [],
        "review_snippet": merchant.get("review_snippet", ""),
        "duration_minutes": merchant.get("duration_minutes", 0),
        "can_reserve": bool(merchant.get("can_reserve")),
        "open": merchant.get("open", ""),
        "close": merchant.get("close", ""),
        "group_deal": group_deal,
        "reason": "当前选中" if selected else "同类备选",
        "risk_notes": [],
        "coupon_notes": coupon_notes,
    }


def _transit_options(from_ref: dict[str, Any], to_ref: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    from_area = from_ref.get("area")
    to_area = to_ref.get("area")
    tv = _travel_between(from_area, to_area)
    options = []
    if tv.get("taxi", 999) < 999:
        options.append({
            "mode": "taxi",
            "duration_minutes": int(tv.get("taxi", 0) or 0),
            "cost": max(0, int(tv.get("taxi", 0) or 0) + 8),
            "walk_minutes": 2,
            "description": f"打车约 {tv.get('taxi', 0)} 分钟，步行约 2 分钟",
        })
    if tv.get("metro", 999) < 999:
        options.append({
            "mode": "public",
            "duration_minutes": int(tv.get("metro", 0) or 0),
            "cost": 4 if tv.get("metro", 0) else 0,
            "walk_minutes": 12 if tv.get("metro", 0) else 0,
            "description": f"地铁/公交约 {tv.get('metro', 0)} 分钟",
        })
    if tv.get("walk", 999) <= 45:
        options.append({
            "mode": "walk",
            "duration_minutes": int(tv.get("walk", 0) or 0),
            "cost": 0,
            "walk_minutes": int(tv.get("walk", 0) or 0),
            "description": f"步行约 {tv.get('walk', 0)} 分钟",
        })
    if not options:
        options.append({
            "mode": "taxi",
            "duration_minutes": int(tv.get("taxi", 22) or 22),
            "cost": 30,
            "walk_minutes": 2,
            "description": "轻规则估算交通时间",
        })
    preferred = request.get("transport")
    recommended = "public" if preferred == "public" and any(o["mode"] == "public" for o in options) else options[0]["mode"]
    return {
        "options": options[:3],
        "recommended_mode": recommended,
        "reason": "按用户出行方式与耗时综合推荐" if preferred else "按最短可达方式推荐",
    }


def attach_closed_itinerary(plan: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of plan with `itinerary` attached."""
    plan = deepcopy(plan or {})
    if plan.get("unavailable"):
        plan["itinerary"] = {
            "itinerary_id": f"itin_{uuid.uuid4().hex[:8]}",
            "intent_summary": request.get("goal_summary") or request.get("primary_intent") or "needs relaxation",
            "status": "needs_selection",
            "origin": {"type": "unknown", "area": None, "source": "unknown"},
            "available_window": {"start_time": None, "end_time": None, "duration_minutes": None, "source": "unknown"},
            "segments": [],
            "transits": [],
            "return_transit": None,
            "optional_addons": [],
            "price_optimization": {},
            "warnings": plan.get("risks", []) or [plan.get("reason", "需要放宽条件")],
            "missing_for_closure": [],
        }
        return plan

    intent_frame = request.get("intent_frame") or {}
    confirmed = intent_frame.get("confirmed_fields") or {}
    sources = intent_frame.get("field_sources") or {}
    home_source = request.get("origin_area_source") or sources.get("home_area", "unknown")
    home_area = request.get("origin_area") or request.get("home_area")
    origin_known = bool(home_area) and home_source in {"explicit_text", "user_answer", "profile_memory"}
    origin = {
        "type": "home_area" if origin_known else "unknown",
        "area": home_area if origin_known else None,
        "source": home_source if origin_known else "unknown",
    }

    duration_minutes = confirmed.get("duration_minutes")
    if not duration_minutes and request.get("window_hours"):
        duration_minutes = int(request.get("window_hours") or 0) * 60
    start_source = sources.get("start_time", "unknown")
    available_window = {
        "start_time": request.get("start_time") if start_source in {"explicit_text", "user_answer"} else None,
        "end_time": confirmed.get("end_time"),
        "duration_minutes": duration_minutes,
        "source": start_source if start_source in {"explicit_text", "user_answer"} else "unknown",
    }

    merchants = _merchant_index()
    business_steps = [s for s in plan.get("steps", []) if s.get("kind") in BUSINESS_KINDS]
    segments: list[dict[str, Any]] = []
    warnings = list(plan.get("risks") or [])

    for idx, step in enumerate(business_steps, 1):
        segment_id = f"seg_{idx}"
        role = _role_for_step(step)
        selected = merchants.get(step.get("id"), step)
        candidates = [_candidate_from_merchant({**selected, **step}, selected=True)]
        alt_ids = []
        for key, ids in (plan.get("slot_alternatives") or {}).items():
            if key.startswith(role.lower()):
                alt_ids.extend(ids)
        for mid in alt_ids:
            if mid in merchants and merchants[mid].get("category") == step.get("category"):
                candidates.append(_candidate_from_merchant(merchants[mid]))
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c["merchant_id"] in seen:
                continue
            seen.add(c["merchant_id"])
            unique_candidates.append(c)
        if len(unique_candidates) < 2 and role in {"PLAY", "EAT", "ADDON"}:
            warnings.append(f"{step.get('category')} 同类备选不足，未静默换品类")

        segment = {
            "segment_id": segment_id,
            "role": role,
            "category": step.get("category"),
            "title": step.get("slot_title") or step.get("name"),
            "source": _segment_source(step, role, request),
            "is_core": step.get("kind") != "addon",
            "start_time": step.get("start"),
            "end_time": step.get("end"),
            "duration_minutes": _to_minutes(step.get("end")) - _to_minutes(step.get("start")),
            "area": step.get("area"),
            "selected_merchant": step.get("id"),
            "merchant_candidates": unique_candidates[:3],
            "booking_requirements": {
                "need_people": role in {"PLAY", "EAT"},
                "need_time": bool(step.get("can_reserve")),
                "need_coupon_choice": bool(step.get("group_deal")),
            },
            "booking_summary": _booking_summary(step, request),
            "coupon_summary": _coupon_summary({**selected, **step}),
            "support_options": _support_options(segment_id),
            "replace_options": _replace_options(),
            "status": "candidate",
        }
        segments.append(segment)

    transits: list[dict[str, Any]] = []
    if segments:
        previous_ref = {"type": "origin", "id": "origin", "area": origin.get("area")}
        for idx, seg in enumerate(segments, 1):
            if previous_ref.get("area") and seg.get("area"):
                transit = _transit_options(previous_ref, {"area": seg["area"]}, request)
                transits.append({
                    "transit_id": f"tr_{idx}",
                    "from": previous_ref,
                    "to": {"type": "segment", "id": seg["segment_id"], "area": seg["area"]},
                    **transit,
                })
            previous_ref = {"type": "segment", "id": seg["segment_id"], "area": seg.get("area")}

    missing_for_closure: list[str] = []
    if not origin_known:
        missing_for_closure.append("还不知道从哪里出发")
    if not available_window.get("duration_minutes"):
        missing_for_closure.append("还不知道这次可用多久")
    return_transit = None
    if origin_known and segments:
        last = segments[-1]
        transit = _transit_options({"type": "segment", "id": last["segment_id"], "area": last.get("area")}, origin, request)
        return_transit = {
            "transit_id": "tr_return",
            "from": {"type": "segment", "id": last["segment_id"], "area": last.get("area")},
            "to": {"type": "origin", "id": "origin", "area": origin.get("area")},
            **transit,
        }
    else:
        missing_for_closure.append("还不知道最后从哪里回去/回哪里")

    price_optimization = optimize_price({**plan, "itinerary": {"segments": segments}}, request)
    if available_window.get("duration_minutes") and plan.get("total_minutes", 0) > available_window["duration_minutes"]:
        warnings.append("总时长超过用户可用窗口，需要放宽时间或减少节点")
    plan["price_optimization"] = price_optimization
    plan["itinerary"] = {
        "itinerary_id": f"itin_{uuid.uuid4().hex[:8]}",
        "intent_summary": request.get("goal_summary") or plan.get("title") or request.get("primary_intent"),
        "status": "draft",
        "origin": origin,
        "available_window": available_window,
        "segments": segments,
        "transits": transits,
        "return_transit": return_transit,
        "optional_addons": plan.get("optional_addons") or [],
        "price_optimization": price_optimization,
        "warnings": warnings,
        "missing_for_closure": missing_for_closure,
    }
    if request.get("scene") == "stay_in" and any(k in (request.get("raw_text") or "") for k in ("看点", "看电影", "追剧", "看东西")):
        plan["itinerary"]["context_note"] = "娱乐内容由用户自行选择；本方案只安排吃喝补给/到家服务。"
    return plan


def attach_closed_itineraries(plans: list[dict[str, Any]], request: dict[str, Any]) -> list[dict[str, Any]]:
    return [attach_closed_itinerary(plan, request) for plan in (plans or [])]


def _review_booking_type(segment: dict[str, Any]) -> str:
    role = segment.get("role")
    category = segment.get("category")
    if role == "EAT":
        return "restaurant_booking"
    if category in {"蛋糕鲜花", "鲜花", "蛋糕"} or segment.get("role") == "STAYIN":
        return "delivery_note" if category in {"蛋糕鲜花", "鲜花", "蛋糕", "外卖", "闪购"} else "activity_booking"
    if role == "ADDON":
        return "delivery_note" if category in {"外卖", "闪购", "奶茶", "咖啡", "甜品"} else "activity_booking"
    return "activity_booking"


def _review_required_fields(booking_type: str) -> list[str]:
    if booking_type == "restaurant_booking":
        return ["party_size", "scheduled_start", "table_type", "coupon_choice", "merchant_contact"]
    if booking_type == "delivery_note":
        return ["scheduled_start", "delivery_place", "receiver_note", "merchant_contact"]
    if booking_type == "transit_only":
        return []
    return ["party_size", "scheduled_start", "theme_or_session", "merchant_contact"]


def _review_prefilled_fields(segment: dict[str, Any], request: dict[str, Any], booking_type: str) -> dict[str, Any]:
    summary = segment.get("booking_summary") or {}
    coupon = segment.get("coupon_summary") or {}
    fields: dict[str, Any] = {
        "scheduled_start": segment.get("start_time"),
        "scheduled_end": segment.get("end_time"),
        "party_size": summary.get("people") or request.get("party_size"),
    }
    if booking_type == "restaurant_booking":
        fields.update({
            "table_type": summary.get("table_type") or "standard_table",
            "coupon_choice": "group_deal" if coupon.get("group_deal_price") else "pay_at_store_mock",
        })
    elif booking_type == "delivery_note":
        fields.update({
            "delivery_place": segment.get("area") or request.get("home_area") or "to_be_confirmed",
            "receiver_note": "Mock delivery note; no real delivery API call",
        })
    else:
        fields.update({
            "theme_or_session": summary.get("script_name") or summary.get("movie") or segment.get("title"),
            "session_time": summary.get("session_time") or segment.get("start_time"),
        })
    return {k: v for k, v in fields.items() if v not in (None, "", [])}


def _coupon_hint(segment: dict[str, Any]) -> str:
    coupon = segment.get("coupon_summary") or {}
    if coupon.get("group_deal_price"):
        return f"Mock group deal: ¥{coupon.get('group_deal_price')}; pay display only, no real payment."
    return "Mock booking only; payment is not executed."


def build_booking_review(
    plan: dict[str, Any] | None,
    request: dict[str, Any] | None,
    accepted_addons: list[str] | None = None,
) -> dict[str, Any]:
    """Build a per-segment Mock booking review from the selected itinerary.

    The review is deliberately local and deterministic: it does not call maps,
    payment, customer service, inventory, or merchant booking APIs.
    """
    plan = plan or {}
    request = request or {}
    accepted = set(accepted_addons or [])
    itinerary = plan.get("itinerary") or attach_closed_itinerary(plan, request).get("itinerary") or {}
    review_segments: list[dict[str, Any]] = []

    for idx, segment in enumerate(itinerary.get("segments") or []):
        source = segment.get("source")
        merchant_id = segment.get("selected_merchant")
        if source == "optional_addon" and merchant_id not in accepted:
            continue
        if not segment.get("is_core", True) and merchant_id not in accepted and source != "explicit_text":
            continue
        booking_type = _review_booking_type(segment)
        merchant_name = segment.get("title")
        candidates = segment.get("merchant_candidates") or []
        if candidates:
            merchant_name = candidates[0].get("name") or merchant_name
        review_segments.append({
            "segment_index": idx,
            "segment_id": segment.get("segment_id"),
            "role": segment.get("role"),
            "category": segment.get("category"),
            "merchant_id": merchant_id,
            "merchant_name": merchant_name,
            "scheduled_start": segment.get("start_time"),
            "scheduled_end": segment.get("end_time"),
            "duration_minutes": segment.get("duration_minutes"),
            "party_size": (segment.get("booking_summary") or {}).get("people") or request.get("party_size"),
            "booking_type": booking_type,
            "bookable": True,
            "required_fields": _review_required_fields(booking_type),
            "prefilled_fields": _review_prefilled_fields(segment, request, booking_type),
            "merchant_contact": "Mock merchant contact: 400-000-0000",
            "notes": [
                "Local Mock booking preview; no real merchant booking.",
                "Please review time, party size, coupon/payment hint, and merchant contact before confirming.",
            ],
            "coupon_or_pay_hint": _coupon_hint(segment),
            "status": "pending_user_review",
        })

    transit_segments = []
    for idx, transit in enumerate(itinerary.get("transits") or []):
        transit_segments.append({
            "segment_index": f"transit_{idx}",
            "booking_type": "transit_only",
            "bookable": False,
            "status": "info_only",
            "scheduled_start": None,
            "scheduled_end": None,
            "duration_minutes": transit.get("recommended", {}).get("duration_minutes"),
            "notes": [transit.get("recommended", {}).get("description") or "Transit suggestion only; no real map API call."],
            "required_fields": [],
            "prefilled_fields": {"mode": transit.get("recommended", {}).get("mode")},
        })

    optional = itinerary.get("optional_addons") or plan.get("optional_addons") or []
    review = {
        "mode": "review_required",
        "status": "pending_user_review",
        "segments": review_segments,
        "transit_segments": transit_segments,
        "optional_addons_excluded": [
            {
                "merchant_id": item.get("id") or item.get("merchant_id"),
                "name": item.get("name"),
                "category": item.get("category"),
            }
            for item in optional
            if (item.get("id") or item.get("merchant_id")) not in accepted
        ],
        "warnings": list(itinerary.get("warnings") or []),
        "mock_only": True,
        "real_booking": False,
        "real_payment": False,
        "real_map_api": False,
    }
    if not review_segments:
        review["warnings"].append("No bookable core segment is available for booking review.")
    return review


def mark_booking_review_confirmed(review: dict[str, Any] | None, bookings: list[dict[str, Any]]) -> dict[str, Any]:
    review = deepcopy(review or {})
    by_mid = {b.get("merchant_id"): b for b in bookings or []}
    for segment in review.get("segments") or []:
        booking = by_mid.get(segment.get("merchant_id"))
        if booking:
            segment["status"] = "mock_booked"
            segment["mock_booking"] = booking
        elif segment.get("bookable"):
            segment["status"] = "ready"
    review["mode"] = "confirmed"
    review["status"] = "mock_booked"
    review["bookings"] = bookings or []
    review["mock_only"] = True
    review["real_booking"] = False
    review["real_payment"] = False
    return review


def shift_plan_for_booking_review(
    plan: dict[str, Any] | None,
    request: dict[str, Any] | None,
    segment_index: int,
    *,
    new_start: str | None = None,
    delta_minutes: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    """Shift a selected segment and all following timeline steps.

    This only edits local Mock time fields and never replaces merchants.
    """
    request = request or {}
    plan = deepcopy(plan or {})
    steps = plan.get("steps") or []
    business_positions = [
        pos for pos, step in enumerate(steps)
        if step.get("kind") in BUSINESS_KINDS and not (step.get("kind") == "addon" and step.get("source") == "optional_addon")
    ]
    warnings: list[str] = []
    if segment_index < 0 or segment_index >= len(business_positions):
        review = build_booking_review(plan, request)
        review["warnings"].append(f"segment_index {segment_index} is out of range")
        return plan, review, review.get("warnings") or []

    raw_pos = business_positions[segment_index]
    old_start = _to_minutes(steps[raw_pos].get("start"))
    if delta_minutes is None:
        if new_start:
            delta_minutes = _to_minutes(new_start) - old_start
        else:
            delta_minutes = 0
    delta_minutes = int(delta_minutes or 0)
    if delta_minutes == 0:
        review = build_booking_review(plan, request)
        return plan, review, warnings

    for pos in range(raw_pos, len(steps)):
        step = steps[pos]
        if step.get("start"):
            step["start"] = _to_time(_to_minutes(step.get("start")) + delta_minutes)
        if step.get("end"):
            step["end"] = _to_time(_to_minutes(step.get("end")) + delta_minutes)
    plan["steps"] = steps
    if plan.get("start_time"):
        plan["start_time"] = steps[raw_pos].get("start") or plan.get("start_time")
    plan = attach_closed_itinerary(plan, request)
    if abs(delta_minutes) >= 90:
        warnings.append("Large time shift; please re-check opening hours in the real product.")
    warnings.append(f"Shifted segment {segment_index + 1} and following segments by {delta_minutes} minutes.")
    review = build_booking_review(plan, request)
    review["warnings"].extend(warnings)
    return plan, review, warnings


if __name__ == "__main__":
    sample = {
        "title": "sample",
        "steps": [],
        "total_cost_per_person": 0,
        "total_minutes": 0,
        "start_time": "19:00",
    }
    print(json.dumps(attach_closed_itinerary(sample, {}), ensure_ascii=False, indent=2))
