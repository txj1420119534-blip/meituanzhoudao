"""Local Mock support / aftersales helpers for Phase 2B Slice 5.

This module is intentionally deterministic and local-only. It does not call
real customer service, refund, payment, merchant, account, or external APIs.
"""
from __future__ import annotations

import copy
import time
import uuid
from typing import Any


ISSUE_TYPES = {
    "refund_request",
    "merchant_full",
    "late_arrival",
    "coupon_help",
    "change_time",
    "complaint",
    "other",
}

ISSUE_ALIASES = {
    "full_or_queue": "merchant_full",
    "cancel": "refund_request",
    "coupon_failed": "coupon_help",
    "contact_platform": "other",
    "contact_merchant": "other",
    "mismatch": "complaint",
}


def normalize_issue_type(issue_type: str | None) -> str:
    raw = str(issue_type or "other").strip()
    normalized = ISSUE_ALIASES.get(raw, raw)
    return normalized if normalized in ISSUE_TYPES else "other"


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _mock_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _clone(value: Any) -> Any:
    return copy.deepcopy(value)


def _safe_segment_from_itinerary(segment: dict[str, Any], index: int | None) -> dict[str, Any]:
    candidates = segment.get("merchant_candidates") or []
    first = candidates[0] if candidates else {}
    return {
        "source": "selected_itinerary",
        "segment_index": index,
        "segment_id": segment.get("segment_id"),
        "role": segment.get("role"),
        "category": segment.get("category") or first.get("category"),
        "title": segment.get("title") or first.get("name"),
        "merchant_id": segment.get("merchant_id") or first.get("merchant_id"),
        "merchant_name": segment.get("merchant_name") or first.get("name"),
        "area": segment.get("area") or first.get("area"),
        "start_time": segment.get("start_time"),
        "end_time": segment.get("end_time"),
        "status": segment.get("status"),
    }


def _safe_segment_from_booking(segment: dict[str, Any], index: int | None) -> dict[str, Any]:
    return {
        "source": "booking_review",
        "segment_index": index,
        "segment_id": segment.get("segment_id"),
        "role": segment.get("role"),
        "category": segment.get("category"),
        "title": segment.get("merchant_name") or segment.get("category"),
        "merchant_id": segment.get("merchant_id"),
        "merchant_name": segment.get("merchant_name"),
        "area": segment.get("area"),
        "start_time": segment.get("scheduled_start"),
        "end_time": segment.get("scheduled_end"),
        "booking_type": segment.get("booking_type"),
        "status": segment.get("status"),
    }


def _segments_for_source(session: dict[str, Any], source: str) -> list[dict[str, Any]]:
    if source == "booking_review":
        return list((session.get("booking_review") or {}).get("segments") or [])
    chosen = session.get("chosen") or {}
    itinerary = chosen.get("itinerary") or {}
    return list(itinerary.get("segments") or [])


def _resolve_segment(
    session: dict[str, Any],
    source: str,
    segment_id: str | None = None,
    target_segment_index: int | None = None,
) -> tuple[int | None, dict[str, Any] | None]:
    if source in {"checkout_result", "rescue_result", "general"}:
        return None, None
    segments = _segments_for_source(session, source)
    if target_segment_index is not None:
        try:
            idx = int(target_segment_index)
        except Exception:
            idx = -1
        if 0 <= idx < len(segments):
            seg = segments[idx]
            return idx, (
                _safe_segment_from_booking(seg, idx)
                if source == "booking_review"
                else _safe_segment_from_itinerary(seg, idx)
            )
    wanted = str(segment_id or "")
    if wanted:
        for idx, seg in enumerate(segments):
            if str(seg.get("segment_id") or "") == wanted:
                return idx, (
                    _safe_segment_from_booking(seg, idx)
                    if source == "booking_review"
                    else _safe_segment_from_itinerary(seg, idx)
                )
    return None, None


def _checkout_coupon_rules(session: dict[str, Any]) -> list[str]:
    preview = session.get("checkout_preview") or {}
    result = session.get("checkout_result") or {}
    strategy = preview.get("recommended_strategy") or {}
    rules = [
        "This is a local Mock coupon explanation; no real coupon is claimed.",
        "Displayed discounts are calculated from local merchant mock data only.",
    ]
    if strategy:
        rules.append(f"Current recommended mock strategy: {strategy.get('label') or strategy.get('strategy_id')}.")
    if result:
        rules.append(f"Mock order reference: {result.get('mock_order_id')}.")
    for warning in preview.get("warnings") or []:
        rules.append(str(warning))
    return rules


