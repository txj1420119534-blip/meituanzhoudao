"""
server.py —— FastAPI 薄服务层。
业务逻辑全部在 agent/，server.py 只做 HTTP 翻译。
启动：python server.py  →  http://127.0.0.1:8000/  /  http://127.0.0.1:8000/admin
"""
import sys
import os
import json
import time
import uuid
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse

from agent.core import Agent
from agent.group_decision import (
    build_vote_room,
    find_option,
    first_replan_feedback,
    public_vote_room,
    replan_context_from_feedback,
    submit_vote,
    summarize_vote_room,
)

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT, "web")
DATA_DIR = os.path.join(ROOT, "data")
MERCHANTS_PATH = os.path.join(DATA_DIR, "merchants.json")

app = FastAPI(title="美团周到 · API")

# CORS（允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 演示用：按 session_id 隔离 Agent，避免多用户串会话
AGENTS: dict[str, Agent] = {}
VOTE_ROOMS: dict[str, dict] = {}


def _session_id(body: dict | None = None, request: Request | None = None) -> str:
    body = body or {}
    if request:
        sid = request.headers.get("X-Session-Id") or request.query_params.get("session_id")
        if sid:
            return sid[:80]
    return str(body.get("session_id") or "default")[:80]


def _agent_for(session_id: str) -> Agent:
    if session_id not in AGENTS:
        AGENTS[session_id] = Agent()
    return AGENTS[session_id]


def _safe_session(s: dict) -> dict:
    """剔除掉 set / 不可序列化字段。"""
    if not s:
        return {}
    vote_room = s.get("vote_room")
    if vote_room and vote_room.get("room_id") in VOTE_ROOMS:
        vote_room = _public_vote_room(VOTE_ROOMS[vote_room["room_id"]])
    req = s.get("request") or {}
    safe_req = {k: v for k, v in req.items() if not k.startswith("_")}
    return {
        "request": safe_req,
        "profile": s.get("profile"),
        "plans": s.get("plans", []),
        "chosen": s.get("chosen"),
        "executed": s.get("executed", False),
        "share_card": s.get("share_card", ""),
        "addon": s.get("addon"),
        "rejected_addon_ids": s.get("rejected_addon_ids", []),
        "accepted_addons": s.get("accepted_addons", []),
        "bookings": s.get("bookings", []),
        "booking_review": s.get("booking_review"),
        "booking_result": s.get("booking_result"),
        "checkout_preview": s.get("checkout_preview"),
        "checkout_result": s.get("checkout_result"),
        "checkout_split": s.get("checkout_split"),
        "checkout_error": s.get("checkout_error"),
        "rejected_ids": list(s.get("rejected_ids", [])),
        "logs": s.get("logs", []),
        "exception_result": s.get("exception_result"),
        "mode": s.get("mode", "ready"),
        "clarifications_needed": s.get("clarifications_needed", []),
        "explicit_categories": s.get("explicit_categories", []),
        "intent_frame": s.get("intent_frame"),
        "constraints": s.get("constraints", {}),
        "group_decision": s.get("group_decision", {}),
        "vote_decision": s.get("vote_decision"),
        "price_optimization": s.get("price_optimization", {}),
        "support_case": s.get("support_case"),
        "support_cases": s.get("support_cases", {}),
        "support_error": s.get("support_error"),
        "vote_room": vote_room,
        "segment_choices": s.get("segment_choices", []),
    }


def _reservation_index() -> dict:
    """Collect local Mock reservations from active sessions for admin display."""
    out: dict[str, dict] = {}
    for sid, ag in AGENTS.items():
        session = ag.session or {}
        review = session.get("booking_review") or {}
        result = session.get("booking_result") or {}
        if result.get("status") not in {"mock_booked", "confirmed"}:
            continue
        for seg in review.get("segments") or []:
            mid = seg.get("merchant_id")
            if not mid:
                continue
            out[mid] = {
                "status": "有预定",
                "session_id": sid,
                "merchant_name": seg.get("merchant_name"),
                "scheduled_start": seg.get("scheduled_start"),
                "party_size": seg.get("party_size"),
                "booking_type": seg.get("booking_type"),
                "preview": f"{seg.get('scheduled_start') or '-'} / {seg.get('party_size') or '-'}人 / {seg.get('booking_type') or 'mock'}",
            }
    return out


