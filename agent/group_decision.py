"""Deterministic group-decision and mock vote-room helpers.

This module is intentionally local-rule only. It does not call an LLM, does not
create real share links, and does not book merchants. The goal is to make the
"send to friends for confirmation" demo explicit and testable.
"""
from __future__ import annotations

import re
import time
import uuid
from typing import Any


GROUP_TOKENS = (
    "朋友", "同学", "同事", "女朋友", "男朋友", "家人", "孩子", "几个人", "我们",
    "聚会", "四个人", "4个人", "三个人", "3个人",
    # Mojibake variants from legacy acceptance fixtures.
    "鏈嬪弸", "鍚屽", "鍚屼簨", "瀹朵汉", "瀛╁瓙", "鎴戜滑", "鑱氫細",
)


def build_group_decision(raw_text: str, intent_frame: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return broad group-choice hints for existing Phase 2A flows."""
    raw_text = raw_text or ""
    frame = intent_frame or {}
    is_group = any(token in raw_text for token in GROUP_TOKENS)
    participants = [token for token in ("朋友", "同学", "同事", "女朋友", "男朋友", "家人", "孩子") if token in raw_text]
    if not participants:
        participants = [token for token in ("鏈嬪弸", "鍚屽", "鍚屼簨", "瀹朵汉", "瀛╁瓙") if token in raw_text]

    choice_cards: list[dict[str, Any]] = []
    if frame.get("next_action") == "show_category_choices":
        choice_cards = [
            {"category": "剧本杀", "why": "适合 4-6 人互动，需要确认本型、人数和恐怖度。"},
            {"category": "KTV", "why": "适合晚上聚会，需注意自驾和是否饮酒。"},
            {"category": "台球", "why": "轻量、预算低、时间灵活，适合先集合。"},
            {"category": "密室", "why": "刺激感强，需要确认是否有人怕恐怖。"},
            {"category": "电影院", "why": "决策简单，适合不想太累的局。"},
            {"category": "桌游", "why": "轻松社交，适合预算较低或新朋友破冰。"},
        ]

    decision_mode = "ask_host"
    if choice_cards:
        decision_mode = "collect_votes" if is_group else "ask_host"
    if "位置不一样" in raw_text or "折中" in raw_text or "浣嶇疆涓嶄竴鏍" in raw_text or "鎶樹腑" in raw_text:
        decision_mode = "compromise_area"

    return {
        "is_group": is_group,
        "participants": participants,
        "known_preferences": _known_preferences(raw_text),
        "unknown_preferences": ["活动方向"] if choice_cards else [],
        "decision_mode": decision_mode,
        "choice_cards": choice_cards,
    }


def build_vote_room(
    session: dict[str, Any],
    *,
    session_id: str = "default",
    base_url: str = "http://127.0.0.1:8000",
    room_id: str | None = None,
) -> dict[str, Any] | None:
    """Build a mock vote room bound to the current planned/selected itinerary."""
    plan, plan_index = _current_plan(session)
    if not plan:
        return None

    room_id = room_id or uuid.uuid4().hex[:8]
    share_url = f"{base_url.rstrip('/')}/vote/{room_id}/page"
    options = _vote_options(session, plan, plan_index)
    if not options:
        return None
    votes = {option["option_id"]: 0 for option in options}
    room = {
        "room_id": room_id,
        "session_id": session_id,
        "created_at": int(time.time()),
        "deadline_minutes": 20,
        "share_url": share_url,
        "link": share_url,
        "share_card": _share_copy(session, plan, share_url),
        "status": "collecting",
        "plan_index": plan_index,
        "options": options,
        "votes": votes,
        "voters": {},
        "feedback": [],
        "hard_constraints": [],
        "warnings": [],
        "resolution": None,
        "confirmed_option": None,
    }
    room["summary"] = summarize_vote_room(room)
    return room


def submit_vote(
    room: dict[str, Any],
    *,
    voter: str,
    option_id: str,
    feedback_text: str = "",
) -> dict[str, Any]:
    """Record a friend's vote and optional text feedback."""
    voter = (voter or f"friend-{len(room.get('voters', {})) + 1}").strip()
    option_id = str(option_id or "")
    option = find_option(room, option_id)
    if not option:
        return {"ok": False, "message": "投票选项不存在", "room": room}

    votes = room.setdefault("votes", {})
    voters = room.setdefault("voters", {})
    old = voters.get(voter)
    if old in votes:
        votes[old] = max(0, int(votes.get(old, 0) or 0) - 1)
    voters[voter] = option_id
    votes[option_id] = int(votes.get(option_id, 0) or 0) + 1

    parsed = parse_friend_feedback(feedback_text, option)
    parsed["voter"] = voter
    parsed["option_id"] = option_id
    if feedback_text:
        room.setdefault("feedback", []).append(parsed)
    if parsed.get("is_hard_constraint"):
        room.setdefault("hard_constraints", []).append(parsed)
        room["status"] = "needs_replan"
    room["summary"] = summarize_vote_room(room)
    return {"ok": True, "room": room, "feedback": parsed}


def parse_friend_feedback(feedback_text: str, option: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify friend feedback into preference / constraint / time_shift."""
    text = (feedback_text or "").strip()
    low = text.lower()
    option = option or {}
    target = option.get("target_segment") or "whole_plan"
    out = {
        "text": text,
        "vote_type": "preference",
        "target_segment": target,
        "is_hard_constraint": False,
        "requires_replan": False,
        "exception_type": None,
        "shift_minutes": None,
        "constraint": None,
        "warning": "",
    }
    if not text:
        return out

    if any(token in text for token in ("不吃辣", "不能吃辣", "别太辣", "不要辣")) or "no spicy" in low:
        out.update({
            "vote_type": "constraint",
            "target_segment": "restaurant",
            "is_hard_constraint": True,
            "requires_replan": True,
            "exception_type": "restaurant_full",
            "constraint": "no_spicy",
            "warning": "朋友反馈不吃辣，需要确认餐饮段是否满足或局部换店。",
        })
        return out

    if any(token in text for token in ("玩过", "打过", "这个本")) and any(token in text for token in ("换", "玩过", "打过")):
        out.update({
            "vote_type": "constraint",
            "target_segment": "activity",
            "is_hard_constraint": True,
            "requires_replan": True,
            "exception_type": "ticket_soldout",
            "constraint": "played_before",
            "warning": "朋友反馈这个本玩过，需要局部替换活动段。",
        })
        return out

    if any(token in text for token in ("晚到", "迟到", "晚半小时", "迟半小时", "晚 30", "晚30", "30分钟")):
        minutes = 30 if any(token in text for token in ("半小时", "30")) else 60
        out.update({
            "vote_type": "time_shift",
            "target_segment": "time",
            "is_hard_constraint": True,
            "requires_replan": True,
            "exception_type": "time_conflict",
            "shift_minutes": minutes,
            "constraint": "late_arrival",
            "warning": f"朋友可能晚到 {minutes} 分钟，需要顺延时间线。",
        })
        return out

    if "恐怖" in text and any(token in text for token in ("不要", "不适合", "第一次", "新手", "怕")):
        out.update({
            "vote_type": "constraint",
            "target_segment": "activity",
            "is_hard_constraint": True,
            "requires_replan": True,
            "exception_type": "ticket_soldout",
            "constraint": "avoid_horror_newbie",
            "warning": "有新手或怕恐怖，需要换轻松一点的活动。",
        })
        return out

    if any(token in text for token in ("便宜", "预算", "太贵")):
        out.update({"vote_type": "preference", "constraint": "cheaper", "warning": "软偏好：希望便宜一点。"})
    elif any(token in text for token in ("轻松", "别太累")):
        out.update({"vote_type": "preference", "constraint": "easy_pace", "warning": "软偏好：希望轻松一点。"})
    elif any(token in text for token in ("太远", "近一点", "别太远")):
        out.update({"vote_type": "preference", "constraint": "nearby", "warning": "软偏好：希望离大家近一点。"})
    return out


def summarize_vote_room(room: dict[str, Any]) -> dict[str, Any]:
    votes = room.get("votes") or {}
    options = room.get("options") or []
    total_votes = sum(int(v or 0) for v in votes.values())
    leading = None
    if options:
        leading = max(options, key=lambda o: (int(votes.get(o.get("option_id"), 0) or 0), -int(o.get("order", 0) or 0)))
        leading = {**leading, "votes": int(votes.get(leading.get("option_id"), 0) or 0)}
    hard = room.get("hard_constraints") or []
    return {
        "total_votes": total_votes,
        "leading_option": leading if total_votes > 0 else None,
        "hard_constraints": hard,
        "requires_replan": bool(hard),
        "can_confirm_leader": total_votes > 0 and not hard,
        "warnings": room.get("warnings") or [],
        "feedback_count": len(room.get("feedback") or []),
    }


def public_vote_room(room: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_vote_room(room)
    leading = summary.get("leading_option")
    winner = leading
    return {
        "room_id": room.get("room_id"),
        "session_id": room.get("session_id"),
        "share_url": room.get("share_url") or room.get("link"),
        "link": room.get("link") or room.get("share_url"),
        "share_card": room.get("share_card", ""),
        "deadline_minutes": room.get("deadline_minutes", 20),
        "status": room.get("status", "collecting"),
        "options": room.get("options", []),
        "votes": room.get("votes", {}),
        "voters_count": len(room.get("voters") or {}),
        "total_votes": summary["total_votes"],
        "winner": winner,
        "summary": summary,
        "feedback": room.get("feedback", []),
        "hard_constraints": room.get("hard_constraints", []),
        "warnings": room.get("warnings", []),
        "resolution": room.get("resolution"),
        "confirmed_option": room.get("confirmed_option"),
    }


def find_option(room: dict[str, Any], option_id: str) -> dict[str, Any] | None:
    for option in room.get("options") or []:
        if str(option.get("option_id")) == str(option_id):
            return option
    return None


def first_replan_feedback(room: dict[str, Any]) -> dict[str, Any] | None:
    for item in room.get("hard_constraints") or []:
        if item.get("requires_replan"):
            return item
    return None


def replan_context_from_feedback(room: dict[str, Any], feedback: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    exception_type = feedback.get("exception_type") or "time_conflict"
    target = feedback.get("target_segment")
    context: dict[str, Any] = {
        "source": "friend_vote",
        "feedback_text": feedback.get("text", ""),
        "location_state": "before_departure",
    }
    if target == "restaurant":
        context["affected_segment_index"] = _first_segment_index(room, ("restaurant", "EAT"))
        if feedback.get("constraint") == "no_spicy":
            context["diet_limits"] = ["no_spicy"]
            context["safety_flags"] = ["no_spicy"]
    elif target == "activity":
        context["affected_segment_index"] = _first_segment_index(room, ("activity", "PLAY"))
    elif target == "time":
        context["shift_minutes"] = int(feedback.get("shift_minutes") or 30)
    return exception_type, context


def _known_preferences(text: str) -> list[str]:
    out: list[str] = []
    if "唱歌" in text or "鍞辨瓕" in text:
        out.append("有人想唱歌")
    if "台球" in text or "鍙扮悆" in text:
        out.append("有人想打台球")
    if "不吃辣" in text or "涓嶅悆杈" in text:
        out.append("有人不吃辣")
    if "怕恐怖" in text or "鎬曟亹鎬" in text:
        out.append("有人怕恐怖")
    return out


def _current_plan(session: dict[str, Any]) -> tuple[dict[str, Any] | None, int]:
    chosen = session.get("chosen")
    plans = session.get("plans") or []
    if chosen:
        for i, plan in enumerate(plans):
            if plan is chosen or plan.get("title") == chosen.get("title"):
                return chosen, i
        return chosen, int(session.get("selected_plan_index") or 0)
    if plans:
        return plans[0], 0
    return None, 0


def _vote_options(session: dict[str, Any], plan: dict[str, Any], plan_index: int) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    order = 0
    for i, candidate in enumerate(session.get("plans") or []):
        options.append({
            "option_id": f"plan_{i}",
            "index": i,
            "order": order,
            "kind": "plan",
            "target_segment": "whole_plan",
            "plan_index": i,
            "title": candidate.get("title") or f"方案 {i + 1}",
            "label": candidate.get("title") or f"方案 {i + 1}",
            "description": candidate.get("focus") or "整体方案备选",
            "cost": candidate.get("total_cost_per_person", 0),
            "minutes": candidate.get("total_minutes", 0),
        })
        order += 1

    for seg_idx, step in _business_positions(plan.get("steps") or []):
        if step.get("kind") == "activity":
            options.append(_segment_option("activity", seg_idx, step, order, plan_index))
            order += 1
        elif step.get("kind") == "restaurant":
            options.append(_segment_option("restaurant", seg_idx, step, order, plan_index))
            order += 1

    for i, addon in enumerate((plan.get("optional_addons") or [])[:3]):
        target = "restaurant" if addon.get("type") == "meal_after_play" or addon.get("category") not in ("奶茶", "咖啡", "甜品") else "addon"
        options.append({
            "option_id": f"addon_{i}",
            "index": None,
            "order": order,
            "kind": "addon",
            "target_segment": target,
            "plan_index": plan_index,
            "segment_index": None,
            "title": addon.get("title") or addon.get("name"),
            "label": addon.get("name") or addon.get("title"),
            "description": addon.get("reason") or "可选加购，不进入主行程账单",
            "cost": addon.get("price", 0),
            "minutes": 0,
        })
        order += 1

    options.append({
        "option_id": "time_on_time",
        "index": None,
        "order": order,
        "kind": "time",
        "target_segment": "time",
        "plan_index": plan_index,
        "title": "按原时间出发",
        "label": "按原时间出发",
        "description": "大家准点到，行程不变。",
        "cost": 0,
        "minutes": 0,
    })
    order += 1
    options.append({
        "option_id": "time_delay_30",
        "index": None,
        "order": order,
        "kind": "time",
        "target_segment": "time",
        "plan_index": plan_index,
        "title": "整体顺延 30 分钟",
        "label": "整体顺延 30 分钟",
        "description": "适合有人晚到，确认后只顺延时间线。",
        "cost": 0,
        "minutes": 30,
    })
    return options


def _segment_option(kind: str, seg_idx: int, step: dict[str, Any], order: int, plan_index: int) -> dict[str, Any]:
    label = "活动" if kind == "activity" else "餐饮"
    return {
        "option_id": f"{kind}_{seg_idx}",
        "index": None,
        "order": order,
        "kind": kind,
        "target_segment": kind,
        "plan_index": plan_index,
        "segment_index": seg_idx,
        "merchant_id": step.get("id"),
        "title": f"{label}：{step.get('name')}",
        "label": step.get("name"),
        "description": f"{step.get('category')} · {step.get('area')} · ¥{step.get('cost', 0)}",
        "cost": step.get("cost", 0),
        "minutes": _duration(step),
    }


def _business_positions(steps: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    out: list[tuple[int, dict[str, Any]]] = []
    for step in steps:
        if step.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery"):
            out.append((len(out), step))
    return out


def _first_segment_index(room: dict[str, Any], keys: tuple[str, str]) -> int | None:
    wanted_kind, wanted_role = keys
    for option in room.get("options") or []:
        if option.get("kind") == wanted_kind and option.get("segment_index") is not None:
            return int(option["segment_index"])
    return None


def _duration(step: dict[str, Any]) -> int:
    try:
        sh, sm = str(step.get("start", "00:00")).split(":", 1)
        eh, em = str(step.get("end", "00:00")).split(":", 1)
        return max(0, int(eh) * 60 + int(em) - int(sh) * 60 - int(sm))
    except Exception:
        return int(step.get("duration_minutes", 0) or 0)


def _share_copy(session: dict[str, Any], plan: dict[str, Any], share_url: str) -> str:
    req = session.get("request") or {}
    people = req.get("party_size") or "几"
    start = req.get("start_time") or "待确认"
    title = plan.get("title") or "周末方案"
    cost = plan.get("total_cost_per_person", 0)
    return (
        f"我用美团周到排了一个方案：{title}\n"
        f"人数：{people}人｜开始：{start}｜人均约 ¥{cost}\n"
        f"大家点一下偏好或留言硬约束，我再最终确认预约：{share_url}"
    )