def _reply_for_issue(issue_type: str, target: dict[str, Any] | None, session: dict[str, Any]) -> str:
    target_name = (target or {}).get("merchant_name") or (target or {}).get("title") or "this itinerary item"
    replies = {
        "refund_request": (
            f"Demo Mock refund note for {target_name}: no real refund will be initiated. "
            "You can keep the plan, ask for a local replacement suggestion, or create a Mock aftersales ticket."
        ),
        "merchant_full": (
            f"{target_name} may be full or queueing. This Mock support entry recommends using local rescue "
            "to replace only this affected segment near the current area."
        ),
        "late_arrival": (
            "A friend may arrive late. This Mock support entry recommends shifting the timeline locally "
            "and preserving the selected merchants where possible."
        ),
        "coupon_help": "This is a Demo Mock coupon explanation. No real coupon is claimed or verified.",
        "change_time": (
            f"You can try changing the time for {target_name}. This is a local Mock suggestion and does not "
            "contact the merchant."
        ),
        "complaint": (
            "A local Mock complaint ticket can be generated for demo purposes. It will not be submitted to "
            "real Meituan customer service."
        ),
        "other": "A local Mock support ticket can be created. No real customer-service channel is contacted.",
    }
    if issue_type == "coupon_help":
        rules = _checkout_coupon_rules(session)
        return replies[issue_type] + " " + " ".join(rules[:2])
    return replies.get(issue_type, replies["other"])


def _actions_for_issue(issue_type: str) -> list[dict[str, Any]]:
    common = [
        {
            "action_id": "keep_plan",
            "label": "Keep current plan",
            "description": "Keep the current itinerary and only record this Mock support note.",
            "mock_only": True,
        }
    ]
    by_issue = {
        "refund_request": [
            {
                "action_id": "open_rescue",
                "label": "Find a local replacement",
                "description": "Open the existing rescue flow instead of starting a real refund.",
                "mock_only": True,
            },
            {
                "action_id": "create_mock_ticket",
                "label": "Create Mock aftersales ticket",
                "description": "Generate a local ticket number for demo tracking.",
                "mock_only": True,
            },
        ],
        "merchant_full": [
            {
                "action_id": "open_rescue",
                "label": "Open local rescue",
                "description": "Replace only the full/queueing segment through existing rescue logic.",
                "mock_only": True,
            }
        ],
        "late_arrival": [
            {
                "action_id": "shift_timeline",
                "label": "Shift timeline",
                "description": "Suggest a local time_conflict adjustment; no merchant is contacted.",
                "mock_only": True,
            }
        ],
        "change_time": [
            {
                "action_id": "shift_timeline",
                "label": "Shift timeline",
                "description": "Suggest a local booking-time adjustment.",
                "mock_only": True,
            }
        ],
        "coupon_help": [
            {
                "action_id": "show_coupon_rules",
                "label": "Show Mock coupon rules",
                "description": "Explain local coupon/member/group-deal mock rules.",
                "mock_only": True,
            }
        ],
        "complaint": [
            {
                "action_id": "create_mock_ticket",
                "label": "Create Mock complaint ticket",
                "description": "Generate a local complaint ticket number only.",
                "mock_only": True,
            }
        ],
        "other": [
            {
                "action_id": "create_mock_ticket",
                "label": "Create Mock support ticket",
                "description": "Generate a local ticket number only.",
                "mock_only": True,
            }
        ],
    }
    return common + by_issue.get(issue_type, by_issue["other"])


def _legacy_next_step(issue_type: str) -> str:
    if issue_type in {"merchant_full", "late_arrival", "change_time"}:
        return "replace_segment"
    if issue_type == "refund_request":
        return "refund_mock"
    if issue_type == "complaint":
        return "contact_merchant"
    return "keep_plan"