def _winner(room: dict) -> dict | None:
    summary = summarize_vote_room(room)
    return summary.get("leading_option")


def _public_vote_room(room: dict) -> dict:
    return public_vote_room(room)


def _create_vote_room(session: dict, base_url: str = "http://127.0.0.1:8000") -> dict | None:
    plans = session.get("plans") or []
    req = session.get("request") or {}
    if len(plans) < 2 or int(req.get("party_size", 1) or 1) < 3:
        return None
    room_id = uuid.uuid4().hex[:8]
    options = []
    for i, p in enumerate(plans):
        options.append({
            "index": i,
            "title": p.get("title", f"方案 {i + 1}"),
            "focus": p.get("focus", ""),
            "cost": p.get("total_cost_per_person", 0),
            "minutes": p.get("total_minutes", 0),
        })
    room = {
        "room_id": room_id,
        "created_at": int(time.time()),
        "deadline_minutes": 20,
        "link": f"{base_url}/vote/{room_id}/page",
        "options": options,
        "votes": {str(o["index"]): 0 for o in options},
        "voters": {},
    }
    VOTE_ROOMS[room_id] = room
    session["vote_room"] = _public_vote_room(room)
    return session["vote_room"]


def _sync_session_vote_room(room_id: str):
    for ag in AGENTS.values():
        if ag.session and ag.session.get("vote_room") and ag.session["vote_room"].get("room_id") == room_id and room_id in VOTE_ROOMS:
            ag.session["vote_room"] = _public_vote_room(VOTE_ROOMS[room_id])


def _ensure_vote_room(session: dict):
    if not session or session.get("mode") != "planned" or session.get("vote_room"):
        return
    _create_vote_room(session)


def _create_vote_room(session: dict, session_id: str = "default", base_url: str = "http://127.0.0.1:8000") -> dict | None:
    """Create a Slice 2 mock vote room from current planned/selected session."""
    room = build_vote_room(session, session_id=session_id, base_url=base_url)
    if not room:
        return None
    VOTE_ROOMS[room["room_id"]] = room
    session["vote_room"] = _public_vote_room(room)
    return session["vote_room"]


def _sync_session_vote_room(room_id: str):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return
    sid = room.get("session_id")
    if sid in AGENTS:
        AGENTS[sid].session["vote_room"] = _public_vote_room(room)
        return
    for ag in AGENTS.values():
        if ag.session and ag.session.get("vote_room") and ag.session["vote_room"].get("room_id") == room_id:
            ag.session["vote_room"] = _public_vote_room(room)


def _ensure_vote_room(session: dict, session_id: str = "default", base_url: str = "http://127.0.0.1:8000"):
    if not session or session.get("mode") not in ("planned", "selected") or session.get("vote_room"):
        return
    req = session.get("request") or {}
    try:
        party_size = int(req.get("party_size", 1) or 1)
    except Exception:
        party_size = 1
    if party_size < 3:
        return
    _create_vote_room(session, session_id=session_id, base_url=base_url)


# ─────────────────────────────────────────────────────────────────
# 用户端接口
# ─────────────────────────────────────────────────────────────────
@app.post("/plan")
async def plan(request: Request):
    """主流程：一句话 → 解析 → 排方案。"""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        text = body.get("text", "")
        session = ag.run(text, context=body.get("planning_context") or {})
        _ensure_vote_room(session, session_id=sid, base_url=str(request.base_url).rstrip("/"))
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/refine")
async def refine(request: Request):
    """追问补全：用户回答了缺失字段后重新规划。
    body: {"answers": {"party_size": 4, "budget_per_person": 150, ...}}
    """
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        answers = body.get("answers", {}) or {}
        session = ag.refine(answers)
        _ensure_vote_room(session, session_id=sid, base_url=str(request.base_url).rstrip("/"))
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/clarify")
async def clarify(request: Request):
    return await refine(request)


@app.post("/confirm")
async def confirm(request: Request):
    """最终确认：执行预订 + 生成分享卡。"""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        if "plan_index" in body:
            ag.choose(body.get("plan_index", 0))
        session = ag.confirm_and_execute()
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/select")
async def select_plan(request: Request):
    """只选择候选方案，不预约、不下单、不生成分享卡。"""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        idx = body.get("plan_index", 0)
        session = ag.choose(idx)
        _ensure_vote_room(session, session_id=sid, base_url=str(request.base_url).rstrip("/"))
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/select_segments")
async def select_segments(request: Request):
    """Select one candidate per visible segment; no real booking is created here."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        session = ag.choose_segments(body.get("segments") or body.get("selected_segments") or [])
        _ensure_vote_room(session, session_id=sid, base_url=str(request.base_url).rstrip("/"))
        return {"ok": True, "session": _safe_session(session), "booking_review": session.get("booking_review")}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/booking/review")
async def booking_review(request: Request):
    """Prepare per-segment Mock booking review. No real merchant booking."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        if "plan_index" in body and not ag.session.get("chosen"):
            ag.choose(body.get("plan_index", 0))
        session = ag.prepare_booking_review()
        return {"ok": True, "session": _safe_session(session), "booking_review": session.get("booking_review")}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/booking/update")
async def booking_update(request: Request):
    """Update local booking review fields and shift following segments if needed."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.update_booking_review(
            segment_index=body.get("segment_index", 0),
            fields=body.get("fields") or {},
        )
        return {"ok": True, "session": _safe_session(session), "booking_review": session.get("booking_review")}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/booking/confirm")
async def booking_confirm(request: Request):
    """Confirm booking review and create local Mock booking result."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.confirm_and_execute()
        return {"ok": True, "session": _safe_session(session), "booking_result": session.get("booking_result")}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/addon/accept")