def create_support_case(
    session: dict[str, Any],
    session_id: str,
    issue_type: str | None = None,
    segment_id: str | None = None,
    target_segment_index: int | None = None,
    source: str | None = None,
    user_message: str | None = None,
) -> dict[str, Any]:
    issue = normalize_issue_type(issue_type)
    selected_source = source or "selected_itinerary"
    idx, target = _resolve_segment(session, selected_source, segment_id, target_segment_index)
    case_id = _mock_id("support")
    created_at = _now()
    case = {
        "support_case_id": case_id,
        "session_id": session_id,
        "issue_type": issue,
        "target_segment_index": idx,
        "target_segment": target,
        "source": selected_source,
        "status": "mock_open",
        "mock_only": True,
        "real_customer_service": False,
        "real_refund": False,
        "real_payment": False,
        "real_order_api": False,
        "messages": [
            {
                "role": "system",
                "text": "Local Mock support case created. No real customer-service, refund, order, payment, or merchant API is called.",
                "created_at": created_at,
            },
            {
                "role": "assistant",
                "text": _reply_for_issue(issue, target, session),
                "created_at": created_at,
            },
        ],
        "suggested_actions": _actions_for_issue(issue),
        "support_message": _reply_for_issue(issue, target, session),
        "refund_policy": "Mock only: no real refund is initiated.",
        "next_step": _legacy_next_step(issue),
        "coupon_rules": _checkout_coupon_rules(session) if issue == "coupon_help" else [],
        "checkout_snapshot": _clone(session.get("checkout_result") or session.get("checkout_preview") or {}) if selected_source == "checkout_result" else {},
        "rescue_snapshot": _clone(session.get("exception_result") or {}) if selected_source == "rescue_result" else {},
        "created_at": created_at,
        "updated_at": created_at,
    }
    if user_message:
        case["messages"].insert(1, {"role": "user", "text": str(user_message), "created_at": created_at})
    support_cases = session.setdefault("support_cases", {})
    support_cases[case_id] = case
    session["support_case"] = case
    return case


def get_support_case(session: dict[str, Any], support_case_id: str) -> dict[str, Any] | None:
    return (session.get("support_cases") or {}).get(support_case_id)


def reply_support_case(case: dict[str, Any], message: str) -> dict[str, Any]:
    now = _now()
    case.setdefault("messages", []).append({"role": "user", "text": str(message or ""), "created_at": now})
    case["messages"].append({
        "role": "assistant",
        "text": "Mock support has recorded your message. This does not contact real customer service.",
        "created_at": now,
    })
    case["updated_at"] = now
    return case


def apply_support_action(
    case: dict[str, Any],
    action_id: str,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = _now()
    action = str(action_id or "keep_plan")
    result: dict[str, Any] = {
        "action_id": action,
        "mock_only": True,
        "real_customer_service": False,
        "real_refund": False,
        "real_payment": False,
        "created_at": now,
    }
    target = case.get("target_segment") or {}
    if action == "open_rescue":
        issue = case.get("issue_type")
        result.update({
            "status": "mock_suggested",
            "next_api_hint": "/exception",
            "exception_type": "restaurant_full" if issue in {"merchant_full", "refund_request"} else "ticket_soldout",
            "context": {
                "location_state": "near_current_merchant",
                "affected_segment_index": case.get("target_segment_index"),
                "affected_segment_id": target.get("segment_id"),
                "current_area": target.get("area"),
                "current_merchant_id": target.get("merchant_id"),
            },
        })
    elif action == "shift_timeline":
        result.update({
            "status": "mock_suggested",
            "next_api_hint": "/exception",
            "exception_type": "time_conflict",
            "context": {
                "affected_segment_index": case.get("target_segment_index"),
                "affected_segment_id": target.get("segment_id"),
                "shift_minutes": 30,
            },
        })
    elif action == "show_coupon_rules":
        result.update({
            "status": "mock_rules",
            "coupon_rules": case.get("coupon_rules") or _checkout_coupon_rules(session or {}),
        })
    elif action == "create_mock_ticket":
        ticket_id = case.get("mock_ticket_id") or _mock_id("ticket")
        case["mock_ticket_id"] = ticket_id
        case["status"] = "mock_ticket_created"
        result.update({"status": "mock_ticket_created", "mock_ticket_id": ticket_id})
    else:
        result.update({"status": "mock_kept", "message": "Current plan kept; Mock support note recorded."})
    case["action_result"] = result
    case["updated_at"] = now
    case.setdefault("messages", []).append({
        "role": "assistant",
        "text": f"Mock action `{action}` completed locally. No real service was called.",
        "created_at": now,
    })
    return case