async def addon_accept(request: Request):
    """Explicitly add an optional add-on into the local Mock checkout bill."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.accept_addon(body.get("addon_id") or body.get("merchant_id"))
        return {"ok": not bool(session.get("checkout_error")), "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/addon/remove")
async def addon_remove(request: Request):
    """Remove optional add-ons from the local Mock checkout bill."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.remove_addon(body.get("addon_id") or body.get("merchant_id"))
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/checkout/preview")
async def checkout_preview(request: Request):
    """Build local Mock checkout preview. Requires booking confirmation."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.preview_checkout()
        return {
            "ok": not bool(session.get("checkout_error")),
            "session": _safe_session(session),
            "checkout_preview": session.get("checkout_preview"),
            "message": (session.get("checkout_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/checkout/apply")
async def checkout_apply(request: Request):
    """Select a local Mock checkout strategy without real payment."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.apply_checkout(body.get("strategy_id"))
        return {
            "ok": not bool(session.get("checkout_error")),
            "session": _safe_session(session),
            "checkout_preview": session.get("checkout_preview"),
            "message": (session.get("checkout_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/checkout/pay")
async def checkout_pay(request: Request):
    """Create local Mock payment result only. No real payment/coupon/member API."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.pay_checkout(body.get("strategy_id"))
        return {
            "ok": not bool(session.get("checkout_error")),
            "session": _safe_session(session),
            "checkout_result": session.get("checkout_result"),
            "message": (session.get("checkout_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/checkout/split")
async def checkout_split(request: Request):
    """Create local Mock split-bill result. No real collection link."""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        session = ag.split_checkout(
            mode=body.get("mode") or "aa",
            members=body.get("members") or None,
            host=body.get("host") or "发起人",
            exempted_members=body.get("exempted_members") or None,
        )
        return {
            "ok": not bool(session.get("checkout_error")),
            "session": _safe_session(session),
            "checkout_split": session.get("checkout_split"),
            "message": (session.get("checkout_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/exception")
async def exception(request: Request):
    """注入异常并局部重排。"""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        exc_type = body.get("type", "")
        session = ag.inject_exception(exc_type, body.get("context") or {})
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/support")
async def support(request: Request):
    """Backward-compatible Mock support entry for one itinerary segment."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        session = ag.create_support_case(
            session_id=sid,
            issue_type=body.get("issue_type", "other"),
            segment_id=body.get("segment_id"),
            target_segment_index=body.get("target_segment_index"),
            source=body.get("source") or "selected_itinerary",
            user_message=body.get("message"),
        )
        return {"ok": not bool(session.get("support_error")), "session": _safe_session(session), "support_case": session.get("support_case")}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/support/create")
async def support_create(request: Request):
    """Create a local Mock support / aftersales case. No real service is called."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        session = ag.create_support_case(
            session_id=sid,
            issue_type=body.get("issue_type", "other"),
            segment_id=body.get("segment_id"),
            target_segment_index=body.get("target_segment_index"),
            source=body.get("source") or "selected_itinerary",
            user_message=body.get("message"),
        )
        return {
            "ok": not bool(session.get("support_error")),
            "session": _safe_session(session),
            "support_case": session.get("support_case"),
            "message": (session.get("support_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/support/{support_case_id}/reply")
async def support_reply(support_case_id: str, request: Request):
    """Append a user reply to a local Mock support case."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        session = ag.reply_support_case(support_case_id, body.get("message", ""))
        return {
            "ok": not bool(session.get("support_error")),
            "session": _safe_session(session),
            "support_case": session.get("support_case"),
            "message": (session.get("support_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/support/{support_case_id}/action")
async def support_action(support_case_id: str, request: Request):
    """Apply a local Mock support action. No real service is called."""
    try:
        body = await request.json()
        sid = _session_id(body, request)
        ag = _agent_for(sid)
        session = ag.apply_support_action(support_case_id, body.get("action_id", "keep_plan"))
        return {
            "ok": not bool(session.get("support_error")),
            "session": _safe_session(session),
            "support_case": session.get("support_case"),
            "message": (session.get("support_error") or {}).get("message", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.get("/support/{support_case_id}")
async def support_get(support_case_id: str, request: Request):
    """Read a local Mock support case within the current session."""
    try:
        sid = _session_id({}, request)
        ag = _agent_for(sid)
        case = ag.get_support_case(support_case_id)
        if not case:
            return {"ok": False, "message": "Mock support case not found in this session.", "support_case": None}
        return {"ok": True, "support_case": case}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/reject")
async def reject(request: Request):
    """用户主动拒绝一个商户，下次检索前剔除。"""
    try:
        body = await request.json()
        ag = _agent_for(_session_id(body, request))
        mid = body.get("merchant_id", "")
        session = ag.reject_merchant(mid)
        return {"ok": True, "session": _safe_session(session)}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/reset")
async def reset(request: Request):
    """新会话。"""
    body = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    sid = _session_id(body, request)
    AGENTS[sid] = Agent()
    return {"ok": True, "message": "已重置"}


# ─────────────────────────────────────────────────────────────────
# 多人投票接口
# ─────────────────────────────────────────────────────────────────
@app.post("/vote/create")
async def vote_create(request: Request):
    body = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    sid = _session_id(body, request)
    ag = _agent_for(sid)
    room = _create_vote_room(ag.session, session_id=sid, base_url=str(request.base_url).rstrip("/"))
    if not room:
        return {"ok": False, "message": "当前方案不足以创建投票房间"}
    return {"ok": True, "room": room}


@app.get("/vote/{room_id}")
async def vote_get(room_id: str):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return JSONResponse(status_code=200, content={"ok": False, "message": "未找到投票房间"})
    _sync_session_vote_room(room_id)
    return {"ok": True, "room": _public_vote_room(room)}


@app.post("/vote/{room_id}")
async def vote_submit(room_id: str, request: Request):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return JSONResponse(status_code=200, content={"ok": False, "message": "未找到投票房间"})
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=200, content={"ok": False, "message": "请求格式不正确"})
    option_id = str(body.get("option_id") or "")
    if not option_id and "plan_index" in body:
        option_id = f"plan_{body.get('plan_index')}"
    result = submit_vote(
        room,
        voter=body.get("voter") or "",
        option_id=option_id,
        feedback_text=body.get("feedback") or body.get("feedback_text") or "",
    )
    if not result.get("ok"):
        return {"ok": False, "message": result.get("message", "投票失败"), "room": _public_vote_room(room)}
    _sync_session_vote_room(room_id)
    return {"ok": True, "room": _public_vote_room(room), "feedback": result.get("feedback")}
    idx = str(body.get("plan_index", ""))
    voter = (body.get("voter") or f"friend-{len(room['voters']) + 1}").strip()
    if idx not in room["votes"]:
        return {"ok": False, "message": "方案不存在"}
    old = room["voters"].get(voter)
    if old is not None and str(old) in room["votes"]:
        room["votes"][str(old)] = max(0, room["votes"][str(old)] - 1)
    room["voters"][voter] = int(idx)
    room["votes"][idx] += 1
    _sync_session_vote_room(room_id)
    return {"ok": True, "room": _public_vote_room(room)}


@app.post("/vote/{room_id}/confirm")
async def vote_confirm(room_id: str, request: Request):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return JSONResponse(status_code=200, content={"ok": False, "message": "未找到投票房间"})
    try:
        body = await request.json()
    except Exception:
        body = {}
    summary = summarize_vote_room(room)
    if summary.get("requires_replan"):
        return {"ok": False, "message": "朋友反馈里有硬约束，请先局部修改方案", "room": _public_vote_room(room)}
    leading = summary.get("leading_option")
    if not leading:
        return {"ok": False, "message": "还没有可确认的领先选项", "room": _public_vote_room(room)}
    sid = room.get("session_id") or _session_id(body, request)
    ag = _agent_for(sid)
    plan_index = leading.get("plan_index")
    if plan_index is not None:
        session = ag.choose(int(plan_index))
    else:
        session = ag.session
        session["mode"] = "selected"
    room["confirmed_option"] = leading
    room["status"] = "confirmed_by_host"
    session["vote_decision"] = {"room_id": room_id, "confirmed_option": leading}
    _sync_session_vote_room(room_id)
    return {"ok": True, "room": _public_vote_room(room), "session": _safe_session(session)}


@app.post("/vote/{room_id}/resolve")
async def vote_resolve(room_id: str, request: Request):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return JSONResponse(status_code=200, content={"ok": False, "message": "未找到投票房间"})
    try:
        body = await request.json()
    except Exception:
        body = {}
    feedback = first_replan_feedback(room)
    if not feedback:
        return {"ok": False, "message": "没有需要局部重排的朋友反馈", "room": _public_vote_room(room)}
    sid = room.get("session_id") or _session_id(body, request)
    ag = _agent_for(sid)
    if not ag.session.get("chosen") and ag.session.get("plans"):
        ag.choose(int(room.get("plan_index") or 0))
    req = ag.session.get("request") or {}
    if feedback.get("constraint") == "no_spicy":
        diet = set(req.get("diet_limits") or [])
        diet.add("no_spicy")
        req["diet_limits"] = list(diet)
        flags = set(req.get("safety_flags") or [])
        flags.add("no_spicy")
        req["safety_flags"] = list(flags)
    if feedback.get("constraint") in ("played_before", "avoid_horror_newbie"):
        prefs = set(req.get("preferences") or [])
        prefs.add("newbie_friendly")
        prefs.add("easy_pace")
        req["preferences"] = list(prefs)
    exception_type, context = replan_context_from_feedback(room, feedback)
    session = ag.inject_exception(exception_type, context)
    room["resolution"] = session.get("exception_result")
    room["status"] = "resolved"
    room.setdefault("warnings", []).extend((session.get("exception_result") or {}).get("warnings") or [])
    _sync_session_vote_room(room_id)
    return {"ok": True, "room": _public_vote_room(room), "session": _safe_session(session)}


@app.get("/vote/{room_id}/page")
async def vote_page(room_id: str):
    room = VOTE_ROOMS.get(room_id)
    if not room:
        return HTMLResponse("<h1>投票房间不存在</h1>", status_code=404)
    buttons = "\n".join(
        f"<button onclick=\"vote({o['index']})\"><b>{o['title']}</b><span>{o['focus']} · ¥{o['cost']} · {round(o['minutes']/60,1)}h</span></button>"
        for o in room.get("options", [])
    )
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>美团周到 · 朋友投票</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:#f5f5f5;margin:0;padding:28px;color:#191919}}
.wrap{{max-width:520px;margin:0 auto}}h1{{font-size:24px;margin:0 0 8px}}p{{color:#666;margin:0 0 18px}}
button{{width:100%;border:1px solid #eee;background:#fff;border-radius:12px;padding:14px;margin:8px 0;text-align:left;font:inherit;box-shadow:0 4px 18px rgba(0,0,0,.06)}}
button:active{{background:#fff6d6}}button b{{display:block;font-size:16px}}button span{{display:block;color:#666;font-size:13px;margin-top:4px}}
.result{{background:#fff6d6;border:1px solid #ffe680;border-radius:12px;padding:12px;margin-top:14px;color:#5a4200}}
</style></head><body><div class="wrap">
<h1>这场周末局选哪个？</h1><p>投票截止：创建后 {room.get('deadline_minutes', 20)} 分钟。你可以重复投，后一次会覆盖前一次。</p>
<input id="voter" placeholder="你的名字" style="width:100%;padding:12px;border:1px solid #eee;border-radius:10px;margin-bottom:8px">
{buttons}<div class="result" id="result">还没人投票。</div></div>
<script>
async function vote(i){{
  const voter = document.getElementById('voter').value || '朋友';
  const r = await fetch('/vote/{room_id}', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{plan_index:i,voter}})}}).then(x=>x.json());
  render(r.room);
}}
async function refresh(){{
  const r = await fetch('/vote/{room_id}').then(x=>x.json());
  if(r.ok) render(r.room);
}}
function render(room){{
  const votes = room.votes || {{}};
  const winner = room.winner;
  document.getElementById('result').innerHTML =
    '当前票数：' + Object.entries(votes).map(([k,v])=>'方案 '+(Number(k)+1)+'：'+v+'票').join(' / ') +
    (winner ? '<br><b>当前领先：</b>' + winner.title + '（' + winner.votes + '票）' : '');
}}
refresh();
</script></body></html>"""
    return HTMLResponse(html)


# ─────────────────────────────────────────────────────────────────
# 后台接口（商户管理 / 广告出价）
# ─────────────────────────────────────────────────────────────────
@app.get("/merchants")
async def get_merchants():
    try:
        with open(MERCHANTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        reservations = _reservation_index()
        if reservations:
            for m in data:
                r = reservations.get(m.get("id"))
                if r:
                    m["reservation_status"] = r["status"]
                    m["reservation_preview"] = r["preview"]
                    m["reservation_detail"] = r
                else:
                    m.setdefault("reservation_status", "无预定")
        return {"ok": True, "data": data}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": f"商户数据不可用：{e}"})


ADMIN_ROLE_BY_CATEGORY = {
    "火锅": "EAT", "江浙菜": "EAT", "烧烤": "EAT", "海鲜": "EAT", "简餐": "EAT", "本地小吃": "EAT", "外卖": "STAYIN",
    "剧本杀": "PLAY", "电影院": "PLAY", "KTV": "PLAY", "台球": "PLAY", "密室": "PLAY", "桌游": "PLAY", "展览": "PLAY",
    "景区": "PLAY", "按摩": "PLAY", "酒店": "PLAY",
    "奶茶": "ADDON", "咖啡": "ADDON", "甜品": "ADDON", "冰淇淋": "ADDON", "蛋糕鲜花": "ADDON", "闪购零食": "ADDON", "酒吧": "ADDON",
}
ADMIN_IMAGE_BY_CATEGORY = {
    "火锅": "🍲", "江浙菜": "🥢", "烧烤": "🍖", "海鲜": "🦀", "简餐": "🍱", "本地小吃": "🥟", "外卖": "🥡",
    "剧本杀": "🎭", "电影院": "🎬", "KTV": "🎤", "台球": "🎱", "密室": "🕵️", "桌游": "🎲", "展览": "🖼️",
    "景区": "🏞️", "按摩": "💆", "酒店": "🏨", "奶茶": "🧋", "咖啡": "☕", "甜品": "🍰", "冰淇淋": "🍦",
    "蛋糕鲜花": "💐", "闪购零食": "🛒", "酒吧": "🍷",
}


def _admin_canonical_category(category: Any, name: str = "") -> str:
    cat = str(category or "").strip()
    if cat in {"citywalk", "Citywalk"}:
        return "景区"
    if cat:
        return cat
    if "剧本" in name or "打本" in name:
        return "剧本杀"
    if "火锅" in name:
        return "火锅"
    if "电影" in name or "影院" in name:
        return "电影院"
    if "奶茶" in name:
        return "奶茶"
    return "景区"


def _admin_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _admin_float(value: Any, default: float = 4.6) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _next_merchant_id(merchants: list[dict[str, Any]]) -> str:
    nums = []
    for m in merchants:
        raw = str(m.get("id", "")).replace("m_", "")
        if raw.isdigit():
            nums.append(int(raw))
    return f"m_{(max(nums) + 1 if nums else 1):04d}"


def _normalize_admin_merchant(body: dict[str, Any], merchants: list[dict[str, Any]]) -> dict[str, Any]:
    item = dict(body or {})
    name = str(item.get("name") or "").strip()
    category = _admin_canonical_category(item.get("category"), name)
    role = ADMIN_ROLE_BY_CATEGORY.get(category, item.get("slot_role") or "PLAY")
    price = _admin_int(item.get("price"), 100)
    if not item.get("id"):
        item["id"] = _next_merchant_id(merchants)
    item["name"] = name
    item["category"] = category
    item["slot_role"] = role
    item["area"] = str(item.get("area") or "新街口").strip()
    item["price"] = price
    item["duration_minutes"] = _admin_int(item.get("duration_minutes"), 90)
    item["rating"] = round(_admin_float(item.get("rating"), 4.6), 1)
    item["review_count"] = _admin_int(item.get("review_count"), 128)
    item["review_tags"] = item.get("review_tags") or [category, "本地 Mock"]
    item["review_snippet"] = item.get("review_snippet") or f"{category}体验稳定，适合周末安排。"
    item["features"] = item.get("features") or [category, "可预约", "本地 Mock"]
    item["image"] = item.get("image") or ADMIN_IMAGE_BY_CATEGORY.get(category, "🏫")
    item["open"] = item.get("open") or "10:00"
    item["close"] = item.get("close") or "22:00"
    item["can_reserve"] = bool(item.get("can_reserve", role != "STAYIN"))
    item["group_deal"] = item.get("group_deal") or {
        "title": f"{category}体验券",
        "price": max(1, round(price * 0.88)),
        "desc": "本地 Mock 券，不触发真实支付",
    }
    item["stock"] = _admin_int(item.get("stock"), 30)
    item["slots"] = item.get("slots") or ["10:00", "14:00", "18:00", "20:00"]
    item["queue_minutes"] = _admin_int(item.get("queue_minutes"), 0)
    item["ad_bid"] = _admin_int(item.get("ad_bid"), 0)
    item["suitable_scenes"] = item.get("suitable_scenes") or (["stay_in"] if role == "STAYIN" else ["friends_out"])
    item["flags"] = item.get("flags") or {"alcohol": category == "酒吧", "kid_friendly": category != "酒吧"}
    item["recommended_dishes"] = item.get("recommended_dishes") or [f"{category}招牌套餐"]
    item["coupons"] = item.get("coupons") or [
        {"id": f"{item['id']}_c1", "title": "到店团购券", "price": max(1, round(price * 0.85)), "desc": "本地 Mock 券，不触发真实支付"},
        {"id": f"{item['id']}_c2", "title": "满减优惠券", "price": max(1, round(price * 0.75)), "desc": "本地 Mock 券，不触发真实支付"},
    ]
    return item


@app.post("/merchants")
async def update_merchant(request: Request):
    try:
        body = await request.json()
        with open(MERCHANTS_PATH, "r", encoding="utf-8") as f:
            merchants = json.load(f)
        body = _normalize_admin_merchant(body, merchants)
        mid = body.get("id", "")
        if not body.get("name"):
            return JSONResponse(status_code=200, content={"ok": False, "message": "商户名称不能为空"})
        found = False
        for i, m in enumerate(merchants):
            if m.get("id") == mid:
                merchants[i] = body
                found = True
                break
        if not found:
            merchants.append(body)
        with open(MERCHANTS_PATH, "w", encoding="utf-8") as f:
            json.dump(merchants, f, ensure_ascii=False, indent=2)
        return {"ok": True, "message": f"商户 {mid} 已{'更新' if found else '新增'}"}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


@app.post("/merchants/ad_bid")
async def update_ad_bid(request: Request):
    """只调佣金旋钮 ad_bid 的便捷接口（后台拖动 slider 用）。"""
    try:
        body = await request.json()
        mid = body.get("id", "")
        bid = int(body.get("ad_bid", 0))
        with open(MERCHANTS_PATH, "r", encoding="utf-8") as f:
            merchants = json.load(f)
        ok = False
        for m in merchants:
            if m.get("id") == mid:
                m["ad_bid"] = bid
                ok = True
                break
        if ok:
            with open(MERCHANTS_PATH, "w", encoding="utf-8") as f:
                json.dump(merchants, f, ensure_ascii=False, indent=2)
        return {"ok": ok, "message": f"已设置 ad_bid={bid}" if ok else "未找到商户"}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})


# ─────────────────────────────────────────────────────────────────
# 静态页面
# ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(os.path.join(WEB_DIR, "app.html"))


@app.get("/admin")
async def admin():
    return FileResponse(os.path.join(WEB_DIR, "admin.html"))


@app.get("/health")
async def health():
    return {"ok": True, "service": "美团周到", "endpoints": [
        "POST /plan", "POST /refine", "POST /clarify", "POST /select", "POST /confirm", "POST /exception",
        "POST /booking/review", "POST /booking/update", "POST /booking/confirm",
        "POST /addon/accept", "POST /addon/remove",
        "POST /checkout/preview", "POST /checkout/apply", "POST /checkout/pay", "POST /checkout/split",
        "POST /support", "POST /support/create", "GET /support/{support_case_id}",
        "POST /support/{support_case_id}/reply", "POST /support/{support_case_id}/action",
        "POST /reject", "POST /reset",
        "POST /vote/create", "GET /vote/{room_id}", "POST /vote/{room_id}",
        "POST /vote/{room_id}/confirm", "POST /vote/{room_id}/resolve", "GET /vote/{room_id}/page",
        "GET /merchants", "POST /merchants", "POST /merchants/ad_bid",
        "GET /", "GET /admin",
    ]}


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print("════════════════════════════════════════════════")
    print("  美团周到 · 服务启动")
    print(f"  用户应用：http://127.0.0.1:{port}/")
    print(f"  平台后台：http://127.0.0.1:{port}/admin")
    print(f"  健康检查：http://127.0.0.1:{port}/health")
    print("════════════════════════════════════════════════")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
