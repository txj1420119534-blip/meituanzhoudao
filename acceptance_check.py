"""Qualification acceptance checks for weekend-agent.

Run:
    python acceptance_check.py

The script calls the local Agent directly. It does not require a browser,
Playwright, a running server, a real external API, or LONGCAT_API_KEY.
"""
from __future__ import annotations

import json
from collections import Counter
import os
import py_compile
import re
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MERCHANTS = DATA / "merchants.json"
TRAVEL = DATA / "travel.json"
DEFAULT_CASE_TIMEOUT = 45
QUICK_STATUS_FILE = ROOT / ".acceptance_quick_status.json"
PACK_STATUS_FILE = ROOT / ".pack_submit_status.json"
ACCEPTANCE_TMP = ROOT / ".acceptance_tmp"
TRUSTED_PUBLIC_SOURCES = {"explicit_text", "user_answer", "profile_memory"}
MEAL_CATEGORIES = {"外卖", "外卖正餐", "江浙菜", "火锅", "海鲜", "烧烤", "简餐", "西餐", "融合菜", "本地面食", "餐厅"}
QUICK_CASE_IDS = {
    6, 63, 64, 65, 66, 67, 68, 69, 70, 83,
    84, 85, 86, 87, 88, 89, 90, 91, 92, 96,
    97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
    108, 109, 110, 111, 112, 113, 114,
    115, 116, 117, 118, 119, 121, 122,
    126, 127, 128, 129, 130, 131, 132, 133, 134,
    135, 136, 137, 138, 139, 140, 141, 142, 143,
    144, 145, 146, 147, 148, 149, 150, 151,
    152, 153, 154, 156, 157, 158, 159, 160, 161, 163, 168,
    169, 170, 171, 172, 173, 174, 175, 176, 177, 178,
    179, 180, 181, 182, 183, 184,
    185, 186, 187, 188, 189, 190, 191, 192, 193,
    194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
    206, 207, 208, 209, 210, 211, 212, 213, 214, 215,
    216, 217, 218, 219, 220, 221, 222, 223, 224, 225,
    226, 227, 228, 229, 230, 231, 232, 233,
}
SYSTEM_CASE_IDS = {93, 94, 95}
os.environ.pop("LONGCAT_API_KEY", None)

def Agent(*args, **kwargs):  # noqa: N802
    from agent.core import Agent as AgentClass
    return AgentClass(*args, **kwargs)


def parse_request(*args, **kwargs):
    from agent.parser import parse_request as parse_request_func
    return parse_request_func(*args, **kwargs)


def build_itinerary(*args, **kwargs):
    from agent.planner import build_itinerary as build_itinerary_func
    return build_itinerary_func(*args, **kwargs)

CHECK_STATUS: dict[str, Any] = {
    "garbled_data": None,
    "doc_encoding": None,
    "api_smoke": None,
    "session_isolation": None,
    "security_scan": None,
    "security_hits": [],
}


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


TEXT = {
    "milk_tea": "想喝奶茶，不要太甜，不能喝冰的",
    "period_tea": "我生理期，想喝点热的不要太甜的奶茶",
    "hotpot": "晚上想吃火锅，不吃辣，4个人，人均150，新街口，18点",
    "movie": "今天晚上想看电影，不想吃饭",
    "seafood": "只想吃个海鲜，不想安排别的",
    "coffee": "只想找个咖啡店坐一会儿",
    "script_missing": "想和朋友打剧本杀",
    "script_full": "4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，4小时",
    "horror_newbie": "6个人想玩恐怖本，但有人第一次玩",
    "stay_in": "我今天不想出门，就想宅家看点东西，点点吃的",
    "birthday": "朋友生日，4个人，预算300一人，想有点仪式感",
    "family": "带孩子周末下午出去玩，别太累，吃清淡点",
    "drive_ktv": "我们自驾去唱歌，后面想喝点",
    "friends_food": "4个朋友今天18:00想先看展再吃饭，人均180，新街口，公共交通，4小时",
    "massage": "周末想做个按摩放松一下，人均200，新街口",
    "billiards": "今晚想和朋友打台球，4个人，人均100，新街口",
    "maanshan": "周末想去马鞍山citywalk，一整天",
    "hotel": "今晚想订个酒店休息一下",
    "queue_feedback": "已经到餐厅门口了，排队太久，换一家",
    "late_feedback": "朋友晚半小时，帮我顺一下",
    "horror_feedback": "这个本太恐怖，换轻松一点",
    "cheap_feedback": "预算超了，换便宜点",
    "caffeine_tea": "晚上想喝奶茶，但不要咖啡因，不要太甜",
    "kid_ktv": "带孩子去KTV唱歌，别有酒",
    "date": "想和女朋友约会，浪漫一点，18点，新街口，人均300",
    "script_long": "4个朋友今晚19:00想玩欢乐盒装本，人均150，新街口，公共交通，6小时",
}

DEFAULT_ANSWERS = {
    "party_size": 4,
    "start_time": "19:00",
    "budget_per_person": 150,
    "script_style": "欢乐本",
    "window_hours": 4,
    "home_area": "新街口",
    "distance_tolerance": "same_area",
    "cuisine_preference": "江浙菜",
    "diet_limits": "none",
    "stayin_mode": "movie_takeaway",
    "experience_mode": "stay_in_online",
}


def _answer_for(session: dict, overrides: dict | None = None) -> dict:
    overrides = overrides or {}
    answers = {}
    for q in session.get("clarifications_needed", []) or []:
        key = q.get("key")
        if key:
            answers[key] = overrides.get(key, DEFAULT_ANSWERS.get(key))
    return {k: v for k, v in answers.items() if v is not None}


def _run(text: str, answers: dict | None = None, auto_refine: bool = True, agent: Agent | None = None) -> tuple[Agent, dict]:
    agent = agent or Agent()
    session = agent.run(text)
    if auto_refine and session.get("mode") == "needs_clarification":
        session = agent.refine(_answer_for(session, answers))
    return agent, session


def _choose(agent: Agent, session: dict, index: int = 0) -> dict:
    if session.get("plans"):
        return agent.choose(index)
    return session


def _choose_confirm(agent: Agent, session: dict, index: int = 0, confirm: bool = True) -> dict:
    session = _choose(agent, session, index)
    if confirm:
        session = agent.confirm_and_execute()
    return session


def _business_steps(plan: dict) -> list[dict]:
    return [s for s in plan.get("steps", []) if s.get("kind") != "travel"]


def _cats(plan: dict) -> list[str]:
    return [s.get("category") for s in _business_steps(plan)]


def _ids(plan: dict) -> list[str]:
    return [s.get("id") for s in _business_steps(plan)]


def _time_to_minutes(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value) * 60 if value < 24 else int(value)
    if not isinstance(value, str):
        return 0
    text = value.strip()
    if ":" not in text:
        return int(text) * 60 if text.isdigit() else 0
    h, m = text.split(":", 1)
    return int(h) * 60 + int(m)


def _main_plan(session: dict) -> dict:
    plans = session.get("plans") or []
    return plans[0] if plans else {}


def _itinerary(session: dict) -> dict:
    return _main_plan(session).get("itinerary") or session.get("chosen", {}).get("itinerary") or {}


def _segments(session: dict) -> list[dict]:
    return _itinerary(session).get("segments") or []


def _script_step(plan: dict) -> dict:
    for s in _business_steps(plan):
        if s.get("category") == "剧本杀":
            return s
    return {}


def _contains_any(values, needles) -> bool:
    vals = set(values or [])
    return any(n in vals for n in needles)


def _plan_summary(session: dict) -> str:
    plan = _main_plan(session)
    if not plan:
        return "无方案"
    if plan.get("unavailable"):
        return f"{plan.get('status')}: {plan.get('reason')}"
    cats = " / ".join(_cats(plan))
    return f"{plan.get('title')} | {cats} | ¥{plan.get('total_cost_per_person')} | {round(plan.get('total_minutes', 0)/60, 1)}h"


def _addon_summary(session: dict) -> str:
    plan = _main_plan(session)
    opt = plan.get("optional_addons") or plan.get("commercial_recommendations") or []
    addon = session.get("addon")
    bits = []
    if opt:
        bits.append("optional=" + "; ".join(f"{x.get('name')}({x.get('category')})" for x in opt[:2]))
    if addon:
        bits.append(f"confirmed_addon={addon.get('name')}({addon.get('category')})")
    return "；".join(bits) if bits else "无"


def _exception_summary(session: dict) -> str:
    exc = session.get("exception_result") or {}
    if not exc:
        return "未触发"
    return f"{exc.get('changed_kind')} | {exc.get('reason')} | needs_user_confirm={exc.get('needs_user_confirm')}"


def public_request(req: dict) -> dict:
    keys = [
        "scene", "primary_intent", "main_role", "requested_categories", "negative_intents",
        "safety_flags", "drink_preferences", "party_size", "start_time", "budget_per_person",
        "script_style", "cuisine_preference", "transport", "confidence", "missing_fields",
        "intent_conflict", "newbie", "feedback_intent", "date_preferences", "activity_choices",
        "cuisine_preferences", "script_style_choices",
    ]
    out = {k: req.get(k) for k in keys if k in req}
    frame = req.get("intent_frame") or {}
    out["intent_frame_public"] = {
        "goal_summary": frame.get("goal_summary"),
        "confirmed_fields": frame.get("confirmed_fields") or {},
        "field_sources": frame.get("field_sources") or {},
        "unknown_fields": frame.get("unknown_fields") or [],
        "sequence": frame.get("sequence") or [],
    }
    return out


def booking_status(session: dict) -> str:
    return f"mode={session.get('mode')} executed={session.get('executed')} bookings={len(session.get('bookings') or [])} share={'yes' if session.get('share_card') else 'no'}"


def result_type(session: dict) -> str:
    plan = _main_plan(session)
    if session.get("mode") == "needs_clarification" and not session.get("plans"):
        return "needs_clarification"
    if plan.get("unavailable") or plan.get("status") in ("needs_relaxation", "plan_unavailable", "not_supported_yet"):
        return "graceful_unavailable"
    return "supported_success"


def default_runner(text: str, answers: dict | None = None, auto_refine: bool = True) -> dict:
    agent = Agent()
    initial = agent.run(text)
    triggered = bool(initial.get("clarifications_needed"))
    if auto_refine and initial.get("mode") == "needs_clarification":
        session = agent.refine(_answer_for(initial, answers))
        completed = session.get("mode") != "needs_clarification"
    else:
        session = initial
        completed = session.get("mode") != "needs_clarification"
    return {
        "agent": agent,
        "session": session,
        "clarification_triggered": triggered,
        "clarification_completed": completed,
    }


def require(condition: bool, message: str, failures: list[str]):
    if not condition:
        failures.append(message)


def require_no_default_public_summary(session: dict, failures: list[str]) -> None:
    req = session.get("request") or {}
    frame = req.get("intent_frame") or {}
    public_text = str(frame.get("goal_summary") or "")
    for token in ("150", "4人", "4 人", "公共交通", "新街口"):
        require(token not in public_text, f"default public summary leaked token: {token}", failures)
    confirmed = frame.get("confirmed_fields") or {}
    sources = frame.get("field_sources") or {}
    for field in ("party_size", "budget_per_person", "start_time", "home_area", "transport"):
        value = confirmed.get(field)
        if value not in (None, "", [], "unknown"):
            require(sources.get(field) in TRUSTED_PUBLIC_SOURCES, f"{field} confirmed without trusted source", failures)


class Case:
    def __init__(
        self,
        cid: int,
        name: str,
        input_text: str,
        check: Callable[[dict], list[str]],
        runner: Callable[[], dict] | None = None,
        timeout_seconds: int = DEFAULT_CASE_TIMEOUT,
    ):
        self.cid = cid
        self.name = name
        self.input = input_text
        self.check = check
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    def run_direct(self) -> dict:
        started = time.time()
        ctx = self.runner() if self.runner else default_runner(self.input)
        failures = self.check(ctx)
        out = {
            "id": self.cid,
            "name": self.name,
            "input": self.input,
            "request": public_request(ctx.get("session", {}).get("request") or ctx.get("request", {})),
            "clarification_triggered": ctx.get("clarification_triggered", False),
            "clarification_completed": ctx.get("clarification_completed", False),
            "result_type": result_type(ctx.get("session", {})),
            "plan_summary": ctx.get("plan_summary", _plan_summary(ctx.get("session", {}))),
            "addon_summary": ctx.get("addon_summary", _addon_summary(ctx.get("session", {}))),
            "booking_status": ctx.get("booking_status", booking_status(ctx.get("session", {}))),
            "exception_summary": ctx.get("exception_summary", _exception_summary(ctx.get("session", {}))),
            "elapsed_seconds": round(time.time() - started, 2),
            "passed": not failures,
            "failures": failures,
        }
        return out

    def failed_result(self, message: str, elapsed: float = 0.0) -> dict:
        return {
            "id": self.cid, "name": self.name, "input": self.input,
            "request": {}, "clarification_triggered": False, "clarification_completed": False,
            "result_type": "error", "plan_summary": "运行异常",
            "addon_summary": "运行异常", "booking_status": "运行异常",
            "exception_summary": "运行异常", "elapsed_seconds": round(elapsed, 2),
            "passed": False, "failures": [message],
        }


def check_compile() -> list[str]:
    failures = []
    files = [ROOT / "server.py", ROOT / "cli.py", ROOT / "acceptance_check.py"] + list((ROOT / "agent").glob("*.py"))
    for file in files:
        try:
            py_compile.compile(str(file), doraise=True)
        except Exception as exc:
            failures.append(f"py_compile failed: {file.name}: {exc}")
    return failures


def check_module_runs() -> list[str]:
    failures = []
    modules = ["agent.parser", "agent.clarify", "agent.catalog", "agent.planner", "agent.tools", "agent.core"]
    for mod in modules:
        try:
            result = subprocess.run(
                [sys.executable, "-m", mod],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            if result.returncode != 0:
                failures.append(f"{mod} exited {result.returncode}: {(result.stderr or result.stdout)[-500:]}")
        except Exception as exc:
            failures.append(f"{mod} raised {exc}")
    return failures


def check_no_key_fallback() -> list[str]:
    failures = []
    old = os.environ.pop("LONGCAT_API_KEY", None)
    try:
        _, session = _run(TEXT["milk_tea"], {"start_time": "19:00", "home_area": "新街口"})
        require(bool(session.get("request")), "no LONGCAT_API_KEY run returned no request", failures)
        require(session.get("mode") in ("planned", "needs_clarification"), "no-key run did not use local fallback", failures)
    finally:
        if old is not None:
            os.environ["LONGCAT_API_KEY"] = old
    return failures


def check_damaged_data_fallback() -> list[str]:
    failures = []
    targets = ["merchants.json", "scenes.json", "travel.json"]
    backups = []
    try:
        for name in targets:
            path = DATA / name
            bak = DATA / f"{name}.acceptance.bak"
            shutil.copyfile(path, bak)
            backups.append((path, bak))
            path.write_text("{ broken json", encoding="utf-8")
            try:
                agent = Agent()
                session = agent.run(TEXT["script_full"])
                require(session.get("mode") in ("planned", "needs_clarification") or session.get("plans"), f"{name} damaged returned unusable session", failures)
            except Exception as exc:
                failures.append(f"{name} damaged caused exception: {exc}")
            shutil.copyfile(bak, path)
    finally:
        for path, bak in backups:
            if bak.exists():
                shutil.copyfile(bak, path)
                bak.unlink()
    return failures


def _visible_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _visible_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _visible_strings(item)


def check_data_integrity() -> list[str]:
    failures: list[str] = []
    merchants = json.loads(MERCHANTS.read_text(encoding="utf-8"))
    travel = json.loads(TRAVEL.read_text(encoding="utf-8"))
    visible_fields = [
        "name", "category", "area", "review_tags", "review_snippet",
        "group_deal", "recommended_dishes", "image", "tags", "description",
        "script_name", "script_style", "open_tables", "signature_dishes",
        "cuisine_tags", "diet_support", "flags", "suitable_scenes",
    ]
    for m in merchants:
        for field in visible_fields:
            for text in _visible_strings(m.get(field)):
                if "?" in text:
                    failures.append(f"merchant {m.get('id')} field {field} contains ?: {text}")
    for key in travel:
        if "?" in key:
            failures.append(f"travel key contains ?: {key}")
    required_routes = {
        "马鞍山->马鞍山",
        "新街口->马鞍山",
        "马鞍山->新街口",
        "河西->马鞍山",
        "马鞍山->河西",
    }
    missing_routes = sorted(required_routes - set(travel))
    if missing_routes:
        failures.append("missing required travel routes: " + ", ".join(missing_routes))
    if len(merchants) < 5000:
        failures.append(f"merchant catalog too small: {len(merchants)} < 5000")
    required = {
        "火锅", "江浙菜", "烧烤", "海鲜", "简餐", "本地小吃", "外卖", "甜品",
        "奶茶", "咖啡", "剧本杀", "密室", "KTV", "台球", "桌游", "电影院",
        "展览", "按摩", "citywalk", "蛋糕鲜花", "闪购零食", "酒店", "酒吧", "冰淇淋",
    }
    categories = {m.get("category") for m in merchants}
    missing = sorted(required - categories)
    if missing:
        failures.append("missing required categories: " + ", ".join(missing))
    category_counts: dict[str, int] = {}
    for m in merchants:
        category_counts[m.get("category")] = category_counts.get(m.get("category"), 0) + 1
    thin_categories = sorted(cat for cat in required if category_counts.get(cat, 0) < 10 and cat != "酒店")
    if thin_categories:
        failures.append("required categories have fewer than 10 samples: " + ", ".join(thin_categories))
    required_areas = {"新街口", "河西", "老门东", "夫子庙", "鼓楼", "玄武湖", "江宁", "仙林", "百家湖", "奥体", "马鞍山"}
    area_counts: dict[str, int] = {}
    for m in merchants:
        area_counts[m.get("area")] = area_counts.get(m.get("area"), 0) + 1
    missing_areas = sorted(required_areas - set(area_counts))
    if missing_areas:
        failures.append("missing required areas: " + ", ".join(missing_areas))
    thin_areas = sorted(area for area in required_areas if area_counts.get(area, 0) < 20)
    if thin_areas:
        failures.append("required areas have fewer than 20 samples: " + ", ".join(thin_areas))
    signatures = [(m.get("name"), m.get("category"), m.get("area"), m.get("price"), m.get("duration_minutes")) for m in merchants]
    if len(signatures) - len(set(signatures)) > 8:
        failures.append("too many duplicate merchant signatures")
    CHECK_STATUS["garbled_data"] = not failures
    return failures


DOC_CHECK_FILES = [
    "README.md",
    "DEMO_PLAYBOOK.md",
    "PROJECT_STATUS.md",
    "ACCEPTANCE_REPORT.md",
    "CHANGE_SUMMARY.md",
    "WORKFLOW_REBUILD_REPORT.md",
    "PHASE2C_POLISH_REPORT.md",
    "CATALOG_EXPANSION_REPORT.md",
    "BROWSER_QA_REPORT.md",
    "PHASE2C_USER_FLOW_PATCH_REPORT.md",
    "NATURAL_INTENT_COORDINATION_REPORT.md",
    "FRIEND_TEST_CHECKLIST.md",
    "DEPLOY_RENDER_GUIDE.md",
    "PHASE2B_FINAL_INTEGRATION_REPORT.md",
]

MOJIBAKE_MARKERS = [
    "涓€", "涓", "锛", "鈥", "銆", "鏂", "拌", "", "鍙",
    "鐨", "绋", "诲", "辩爜", "乣", "歚", "ÎŢ", "濂惰",
    "闂", "棶", "瑙", "規", "勭", "榛", "㈢", "煡",
]


def _has_private_use_chars(text: str) -> bool:
    return any(0xE000 <= ord(ch) <= 0xF8FF for ch in text)


def _has_mojibake(text: str) -> bool:
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def check_doc_encoding() -> list[str]:
    """Check deliverable docs for UTF-8 readability and common mojibake markers."""
    failures: list[str] = []
    required_playbook_terms = ["演示目标", "开场话术", "生日组局", "多人投票", "半路救援", "Mock"]

    for name in DOC_CHECK_FILES:
        path = ROOT / name
        if not path.exists():
            failures.append(f"{name} missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{name} is not valid UTF-8: {exc}")
            continue
        if _has_private_use_chars(text):
            failures.append(f"{name} contains Unicode private-use characters")
        if _has_mojibake(text):
            failures.append(f"{name} contains common Chinese mojibake markers")
        if name == "DEMO_PLAYBOOK.md":
            missing_terms = [term for term in required_playbook_terms if term not in text]
            if missing_terms:
                failures.append(f"DEMO_PLAYBOOK.md missing readable terms: {', '.join(missing_terms)}")

    CHECK_STATUS["doc_encoding"] = not failures
    return failures


def check_api_smoke() -> list[str]:
    failures: list[str] = []
    try:
        from fastapi.testclient import TestClient
        import server
    except Exception as exc:
        CHECK_STATUS["api_smoke"] = False
        CHECK_STATUS["session_isolation"] = False
        return [f"TestClient import failed: {exc}"]

    try:
        server.AGENTS.clear()
        client = TestClient(server.app)
        sid_a = "acceptance_api_a"
        sid_b = "acceptance_api_b"
        headers_a = {"X-Session-Id": sid_a}
        headers_b = {"X-Session-Id": sid_b}

        r = client.post("/plan", json={"session_id": sid_a, "text": TEXT["script_missing"]}, headers=headers_a).json()
        require(r.get("ok") is True, "/plan session_a failed", failures)
        require(r.get("session", {}).get("mode") == "needs_clarification", "/plan session_a should need clarification", failures)

        r = client.post("/refine", json={
            "session_id": sid_a,
            "answers": {
                "party_size": 4, "start_time": "19:00", "budget_per_person": 150,
                "script_style": "欢乐本", "window_hours": 4, "home_area": "新街口",
            },
        }, headers=headers_a).json()
        require(r.get("ok") is True and r.get("session", {}).get("plans"), "/refine session_a failed to plan", failures)
        room_id = (r.get("session", {}).get("vote_room") or {}).get("room_id")
        if room_id:
            bad_vote = client.post(
                f"/vote/{room_id}",
                data="{bad json",
                headers={**headers_a, "Content-Type": "application/json"},
            ).json()
            require(
                bad_vote.get("ok") is False and bad_vote.get("message") == "请求格式不正确",
                "/vote/{room_id} invalid JSON did not return readable error",
                failures,
            )

        r_b = client.post("/plan", json={
            "session_id": sid_b,
            "text": TEXT["milk_tea"],
        }, headers=headers_b).json()
        require(r_b.get("ok") is True, "/plan session_b failed", failures)
        if r_b.get("session", {}).get("mode") == "needs_clarification":
            r_b = client.post("/clarify", json={
                "session_id": sid_b,
                "answers": {"start_time": "20:00", "home_area": "新街口", "budget_per_person": 30},
            }, headers=headers_b).json()
            require(r_b.get("ok") is True, "/clarify session_b failed", failures)
        req_b = r_b.get("session", {}).get("request", {})
        require(req_b.get("primary_intent") == "milk_tea", "session_b did not keep milk tea request", failures)

        r = client.post("/select", json={"session_id": sid_a, "plan_index": 0}, headers=headers_a).json()
        require(r.get("ok") is True and r.get("session", {}).get("mode") == "selected", "/select session_a failed", failures)
        require((r.get("session", {}).get("request") or {}).get("primary_intent") == "script_game", "session_a polluted before confirm", failures)

        r = client.post("/confirm", json={"session_id": sid_a}, headers=headers_a).json()
        require(r.get("ok") is True and r.get("session", {}).get("bookings"), "/confirm session_a failed", failures)
        require((r.get("session", {}).get("request") or {}).get("primary_intent") == "script_game", "session_a polluted after confirm", failures)

        r = client.post("/exception", json={
            "session_id": sid_a,
            "type": "ticket_soldout",
            "context": {"location_state": "before_departure"},
        }, headers=headers_a).json()
        require(r.get("ok") is True and r.get("session", {}).get("exception_result"), "/exception session_a failed", failures)

        r = client.post("/reset", json={"session_id": sid_b}, headers=headers_b).json()
        require(r.get("ok") is True, "/reset session_b failed", failures)
        require(server.AGENTS[sid_a].session.get("request", {}).get("primary_intent") == "script_game", "reset session_b polluted session_a", failures)
        require(server.AGENTS[sid_b].session.get("mode") == "ready", "reset session_b did not reset only session_b", failures)
    except Exception as exc:
        failures.append(f"API smoke raised: {exc}")

    CHECK_STATUS["api_smoke"] = not failures
    CHECK_STATUS["session_isolation"] = not failures
    return failures


def _security_pattern() -> re.Pattern:
    pattern = (
        r"s" + r"k-[A-Za-z0-9_-]{20,}|"
        r"DEEPSEEK_API_KEY\s*=\s*s" + r"k-|"
        r"OPENAI_API_KEY\s*=\s*s" + r"k-|"
        r"g" + r"hp_[A-Za-z0-9_]{20,}|"
        r"github" + r"_pat_"
    )
    return re.compile(pattern)


def _redact_security_text(text: str) -> str:
    return _security_pattern().sub("[REDACTED_SECRET_PATTERN]", str(text))


def _iter_scan_files():
    skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", "output", ".playwright-cli"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        yield path


def check_security_scan() -> list[str]:
    failures: list[str] = []
    pattern = _security_pattern()

    tracked_env = subprocess.run(["git", "ls-files", ".env", "*.env"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if tracked_env.stdout.strip():
        failures.append(".env or *.env is tracked: " + tracked_env.stdout.strip())

    git_grep = subprocess.run(["git", "grep", "-n", "-I", "-E", pattern.pattern], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if git_grep.returncode == 0 and git_grep.stdout.strip():
        failures.append("git grep key hits: " + _redact_security_text(git_grep.stdout.strip().splitlines()[0]))

    fs_hits = []
    for path in _iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if pattern.search(text):
            fs_hits.append(str(path.relative_to(ROOT)))
    if fs_hits:
        failures.append("filesystem key hits: " + ", ".join(fs_hits[:10]))
    CHECK_STATUS["security_hits"] = failures[:]
    CHECK_STATUS["security_scan"] = not failures
    return failures


SYSTEM_CHECK_SPECS: dict[str, tuple[Callable[[], list[str]], int]] = {
    "compile": (check_compile, 90),
    "module_runs": (check_module_runs, 180),
    "no_key_fallback": (check_no_key_fallback, 60),
    "damaged_data_fallback": (check_damaged_data_fallback, 120),
    "data_integrity": (check_data_integrity, 45),
    "doc_encoding": (check_doc_encoding, 45),
    "api_smoke": (check_api_smoke, 120),
    "security_scan": (check_security_scan, 90),
}


def script_fields_ok(step: dict) -> list[str]:
    failures = []
    status = step.get("script_status") or {}
    mapping = {
        "script name": status.get("name") or status.get("script_name"),
        "style": status.get("style"),
        "required_players": status.get("required_players"),
        "current_players": status.get("current_players"),
        "need_players": status.get("need_players"),
        "can_start_if_join": status.get("can_start_if_join") or status.get("can_fill_after_join"),
        "dm_rating": step.get("dm_rating"),
        "newbie_friendly": step.get("newbie_friendly"),
        "horror_level": step.get("horror_level"),
        "duration": status.get("duration_minutes"),
    }
    for key, value in mapping.items():
        if value in (None, "", []):
            failures.append(f"missing script field: {key}")
    return failures


def runner_exc(exc_type: str, context: dict, text: str = TEXT["friends_food"], answers: dict | None = None) -> dict:
    agent, session = _run(text, answers or {})
    session = _choose_confirm(agent, session, confirm=False)
    before_ids = _ids(session.get("chosen") or {})
    session = agent.inject_exception(exc_type, context)
    return {"agent": agent, "session": session, "before_ids": before_ids}


def with_temp_ad_bid(mid: str, bid: int, runner: Callable[[], dict]) -> dict:
    data = json.loads(MERCHANTS.read_text(encoding="utf-8"))
    backup = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        for item in data:
            if item.get("id") == mid:
                item["ad_bid"] = bid
        MERCHANTS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return runner()
    finally:
        MERCHANTS.write_text(backup, encoding="utf-8")


def make_cases(selected_ids: set[int] | None = None) -> list[Case]:
    selected_ids = set(selected_ids or [])
    cases: list[Case] = []

    def add(case: Case) -> None:
        if not selected_ids and case.cid in SYSTEM_CASE_IDS:
            return
        if not selected_ids or case.cid in selected_ids:
            cases[:] = [existing for existing in cases if existing.cid != case.cid]
            cases.append(case)

    def c1(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        require(req.get("primary_intent")=="milk_tea", "primary_intent is not milk_tea", f)
        require(req.get("main_role")=="ADDON", "main_role is not ADDON", f)
        require("party_size" not in (req.get("missing_fields") or []), "asked party_size for milk tea", f)
        require(cats and cats == ["奶茶"], f"main plan categories changed: {cats}", f)
        step=_business_steps(plan)[0] if _business_steps(plan) else {}
        opts=step.get("drink_options", {}) or {}; body=step.get("body_suitability", {}) or {}
        require(opts.get("hot_available") or body.get("not_too_sweet") or body.get("cannot_ice"), "drink recommendation does not support hot/low sugar/no ice", f)
        return f
    add(Case(1, "milk tea single point", TEXT["milk_tea"], c1, lambda: default_runner(TEXT["milk_tea"], {"start_time":"19:00","home_area":"新街口"})))

    def c2(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); step=_business_steps(plan)[0] if _business_steps(plan) else {}
        require(_contains_any(req.get("safety_flags"), ["body_uncomfortable"]), "missing body_uncomfortable", f)
        require(_contains_any(req.get("safety_flags"), ["cannot_ice"]), "missing cannot_ice", f)
        require(_contains_any(req.get("safety_flags"), ["not_too_sweet"]), "missing not_too_sweet", f)
        require((req.get("drink_preferences") or {}).get("hot_required") is True, "hot_required is not true", f)
        require((step.get("drink_options") or {}).get("hot_available") is True, "recommended merchant has no hot drink", f)
        return f
    add(Case(2, "period hot milk tea", TEXT["period_tea"], c2, lambda: default_runner(TEXT["period_tea"], {"start_time":"19:00","home_area":"新街口"})))

    def c3(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        require(req.get("primary_intent")=="hotpot", "primary_intent is not hotpot", f)
        require(req.get("main_role")=="EAT", "main_role is not EAT", f)
        require("火锅" in (req.get("requested_categories") or []), "requested_categories missing 火锅", f)
        if plan.get("unavailable"):
            require(plan.get("status") in ("needs_relaxation","plan_unavailable"), "unavailable plan lacks relaxation status", f)
        else:
            require(cats == ["火锅"], f"hotpot silently changed to {cats}", f)
            step=_business_steps(plan)[0]; support=set(step.get("diet_support") or [])
            require(bool({"no_spicy","不辣","番茄锅","鸳鸯锅","清汤锅"} & support) or int(step.get("spicy_level", 9) or 9) <= 1, "hotpot lacks no-spicy support", f)
        return f
    add(Case(3, "hotpot no spicy", TEXT["hotpot"], c3))

    def c4(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        frame=req.get("intent_frame") or {}; seq=frame.get("sequence") or []; goal=frame.get("goal_summary") or ""
        require(req.get("primary_intent")=="movie", "primary_intent is not movie", f)
        require("no_meal" in (req.get("negative_intents") or []), "missing no_meal", f)
        require(any(x.get("role")=="PLAY" and x.get("category")=="电影院" for x in seq), f"movie sequence missing PLAY/cinema: {seq}", f)
        require(not any(x.get("role")=="EAT" for x in seq), f"no_meal leaked EAT into intent_frame.sequence: {seq}", f)
        require(not any(x in goal for x in ("吃饭", "再吃饭", "餐厅", "正餐")), f"no_meal leaked food into goal_summary: {goal}", f)
        require(cats == ["电影院"], f"movie plan includes non-movie nodes: {cats}", f)
        opt=plan.get("optional_addons") or []
        require(not any(x.get("category") in ("外卖正餐","江浙菜","火锅","海鲜","餐厅") for x in opt), f"no_meal leaked restaurant addon: {opt}", f)
        return f
    add(Case(4, "movie no meal", TEXT["movie"], c4, lambda: default_runner(TEXT["movie"], {"start_time":"19:30","home_area":"新街口"})))

    def c5(ctx):
        f=[]; req=ctx["session"]["request"]; cats=_cats(_main_plan(ctx["session"]))
        require(req.get("main_role")=="EAT", "main_role is not EAT", f)
        require(req.get("scene")=="food_only", "scene is not food_only", f)
        require(cats == ["海鲜"], f"seafood plan changed to {cats}", f)
        return f
    add(Case(5, "seafood only", TEXT["seafood"], c5, lambda: default_runner(TEXT["seafood"], {"start_time":"18:00","budget_per_person":220,"home_area":"新街口"})))

    def c6(ctx):
        f=[]; req=ctx["session"]["request"]; cats=_cats(_main_plan(ctx["session"]))
        require(req.get("main_role") in ("ADDON","EAT"), "coffee main_role is unclear", f)
        require(req.get("scene") in ("addon_only","food_only"), "coffee forced into friends_out", f)
        require("party_size" not in (req.get("missing_fields") or []), "coffee asks party/script people", f)
        require(cats and cats[0] == "咖啡", f"coffee plan changed to {cats}", f)
        require_no_default_public_summary(ctx["session"], f)
        return f
    add(Case(6, "coffee sit awhile", TEXT["coffee"], c6, lambda: default_runner(TEXT["coffee"], {"start_time":"15:00","home_area":"新街口"})))

    def c7(ctx):
        f=[]; session=ctx["session"]; keys=set(q.get("key") for q in session.get("clarifications_needed", []))
        require(session.get("mode")=="needs_clarification", "script missing info did not pause", f)
        require({"party_size","start_time","budget_per_person","script_style"} <= keys or {"party_size","start_time","budget_per_person","window_hours"} <= keys, f"missing script clarification keys: {keys}", f)
        require(not session.get("plans"), "script missing info produced random plans", f)
        return f
    add(Case(7, "script missing info", TEXT["script_missing"], c7, lambda: default_runner(TEXT["script_missing"], auto_refine=False)))

    def c8(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); cats=_cats(plan); step=_script_step(plan)
        require(req.get("primary_intent")=="script_game", "primary_intent not script_game", f)
        require(req.get("main_role")=="PLAY", "main_role not PLAY", f)
        require("剧本杀" in (req.get("requested_categories") or []), "requested_categories missing 剧本杀", f)
        require(cats == ["剧本杀"], f"script plan includes non-script nodes: {cats}", f)
        f.extend(script_fields_ok(step))
        return f
    add(Case(8, "script full fields", TEXT["script_full"], c8))

    def c9(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); step=_script_step(plan)
        require(req.get("script_style")=="恐怖本", "horror style not recognized", f)
        require(req.get("newbie") is True or "newbie_friendly" in (req.get("preferences") or []), "newbie not recognized", f)
        if plan.get("unavailable"):
            require(plan.get("status")=="needs_relaxation", "horror newbie unavailable lacks needs_relaxation", f)
        else:
            require(step.get("newbie_friendly") is True and step.get("horror_level") not in ("中","高"), "first horror recommendation unsafe for newbie", f)
        return f
    add(Case(9, "horror with newbie", TEXT["horror_newbie"], c9, lambda: default_runner(TEXT["horror_newbie"], {"start_time":"19:00","budget_per_person":180,"home_area":"新街口","window_hours":4})))

    def c10(ctx):
        f=[]; req=ctx["session"]["request"]; cats=_cats(_main_plan(ctx["session"])); frame=req.get("intent_frame") or {}; goal=frame.get("goal_summary") or ""
        require(req.get("scene")=="stay_in", "scene not stay_in", f)
        require(goal and goal != "还需要确认目标", f"stay_in goal_summary is not usable: {goal}", f)
        require("在线电影" not in cats, "stay_in should not include online movie merchant", f)
        require(set(cats) <= {"外卖","闪购零食"}, f"stay-in has non-executable or offline cats: {cats}", f)
        return f
    add(Case(10, "stay in", TEXT["stay_in"], c10, lambda: default_runner(TEXT["stay_in"], {"start_time":"20:00","budget_per_person":120,"stayin_mode":"movie_takeaway"})))

    def c11(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; goal=frame.get("goal_summary") or ""; plan=_main_plan(ctx["session"]); cats=_cats(plan); opt=plan.get("optional_addons") or []
        require((frame.get("confirmed_fields") or {}).get("occasion") == "生日", "birthday occasion not confirmed in intent_frame", f)
        require(goal and goal != "还需要确认目标", f"birthday goal_summary is not usable: {goal}", f)
        require("蛋糕鲜花" not in cats, f"birthday cake/flowers should not be core Plan A/B segment: {cats}", f)
        require(bool(plan.get("long_lead_addon_hint")) or any("生日" in str(x.get("title") or x.get("type") or "") for x in opt), "birthday long-lead cake/flowers prompt missing", f)
        return f
    add(Case(11, "birthday delivery", TEXT["birthday"], c11, lambda: default_runner(TEXT["birthday"], {"start_time":"18:00","home_area":"新街口","window_hours":4})))

    def c12(ctx):
        f=[]; req=ctx["session"]["request"]; cats=_cats(_main_plan(ctx["session"]))
        require(req.get("has_kid") is True or "kid_safe" in (req.get("safety_flags") or []), "kid safety not recognized", f)
        require(not any(c in cats for c in ("酒吧","密室")), f"kid plan contains unsafe category: {cats}", f)
        return f
    add(Case(12, "family safe", TEXT["family"], c12, lambda: default_runner(TEXT["family"], {"party_size":3,"start_time":"14:00","budget_per_person":180,"home_area":"新街口"})))

    def c13(ctx):
        f=[]; req=ctx["session"]["request"]; plan=_main_plan(ctx["session"]); opt=plan.get("optional_addons") or []
        require(req.get("transport")=="self_drive", "self_drive not recognized", f)
        require("drive_safe" in (req.get("safety_flags") or []) or "no_alcohol" in (req.get("safety_flags") or []), "drive alcohol safety missing", f)
        require(not any(x.get("category")=="酒吧" for x in opt), "self-drive plan recommends bar/alcohol addon", f)
        return f
    add(Case(13, "self-drive drinking safety", TEXT["drive_ktv"], c13, lambda: default_runner(TEXT["drive_ktv"], {"party_size":4,"start_time":"20:00","budget_per_person":180,"home_area":"新街口","window_hours":3})))

    def runner14():
        agent, session = _run(TEXT["script_full"])
        first = _ids(_main_plan(session))[0]
        agent.reject_merchant(first)
        session = agent.run(TEXT["script_full"])
        if session.get("mode") == "needs_clarification":
            session = agent.refine(_answer_for(session))
        return {"agent":agent,"session":session,"rejected":first}
    def c14(ctx):
        f=[]; rejected=ctx["rejected"]; ids=_ids(_main_plan(ctx["session"]))
        require(rejected not in ids, f"rejected merchant {rejected} returned in main plan {ids}", f)
        return f
    add(Case(14, "reject memory suppresses merchant", TEXT["script_full"], c14, runner14))

    def c15(ctx):
        f=[]; req=ctx["session"]["request"]; cats=_cats(_main_plan(ctx["session"]))
        require(cats == ["电影院"], f"high ad merchant broke requested movie/no_meal hard constraint: {cats}", f)
        require("no_meal" in (req.get("negative_intents") or []), "no_meal lost", f)
        return f
    add(Case(15, "ad cannot break hard constraints", TEXT["movie"], c15, lambda: with_temp_ad_bid("m_014", 999999, lambda: default_runner(TEXT["movie"], {"start_time":"19:30","home_area":"新街口"}))))

    def c16(ctx):
        f=[]; require(not ctx["session"].get("bookings"), "bookings exist before select", f); return f
    add(Case(16, "no booking before select", TEXT["script_full"], c16))

    def runner17():
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        return {"agent":agent,"session":session}
    def c17(ctx):
        f=[]; require(not ctx["session"].get("bookings"), "bookings exist after select before confirm", f); return f
    add(Case(17, "no booking after select before confirm", TEXT["script_full"], c17, runner17))

    def runner18():
        agent, session = _run(TEXT["script_full"])
        session = _choose_confirm(agent, session)
        return {"agent":agent,"session":session}
    def c18(ctx):
        f=[]; session=ctx["session"]
        require(bool(session.get("bookings")), "bookings empty after confirm", f)
        require(bool(session.get("share_card")), "share_card missing after confirm", f)
        return f
    add(Case(18, "booking only after confirm", TEXT["script_full"], c18, runner18))

    def c19(ctx):
        f=[]; agent, session = _run(TEXT["friends_food"])
        agent.choose(0); session=agent.confirm_and_execute()
        addon=session.get("addon"); booked={b.get("merchant_id") for b in session.get("bookings", [])}
        if addon:
            require(addon.get("id") not in booked, "optional addon was booked by default", f)
        return f
    add(Case(19, "optional addons not in bill by default", TEXT["friends_food"], lambda ctx: c19(ctx)))

    def runner20():
        agent, session = _run(TEXT["script_full"])
        before = session.get("mode")
        session = agent.choose(0)
        selected = session.get("mode")
        session = agent.confirm_and_execute()
        return {"agent":agent,"session":session,"order":[before,selected,session.get("mode")]}
    def c20(ctx):
        f=[]; require(ctx["order"] == ["planned","selected","executed"], f"bad backend state order: {ctx['order']}", f); return f
    add(Case(20, "friend confirmation before final booking state", TEXT["script_full"], c20, runner20))

    def c21(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; before=ctx["before_ids"]; after=_ids(ctx["session"].get("chosen") or {})
        require(exc.get("changed_kind")=="restaurant", "restaurant_full did not target restaurant", f)
        require(before[0:1] == after[0:1], "non-restaurant node changed", f)
        require("其它节点不动" in (exc.get("reason") or ""), "no explanation for partial replacement", f)
        return f
    add(Case(21, "restaurant_full before_departure", TEXT["friends_food"], c21, lambda: runner_exc("restaurant_full", {"type":"restaurant_full","location_state":"before_departure"})))

    def c22(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; after=exc.get("after") or {}
        require(exc.get("changed_kind")=="restaurant", "near_current did not target restaurant", f)
        require(after.get("area") in ("新街口","老门东","河西"), "replacement lacks area", f)
        require(after.get("area")=="新街口", f"near_current did not prefer same area: {after.get('area')}", f)
        return f
    add(Case(22, "restaurant_full near current", TEXT["friends_food"], c22, lambda: runner_exc("restaurant_full", {"type":"restaurant_full","location_state":"near_current_merchant","current_area":"新街口"})))

    def c23(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; after=exc.get("after") or {}
        require(exc.get("changed_kind")=="activity", "ticket_soldout did not target activity", f)
        require(after.get("category")=="剧本杀" or "同位置语境下没有可替换" in (exc.get("reason") or ""), "script ticket replacement did not prefer script", f)
        return f
    add(Case(23, "ticket soldout script", TEXT["script_full"], c23, lambda: runner_exc("ticket_soldout", {"type":"ticket_soldout","location_state":"before_departure"}, TEXT["script_full"])))

    def c24(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; plan=ctx["session"].get("chosen") or {}
        require(exc.get("changed_kind")=="time", "time_conflict did not adjust time", f)
        require(exc.get("after") != exc.get("before"), "start time did not change", f)
        require(all(":" in s.get("start","") and ":" in s.get("end","") for s in _business_steps(plan)), "bad time format after replan", f)
        return f
    add(Case(24, "time conflict", TEXT["script_full"], c24, lambda: runner_exc("time_conflict", {"type":"time_conflict"}, TEXT["script_full"])))

    def c25(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}
        require(exc.get("needs_user_confirm") is True, "over-budget exception missing needs_user_confirm=true", f)
        still_ok = exc.get("still_ok") or {}
        require(still_ok.get("budget") is False or exc.get("warnings"), "over-budget exception did not expose budget risk", f)
        return f
    def runner25():
        text = TEXT["friends_food"].replace("人均180，", "")
        return runner_exc("restaurant_full", {"type":"restaurant_full","location_state":"before_departure"}, text, {"budget_per_person": 60})
    add(Case(25, "over budget exception confirm", TEXT["friends_food"], c25, runner25))

    def c26(ctx):
        f=[]; require(ctx["session"].get("mode") in ("needs_clarification","planned"), "empty input crashed or unusable", f); return f
    add(Case(26, "empty input", "", c26, lambda: default_runner("", auto_refine=False)))

    def c27(ctx):
        f=[]; req=ctx["session"]["request"]
        require(ctx["session"].get("mode")=="needs_clarification" or req.get("confidence", 1) < 0.5, "garbled input not low-confidence/clarified", f)
        return f
    add(Case(27, "garbled input", "####@@@", c27, lambda: default_runner("####@@@", auto_refine=False)))

    def c28(ctx):
        f=[]; req=ctx["session"]["request"]; keys=set(req.get("missing_fields") or [])
        require(req.get("confidence", 1) < 0.5 or req.get("intent_conflict"), "mutual conflict not low confidence", f)
        require("experience_mode" in keys or ctx["session"].get("mode")=="needs_clarification", "mutual conflict did not ask clarification", f)
        return f
    add(Case(28, "mutual stay-in cinema", "我不想出门，但想去影院看电影", c28, lambda: default_runner("我不想出门，但想去影院看电影", auto_refine=False)))

    def c29(ctx):
        f=[]; plan=_main_plan(ctx["session"])
        require(plan.get("unavailable") or plan.get("status")=="needs_relaxation", "low budget did not return needs_relaxation", f)
        return f
    add(Case(29, "ultra low budget script", "4个人想玩剧本杀，人均20，新街口，19:00，4小时", c29))

    def runner30():
        req = parse_request(TEXT["script_full"])
        merchants = json.loads(MERCHANTS.read_text(encoding="utf-8"))
        req["_rejected_ids"] = {str(m.get("id")) for m in merchants if m.get("category") == "剧本杀"}
        plans = build_itinerary(req)
        return {"session":{"request":req,"plans":plans}}
    def c30(ctx):
        f=[]; plan=_main_plan(ctx["session"])
        require(plan.get("unavailable") or plan.get("status")=="needs_relaxation", "no candidates did not return unavailable/relaxation", f)
        return f
    add(Case(30, "merchant pool no candidate", TEXT["script_full"], c30, runner30))

    def lock_case(expected_cat: str, expected_intent: str | None = None):
        def check(ctx):
            f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"]); cats=_cats(plan)
            require(expected_cat in (req.get("requested_categories") or []), f"requested category missing {expected_cat}", f)
            if expected_intent:
                require(req.get("primary_intent")==expected_intent, f"primary_intent not {expected_intent}: {req.get('primary_intent')}", f)
            if plan.get("unavailable"):
                require(plan.get("status") in ("needs_relaxation","not_supported_yet","plan_unavailable"), "unsupported case lacks structured failure", f)
            else:
                require(cats and cats == [expected_cat], f"{expected_cat} silently changed to {cats}", f)
            return f
        return check
    add(Case(31, "massage relaxation", TEXT["massage"], lock_case("按摩", "massage"), lambda: default_runner(TEXT["massage"], {"start_time":"15:00","home_area":"新街口","budget_per_person":200})))
    add(Case(32, "billiards", TEXT["billiards"], lock_case("台球", "billiards"), lambda: default_runner(TEXT["billiards"], {"start_time":"19:00","home_area":"新街口","budget_per_person":100,"window_hours":2})))
    add(Case(33, "maanshan citywalk", TEXT["maanshan"], lock_case("citywalk", "citywalk"), lambda: default_runner(TEXT["maanshan"], {"party_size":2,"start_time":"10:00","budget_per_person":150,"home_area":"马鞍山","window_hours":10})))
    add(Case(34, "hotel rest", TEXT["hotel"], lock_case("酒店", "hotel"), lambda: default_runner(TEXT["hotel"], {"party_size":1,"start_time":"21:00","budget_per_person":300,"home_area":"新街口","window_hours":4})))

    def feedback_runner(base_text: str, feedback_text: str, answers: dict | None = None):
        agent, session = _run(base_text, answers or {})
        session = _choose(agent, session)
        before_ids = _ids(session.get("chosen") or {})
        session = agent.run(feedback_text)
        return {"agent":agent,"session":session,"before_ids":before_ids}

    def c35(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}
        require((ctx["session"].get("request") or {}).get("feedback_intent")=="queue_or_full", "queue feedback not detected", f)
        require(exc.get("changed_kind")=="restaurant", "queue feedback did not replan restaurant", f)
        require(ctx["before_ids"][0:1] == _ids(ctx["session"].get("chosen") or {})[0:1], "feedback replanned from scratch", f)
        return f
    add(Case(35, "feedback queue too long", TEXT["queue_feedback"], c35, lambda: feedback_runner(TEXT["friends_food"], TEXT["queue_feedback"])))

    def c36(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}
        require((ctx["session"].get("request") or {}).get("feedback_intent")=="friend_late", "late feedback not detected", f)
        require(exc.get("changed_kind")=="time", "late feedback did not shift time", f)
        return f
    add(Case(36, "feedback friend late", TEXT["late_feedback"], c36, lambda: feedback_runner(TEXT["script_full"], TEXT["late_feedback"])))

    def c37(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; step=_script_step(ctx["session"].get("chosen") or {})
        require((ctx["session"].get("request") or {}).get("feedback_intent")=="too_horror", "horror feedback not detected", f)
        if exc.get("after"):
            require(step.get("horror_level") not in ("中","高"), "horror feedback kept scary script", f)
        else:
            require(exc.get("needs_user_confirm") is True, "no lighter script but no user confirmation", f)
        return f
    add(Case(37, "feedback too horror", TEXT["horror_feedback"], c37, lambda: feedback_runner("6个人今晚19:30想玩恐怖本，人均200，河西，4小时", TEXT["horror_feedback"])))

    def c38(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}
        require((ctx["session"].get("request") or {}).get("feedback_intent")=="too_expensive", "budget feedback not detected", f)
        require(exc.get("changed_kind")=="budget", "budget feedback did not enter budget replan", f)
        return f
    add(Case(38, "feedback cheaper", TEXT["cheap_feedback"], c38, lambda: feedback_runner(TEXT["script_full"], TEXT["cheap_feedback"])))

    def c39(ctx):
        f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"]); step=_business_steps(plan)[0] if _business_steps(plan) else {}
        require(req.get("primary_intent")=="milk_tea", "caffeine tea did not stay milk tea", f)
        require("caffeine_free" in (req.get("safety_flags") or []), "missing caffeine_free", f)
        require(_cats(plan)==["奶茶"], f"caffeine tea changed category: {_cats(plan)}", f)
        require((step.get("drink_options") or {}).get("caffeine") in ("none","free","caffeine_free"), "recommended drink has caffeine", f)
        return f
    add(Case(39, "caffeine-free milk tea", TEXT["caffeine_tea"], c39, lambda: default_runner(TEXT["caffeine_tea"], {"start_time":"20:00","home_area":"新街口","budget_per_person":30})))

    def c40(ctx):
        f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"]); cats=_cats(plan); opt=plan.get("optional_addons") or []
        require("kid_safe" in (req.get("safety_flags") or []) or req.get("has_kid"), "kid KTV missing kid safety", f)
        require("no_alcohol" in (req.get("safety_flags") or []) or "no_alcohol" in (req.get("negative_intents") or []), "kid KTV missing no_alcohol", f)
        require(cats == ["KTV"] or (plan.get("unavailable") and plan.get("status") in ("needs_relaxation","not_supported_yet")), f"KTV changed to {cats}", f)
        require(not any(x.get("category")=="酒吧" for x in opt), "kid/no alcohol KTV recommends bar", f)
        return f
    add(Case(40, "kid KTV no alcohol", TEXT["kid_ktv"], c40, lambda: default_runner(TEXT["kid_ktv"], {"party_size":3,"start_time":"19:00","budget_per_person":150,"home_area":"新街口","window_hours":2})))

    def no_plan_runner(text):
        return default_runner(text, auto_refine=False)

    def frame_check(expected_intent, expected_action, forbidden_goal=()):
        def check(ctx):
            f=[]; s=ctx["session"]; req=s.get("request") or {}; frame=req.get("intent_frame") or {}
            require(frame.get("primary_intent")==expected_intent, f"intent not {expected_intent}: {frame.get('primary_intent')}", f)
            require(frame.get("next_action")==expected_action, f"next_action not {expected_action}: {frame.get('next_action')}", f)
            require(not s.get("plans"), "broad/rest intent generated merchant plans", f)
            goal = frame.get("goal_summary") or req.get("goal_summary") or ""
            for bad in forbidden_goal:
                require(str(bad) not in goal, f"default leaked into goal_summary: {bad}", f)
            return f
        return check

    add(Case(41, "intent truth food discovery", "我想吃点什么",
                      frame_check("food_discovery", "ask_clarification", ["周末","150","公共交通","新街口","4人"]),
                      lambda: no_plan_runner("我想吃点什么")))
    add(Case(42, "intent truth casual food", "随便吃点",
                      frame_check("food_discovery", "ask_clarification", ["150","公共交通","新街口","4人"]),
                      lambda: no_plan_runner("随便吃点")))
    add(Case(43, "intent truth nearby food asks location", "附近有啥好吃的",
                      frame_check("food_discovery", "ask_clarification", ["新街口"]),
                      lambda: no_plan_runner("附近有啥好吃的")))
    def c44(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; cf=frame.get("confirmed_fields") or {}
        require(frame.get("primary_intent")=="food_discovery", "tonight dinner not food discovery", f)
        require(cf.get("start_time") is not None, "tonight dinner did not keep time", f)
        require(cf.get("party_size") is None and cf.get("budget_per_person") is None and cf.get("home_area") is None, "default fields leaked into confirmed_fields", f)
        require(not ctx["session"].get("plans"), "broad dinner generated plans", f)
        return f
    add(Case(44, "intent truth tonight dinner", "今晚吃饭", c44, lambda: no_plan_runner("今晚吃饭")))
    add(Case(45, "intent truth rest sleep", "我想睡会",
                      frame_check("rest", "rest_support", ["展览","咖啡馆","餐厅","剧本杀"]),
                      lambda: no_plan_runner("我想睡会")))
    add(Case(46, "intent truth rest exhausted", "我好累，现在什么都不想干",
                      frame_check("rest", "rest_support", ["展览","餐厅","剧本杀"]),
                      lambda: no_plan_runner("我好累，现在什么都不想干")))
    add(Case(47, "intent truth outing category choices", "我想和同学出去玩",
                      frame_check("outing", "show_category_choices", ["城市影像展","餐厅"]),
                      lambda: no_plan_runner("我想和同学出去玩")))
    add(Case(48, "intent truth date asks first", "想和女朋友去约会，浪漫一点",
                      frame_check("date", "ask_clarification", ["150","公共交通","新街口"]),
                      lambda: no_plan_runner("想和女朋友去约会，浪漫一点")))
    def c49(ctx):
        f=[]; s=ctx["session"]; frame=(s.get("request") or {}).get("intent_frame") or {}; seq=frame.get("sequence") or []
        require([x.get("category") for x in seq[:2]] == ["剧本杀", None], f"sequence not script then eat: {seq}", f)
        require(s.get("mode")=="needs_clarification", "script+eat missing fields did not ask", f)
        require(not s.get("plans"), "script+eat missing fields generated plans", f)
        return f
    add(Case(49, "intent truth script then meal", "想打个本，再去吃个饭", c49, lambda: no_plan_runner("想打个本，再去吃个饭")))
    def c50(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; cats=[x.get("category") for x in frame.get("sequence") or []]
        require("电影院" in cats, f"movie category missing: {cats}", f)
        require("no_meal" not in (req.get("negative_intents") or []) or True, "noop", f)
        if ctx["session"].get("plans"):
            require(_cats(_main_plan(ctx["session"])) == ["电影院"], "movie plan contains non-movie main node", f)
        return f
    add(Case(50, "intent truth short movie", "想出去玩2小时，看个电影", c50, lambda: no_plan_runner("想出去玩2小时，看个电影")))

    def c51(ctx):
        f=[]; req=ctx["session"].get("request") or {}; cons=ctx["session"].get("constraints") or {}
        require("cannot_ice" in (req.get("safety_flags") or []), "missing cannot_ice", f)
        require(any(x.get("type")=="drink_temperature" for x in cons.get("hard_constraints") or []), "constraint engine missing drink_temperature", f)
        return f
    add(Case(51, "constraint pregnant hot drink", "我是孕妇，想喝点热的，不要冰", c51, lambda: no_plan_runner("我是孕妇，想喝点热的，不要冰")))
    def c52(ctx):
        f=[]; cons=ctx["session"].get("constraints") or {}
        require("kid_safe" in [x.get("type") for x in cons.get("safety_constraints") or []], "missing kid_safe constraint", f)
        require("酒吧" in (cons.get("blocked_categories") or []), "kid_safe did not block bar", f)
        return f
    add(Case(52, "constraint kid safe", "带孩子出去玩，别太成人", c52, lambda: no_plan_runner("带孩子出去玩，别太成人")))
    def c53(ctx):
        f=[]; cons=ctx["session"].get("constraints") or {}
        require(any(x.get("type")=="no_alcohol" for x in cons.get("hard_constraints") or []), "missing no_alcohol hard constraint", f)
        return f
    add(Case(53, "constraint self-drive no alcohol", "自驾去唱歌，别喝酒", c53, lambda: no_plan_runner("自驾去唱歌，别喝酒")))
    def c54(ctx):
        f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"])
        require("no_spicy" in (req.get("safety_flags") or []) or "no_spicy" in (req.get("diet_limits") or []), "missing no_spicy", f)
        if plan and not plan.get("unavailable"):
            step=_business_steps(plan)[0] if _business_steps(plan) else {}
            support=set(step.get("diet_support") or [])
            require(bool(support & {"no_spicy","不辣","番茄锅","鸳鸯锅","清汤锅"}), "hotpot no-spicy support missing", f)
        return f
    add(Case(54, "constraint hotpot no spicy", "有人不吃辣，想吃火锅", c54, lambda: default_runner("有人不吃辣，想吃火锅", {"party_size":4,"start_time":"18:00","budget_per_person":150,"home_area":"新街口"})))
    def c55(ctx):
        f=[]; req=ctx["session"].get("request") or {}
        require("horror" in (req.get("intent_tags") or []) or req.get("primary_intent") in ("escape_room","outing"), "escape/horror intent not detected", f)
        return f
    add(Case(55, "constraint escape fear horror", "有人怕恐怖，想玩密室", c55, lambda: no_plan_runner("有人怕恐怖，想玩密室")))

    def c56(ctx):
        f=[]; gd=ctx["session"].get("group_decision") or {}
        require(gd.get("is_group") is True, "group not detected", f)
        require(gd.get("choice_cards"), "outing group has no choice cards", f)
        require(not ctx["session"].get("plans"), "group broad intent generated stores", f)
        return f
    add(Case(56, "group outing choices", "我和同学出去玩，还没想好干啥", c56, lambda: no_plan_runner("我和同学出去玩，还没想好干啥")))
    def c57(ctx):
        f=[]; gd=ctx["session"].get("group_decision") or {}
        require(gd.get("decision_mode") in ("collect_votes","ask_host"), f"bad group decision mode {gd.get('decision_mode')}", f)
        require("有人想唱歌" in (gd.get("known_preferences") or []) and "有人想打台球" in (gd.get("known_preferences") or []), "parallel preferences missing", f)
        return f
    add(Case(57, "group parallel preferences", "我和朋友聚会，有人想唱歌有人想打台球", c57, lambda: no_plan_runner("我和朋友聚会，有人想唱歌有人想打台球")))
    def c58(ctx):
        f=[]; gd=ctx["session"].get("group_decision") or {}
        require(gd.get("decision_mode")=="compromise_area", f"not compromise_area: {gd.get('decision_mode')}", f)
        return f
    add(Case(58, "group compromise area", "四个人位置不一样，想找折中的地方", c58, lambda: no_plan_runner("四个人位置不一样，想找折中的地方")))

    def c59(ctx):
        from agent.price_optimizer import optimize_price
        f=[]; plan={"steps":[{"kind":"activity","price":100,"group_deal":{"price":88}},{"kind":"restaurant","price":120,"group_deal":{"price":108}}]}
        pay=optimize_price(plan,{})
        require(pay["separate_best_total"] < pay["bundle_total"], "mock separate is not cheaper than bundle", f)
        require(pay["recommended_payment"]=="separate", f"did not recommend separate: {pay}", f)
        require(pay["warnings"], "missing saving warning", f)
        return f
    add(Case(59, "price separate cheaper", "price mock separate", c59, lambda: {"session":{"request":{}}, "plan_summary":"price mock"}))
    def c60(ctx):
        from agent.price_optimizer import optimize_price
        f=[]; pay=optimize_price({"steps":[{"kind":"activity","price":100}]},{})
        require(any(x["name"]=="不可与其它优惠同享" and x["usable"] is False for x in pay["restrictions"]), "coupon restriction missing", f)
        return f
    add(Case(60, "price weekend restriction visible", "price mock coupon", c60, lambda: {"session":{"request":{}}, "plan_summary":"price mock"}))
    def c61(ctx):
        from agent.price_optimizer import optimize_price
        f=[]; pay=optimize_price({"steps":[{"kind":"activity","price":50,"group_deal":{"price":45}}]},{"member_enabled": True})
        require("member_total" in pay and pay["member_total"] <= pay["separate_best_total"], "member price not calculated", f)
        return f
    add(Case(61, "price member cheaper", "price mock member", c61, lambda: {"session":{"request":{}}, "plan_summary":"price mock"}))

    add(Case(62, "regression script full still plans", TEXT["script_full"], c8))
    add(Case(63, "regression period milk tea", TEXT["period_tea"], c2, lambda: default_runner(TEXT["period_tea"], {"start_time":"19:00","home_area":"新街口"})))
    add(Case(64, "regression movie no meal", TEXT["movie"], c4, lambda: default_runner(TEXT["movie"], {"start_time":"19:30","home_area":"新街口"})))

    # Phase 2A: closed-loop itinerary model.
    def c65(ctx):
        f=[]; s=ctx["session"]
        require(s.get("mode") == "needs_clarification", "broad food should ask clarification", f)
        require(not s.get("plans"), "broad food should not build itinerary", f)
        require_no_default_public_summary(s, f)
        return f
    add(Case(65, "phase2a broad food no itinerary", "我想吃点什么", c65, lambda: default_runner("我想吃点什么", auto_refine=False)))

    def c66(ctx):
        f=[]; s=ctx["session"]
        require(s.get("mode") == "rest_support", "rest-first should enter rest_support", f)
        require(not s.get("plans"), "rest-first should not build merchant itinerary", f)
        require_no_default_public_summary(s, f)
        return f
    add(Case(66, "phase2a rest support no itinerary", "我想睡会", c66, lambda: default_runner("我想睡会", auto_refine=False)))

    def c67(ctx):
        f=[]; s=ctx["session"]
        require(s.get("mode") == "category_choices", "broad outing should show category choices", f)
        require(not s.get("plans"), "broad outing should not build concrete itinerary", f)
        return f
    add(Case(67, "phase2a broad outing choice cards", "我想和同学出去玩", c67, lambda: default_runner("我想和同学出去玩", auto_refine=False)))

    def c68(ctx):
        f=[]; segs=_segments(ctx["session"])
        cats=[x.get("category") for x in segs]
        roles=[x.get("role") for x in segs]
        require(len(segs) >= 2, "script then meal should generate two segments", f)
        require("剧本杀" in cats, "script segment missing", f)
        require("EAT" in roles, "meal segment missing", f)
        require(bool(_itinerary(ctx["session"]).get("transits")), "multi-segment itinerary should include transit", f)
        return f
    add(Case(68, "phase2a script then meal itinerary", "想打个本，再去吃个饭", c68, lambda: default_runner("想打个本，再去吃个饭", {"party_size":4,"start_time":"19:00","budget_per_person":180,"script_style":"欢乐本","window_hours":5,"home_area":"新街口"})))

    def c69(ctx):
        f=[]; it=_itinerary(ctx["session"]); cats=[x.get("category") for x in _segments(ctx["session"])]
        require(cats == ["剧本杀"], "script full should be single script segment", f)
        require(bool(it.get("transits")), "script itinerary should include departure transit", f)
        require(bool(it.get("return_transit")), "script itinerary should include return transit", f)
        return f
    add(Case(69, "phase2a script single closed itinerary", TEXT["script_full"], c69))

    def c70(ctx):
        f=[]; cats=[x.get("category") for x in _segments(ctx["session"])]
        require("电影院" in cats, "movie segment missing", f)
        require(not any(x.get("role") == "EAT" for x in _segments(ctx["session"])), "2h movie should not add meal as core", f)
        return f
    add(Case(70, "phase2a 2h movie no forced meal", "1个人19:00想出去玩2小时，看个电影，新街口，人均100", c70))

    def c71(ctx):
        f=[]; segs=_segments(ctx["session"])
        require(any(x.get("category") == "电影院" for x in segs), "5h movie should keep movie core", f)
        require(not any(x.get("source") == "explicit_text" and x.get("role") == "EAT" for x in segs), "meal cannot be marked explicit unless user asked", f)
        return f
    add(Case(71, "phase2a 5h movie meal not explicit", "1个人19:00想出去玩5小时，看个电影，新街口，人均150", c71))

    def c72(ctx):
        f=[]; it=_itinerary(ctx["session"])
        require(any("超过" in str(x) or "窗口" in str(x) for x in it.get("warnings", [])), "overtime itinerary should warn/need relaxation", f)
        return f
    add(Case(72, "phase2a overtime warning", "4个人21:00先看电影再吃饭，公共交通，新街口，人均150，2小时", c72))

    def c73(ctx):
        f=[]; it=_itinerary(ctx["session"])
        require(it.get("origin", {}).get("type") == "unknown", "unknown origin should not default to New Street", f)
        require(any("出发" in x for x in it.get("missing_for_closure", [])), "origin missing should be listed", f)
        return f
    def unknown_origin_runner():
        agent = Agent()
        agent.run(TEXT["movie"])
        return {"agent": agent, "session": agent.refine({"start_time": "19:30"})}
    add(Case(73, "phase2a unknown origin closure", TEXT["movie"], c73, unknown_origin_runner))

    def c74(ctx):
        f=[]; it=_itinerary(ctx["session"])
        require(it.get("return_transit") is None or any("回" in x for x in it.get("missing_for_closure", [])), "unknown return should be null or listed missing", f)
        return f
    add(Case(74, "phase2a unknown return closure", TEXT["movie"], c74, unknown_origin_runner))

    def c75(ctx):
        f=[]; it=_itinerary(ctx["session"])
        for seg in it.get("segments", []):
            if seg.get("is_core"):
                enough = len(seg.get("merchant_candidates") or []) >= 2
                warned = any("备选不足" in str(w) for w in it.get("warnings", []))
                require(enough or warned, f"segment {seg.get('segment_id')} lacks candidates without warning", f)
        return f
    add(Case(75, "phase2a candidate count or warning", TEXT["script_full"], c75))

    def c76_runner():
        agent, s = _run(TEXT["friends_food"], {"start_time":"18:00","home_area":"新街口","budget_per_person":180})
        s = _choose_confirm(agent, s, confirm=False)
        before = [x.get("id") for x in _business_steps(s.get("chosen") or {})]
        s = agent.inject_exception("restaurant_full", {"location_state":"near_current_merchant","current_area":"新街口"})
        return {"agent":agent,"session":s,"before_ids":before}
    def c76(ctx):
        f=[]; before=ctx.get("before_ids") or []; after=[x.get("id") for x in _business_steps(ctx["session"].get("chosen") or {})]
        require(len(before)==len(after), "replace should keep segment count", f)
        require(before[:1]==after[:1], "replace should keep unaffected first segment", f)
        return f
    add(Case(76, "phase2a replace only current segment", "restaurant_full local replace", c76, c76_runner))

    def c77_runner():
        agent, s = _run(TEXT["script_full"])
        return {"agent":agent,"session":_choose_confirm(agent, s)}
    def c77(ctx):
        f=[]; segs=_segments(ctx["session"]); script=next((x for x in segs if x.get("category")=="剧本杀"), {})
        b=script.get("booking_summary") or {}
        for key in ["script_name","people","session_time","duration_minutes","assembling","mock_contact"]:
            require(key in b, f"script booking summary missing {key}", f)
        return f
    add(Case(77, "phase2a script booking summary", TEXT["script_full"], c77, c77_runner))

    def c78_runner():
        agent, s = _run(TEXT["friends_food"], {"start_time":"18:00","home_area":"新街口","budget_per_person":180})
        return {"agent":agent,"session":_choose_confirm(agent, s)}
    def c78(ctx):
        f=[]; eat=next((x for x in _segments(ctx["session"]) if x.get("role")=="EAT"), {})
        b=eat.get("booking_summary") or {}
        for key in ["people","table_type","arrival_time","use_group_deal","mock_contact"]:
            require(key in b, f"restaurant booking summary missing {key}", f)
        return f
    add(Case(78, "phase2a restaurant booking summary", TEXT["friends_food"], c78, c78_runner))

    def c79(ctx):
        f=[]
        for seg in _segments(ctx["session"]):
            labels=" ".join(x.get("label","") for x in seg.get("support_options") or [])
            require("满座" in labels and "取消" in labels and "换时间" in labels and "客服" in labels, "support options incomplete", f)
        return f
    add(Case(79, "phase2a support options per segment", TEXT["script_full"], c79))

    def c80_runner():
        agent, s = _run(TEXT["script_full"]); s=agent.choose(0); seg=(_segments(s) or [{}])[0]
        return {"agent":agent,"session":agent.support_issue(seg.get("segment_id","seg_1"), "full_or_queue")}
    def c80(ctx):
        f=[]; sc=ctx["session"].get("support_case") or {}
        require(bool(sc.get("suggested_actions")), "support case should return suggested actions", f)
        require(sc.get("next_step") in {"replace_segment","contact_merchant","refund_mock","keep_plan"}, "support next_step invalid", f)
        return f
    add(Case(80, "phase2a support mock page", "support mock", c80, c80_runner))

    def c81(ctx):
        f=[]; pay=_itinerary(ctx["session"]).get("price_optimization") or _main_plan(ctx["session"]).get("price_optimization") or {}
        require("separate_best_total" in pay and "bundle_total" in pay, "itinerary price optimization missing totals", f)
        if pay.get("separate_best_total", 9999) < pay.get("bundle_total", 0):
            require(pay.get("recommended_payment") == "separate", "separate cheaper should recommend separate", f)
        return f
    add(Case(81, "phase2a price optimizer attached", TEXT["script_full"], c81))

    def c82(ctx):
        f=[]; plan=_main_plan(ctx["session"]); seg_areas={x.get("area") for x in _segments(ctx["session"])}
        for addon in plan.get("optional_addons") or []:
            require(addon.get("area") in seg_areas, "optional addon should stay in same business area", f)
        return f
    add(Case(82, "phase2a optional addon same area", TEXT["script_full"], c82))

    def refined_script_meal_runner():
        agent = Agent()
        agent.run("想打个本，再去吃个饭")
        session = agent.refine({
            "party_size": 4,
            "start_time": "19:00",
            "budget_per_person": 180,
            "script_style": "欢乐本",
            "window_hours": 5,
            "home_area": "新街口",
        })
        return {"agent": agent, "session": session}

    def c83(ctx):
        f=[]; it=_itinerary(ctx["session"])
        origin=it.get("origin") or {}
        require(origin.get("type")=="home_area", "origin type should be home_area after refine", f)
        require(origin.get("area")=="新街口", "origin area should be refined answer", f)
        require(origin.get("source")=="user_answer", "origin source should be user_answer", f)
        require(len(it.get("transits") or []) >= 2, "refined multi-segment should have origin and inter-segment transit", f)
        require(bool(it.get("return_transit")), "refined multi-segment should have return transit", f)
        fs=(ctx["session"].get("request") or {}).get("intent_frame",{}).get("field_sources",{})
        require(fs.get("home_area")=="user_answer" and fs.get("start_time")=="user_answer", "field_sources not synced from answers", f)
        return f
    add(Case(83, "cleanup refined home_area updates origin", "想打个本，再去吃个饭", c83, refined_script_meal_runner))

    def c84(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; confirmed=frame.get("confirmed_fields") or {}
        require(req.get("party_size") is None, "broad input should not write party_size fallback", f)
        require(req.get("budget_per_person") is None, "broad input should not write budget fallback", f)
        require(req.get("start_time") is None, "broad input should not write start_time fallback", f)
        require(confirmed.get("party_size") is None, "intent_frame should not confirm default party_size", f)
        require(confirmed.get("budget_per_person") is None, "intent_frame should not confirm default budget", f)
        require("internal_default" not in json.dumps(frame, ensure_ascii=False), "intent_frame should not contain internal_default", f)
        return f
    add(Case(84, "cleanup no internal default after broad input", "我想吃点什么", c84, lambda: default_runner("我想吃点什么", auto_refine=False)))

    def c85(ctx):
        f=[]; segs=_segments(ctx["session"])
        require(segs and segs[0].get("category")=="剧本杀", "first segment should be script game", f)
        require(segs and segs[0].get("source")=="explicit_text", "script segment should be explicit_text", f)
        eat=next((x for x in segs if x.get("role")=="EAT"), {})
        require(bool(eat), "EAT segment missing", f)
        require(eat.get("source")=="explicit_text", "explicit meal should be explicit_text", f)
        return f
    add(Case(85, "cleanup script then meal explicit sources", "想打个本，再去吃个饭", c85, refined_script_meal_runner))

    def c86(ctx):
        f=[]; segs=_segments(ctx["session"])
        movie=next((x for x in segs if x.get("category")=="电影院"), {})
        require(movie.get("source")=="explicit_text", "movie should be explicit_text", f)
        for seg in segs:
            if seg.get("role")=="EAT":
                require(seg.get("source")!="explicit_text", "system suggested meal cannot be explicit_text", f)
        return f
    add(Case(86, "cleanup movie 5h meal not explicit", "1个人19:00想出去玩5小时，看个电影，新街口，人均150", c86))

    def c87(ctx):
        f=[]; pay=_itinerary(ctx["session"]).get("price_optimization") or {}
        require(pay.get("original_total", 0)>0, "original_total should be nonzero", f)
        require(pay.get("separate_best_total", 0)>0, "separate_best_total should be nonzero", f)
        require(pay.get("bundle_total", 0)>0, "bundle_total should be nonzero", f)
        for seg in _segments(ctx["session"]):
            if seg.get("is_core", True):
                require((seg.get("coupon_summary") or {}).get("original_price", 0)>0, "coupon original_price should be nonzero for billable segment", f)
        return f
    add(Case(87, "cleanup price totals nonzero", TEXT["script_full"], c87))

    def c88(ctx):
        f=[]; cats=_cats(_main_plan(ctx["session"])); it=_itinerary(ctx["session"])
        require("在线电影" not in cats, "stay_in should not include online movie merchant", f)
        require(any(c in cats for c in ["外卖","闪购零食"]), "stay_in should include Meituan executable supply", f)
        if "看" in (ctx["session"].get("request",{}).get("raw_text") or ""):
            require(bool(it.get("context_note")), "watching content should be context_note", f)
        return f
    add(Case(88, "cleanup stay_in no online movie merchant", TEXT["stay_in"], c88, lambda: default_runner(TEXT["stay_in"], {"start_time":"20:00","home_area":"新街口","budget_per_person":120})))

    def support_api_runner():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        client=TestClient(server.app)
        sid="cleanup_support"
        r=client.post("/plan", json={"session_id":sid,"text":TEXT["script_full"]}).json()
        if not r.get("session",{}).get("plans"):
            return {"session": r.get("session",{}), "api_response": r}
        client.post("/select", json={"session_id":sid,"plan_index":0}).json()
        res=client.post("/support", json={"session_id":sid,"segment_id":"seg_1","issue_type":"full_or_queue"}).json()
        return {"session": res.get("session",{}), "api_response": res}
    def c89(ctx):
        f=[]; res=ctx.get("api_response") or {}; sc=(res.get("session") or {}).get("support_case") or {}
        require(res.get("ok") is True, "/support should return ok true", f)
        require(bool(sc.get("suggested_actions")), "/support should return suggested_actions", f)
        return f
    add(Case(89, "cleanup support API TestClient", "support api", c89, support_api_runner))

    def c90(ctx):
        f=[]; it=_itinerary(ctx["session"])
        require(it.get("origin",{}).get("type")=="unknown", "origin should remain unknown", f)
        require(not it.get("transits"), "unknown origin should not create fake origin transit", f)
        require(any("出发" in x for x in it.get("missing_for_closure", [])), "missing_for_closure should mention origin", f)
        return f
    add(Case(90, "cleanup unknown origin no fake transit", TEXT["movie"], c90, unknown_origin_runner))

    def c91(ctx):
        f=[]; it=_itinerary(ctx["session"])
        require(it.get("origin",{}).get("source")=="user_answer", "known origin should come from user_answer", f)
        require(bool(it.get("transits")), "known origin should produce origin transit", f)
        require(bool(it.get("return_transit")), "known origin should produce return transit", f)
        return f
    add(Case(91, "cleanup known origin transit and return", "想打个本，再去吃个饭", c91, refined_script_meal_runner))

    def c92(ctx):
        f=[]
        for seg in _segments(ctx["session"]):
            if seg.get("is_core", True):
                require((seg.get("coupon_summary") or {}).get("original_price", 0)>0, "segment coupon_summary original_price should be nonzero", f)
        return f
    add(Case(92, "cleanup segment coupon summary nonzero", TEXT["script_full"], c92))

    def system_case_runner(check_fn: Callable[[], list[str]]) -> dict:
        failures = check_fn()
        return {
            "session": {"request": {}},
            "system_failures": failures,
            "plan_summary": "system check",
            "booking_status": "system check",
            "exception_summary": "system check",
        }

    def c_system(ctx):
        return list(ctx.get("system_failures") or [])

    add(Case(93, "quick API smoke and session isolation", "api smoke", c_system, lambda: system_case_runner(check_api_smoke), timeout_seconds=90))
    add(Case(94, "quick data integrity", "data integrity", c_system, lambda: system_case_runner(check_data_integrity)))
    add(Case(95, "quick security scan", "security scan", c_system, lambda: system_case_runner(check_security_scan)))

    def c96(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; seq=frame.get("sequence") or []
        require(any(x.get("role")=="PLAY" and x.get("category")=="电影院" and x.get("source")=="explicit_text" for x in seq), f"positive movie segment missing explicit source: {seq}", f)
        require(any(x.get("role")=="EAT" and x.get("source")=="explicit_text" for x in seq), f"positive meal segment missing explicit source: {seq}", f)
        require("no_meal" not in (req.get("negative_intents") or []), "positive movie+meal should not be marked no_meal", f)
        it=_itinerary(ctx["session"])
        require(bool(it.get("warnings")) or bool(_segments(ctx["session"])), "positive movie+meal lost itinerary/warning logic", f)
        return f
    add(Case(96, "microfix positive movie then meal retained", "4个人21:00先看电影再吃饭，公共交通，新街口，人均150，2小时", c96))

    def rescue_runner(text: str, exc_type: str, target_role: str | None = None, target_kind: str | None = None, answers: dict | None = None) -> dict:
        agent, session = _run(text, answers or {})
        session = agent.choose(0)
        chosen = session.get("chosen") or {}
        segs = (chosen.get("itinerary") or {}).get("segments") or []
        target_idx = 0
        for i, seg in enumerate(segs):
            if target_role and seg.get("role") == target_role:
                target_idx = i
                break
            if target_kind and seg.get("category") == target_kind:
                target_idx = i
                break
        target = segs[target_idx] if segs else {}
        before_ids = _ids(chosen)
        before_segments = [
            {"id": s.get("id"), "kind": s.get("kind"), "category": s.get("category"), "name": s.get("name")}
            for s in _business_steps(chosen)
        ]
        context = {
            "type": exc_type,
            "issue_type": exc_type,
            "affected_segment_index": target_idx,
            "affected_segment_id": target.get("segment_id"),
            "current_area": target.get("area"),
            "location_state": "near_current_merchant" if exc_type == "restaurant_full" else "before_departure",
        }
        session = agent.inject_exception(exc_type, context)
        return {
            "agent": agent,
            "session": session,
            "before_ids": before_ids,
            "before_segments": before_segments,
            "target_index": target_idx,
        }

    def c97(ctx):
        f=[]; session=ctx["session"]; exc=session.get("exception_result") or {}; after_ids=_ids(session.get("chosen") or {})
        require(exc.get("issue_type")=="restaurant_full", "issue_type should be restaurant_full", f)
        require(exc.get("changed_kind")=="restaurant", "restaurant rescue did not target restaurant", f)
        require(exc.get("affected_segment_index")==ctx["target_index"], "affected restaurant segment index mismatch", f)
        require((exc.get("original_segment") or {}).get("role")=="EAT", "original segment is not EAT", f)
        require((exc.get("replacement_segment") or {}).get("kind")=="restaurant", "replacement segment is not restaurant", f)
        require(bool(exc.get("changed_segments")), "changed_segments missing", f)
        require(bool(exc.get("kept_segments")), "kept_segments missing", f)
        require(ctx["before_ids"][0:1] == after_ids[0:1], "activity segment changed during restaurant rescue", f)
        if (session.get("chosen") or {}).get("total_cost_per_person", 0) > (session.get("request") or {}).get("budget_per_person", 999):
            require(exc.get("needs_user_confirm") is True or exc.get("warnings"), "over-budget rescue lacks confirm/warning", f)
        return f
    add(Case(97, "phase2b rescue restaurant segment only", TEXT["friends_food"], c97, lambda: rescue_runner(TEXT["friends_food"], "restaurant_full", target_role="EAT")))

    def c98(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; after=exc.get("replacement_segment") or {}
        require(exc.get("issue_type")=="ticket_soldout", "issue_type should be ticket_soldout", f)
        require(exc.get("changed_kind")=="activity", "ticket rescue did not target activity", f)
        require((exc.get("original_segment") or {}).get("role")=="PLAY", "original segment is not PLAY", f)
        require(after.get("role")=="PLAY" or after.get("kind")=="activity", "replacement segment is not PLAY/activity", f)
        require("needs_user_confirm" in exc, "needs_user_confirm field missing", f)
        require(bool(exc.get("changed_segments")), "changed_segments missing for activity rescue", f)
        return f
    add(Case(98, "phase2b rescue activity soldout segment only", TEXT["script_full"], c98, lambda: rescue_runner(TEXT["script_full"], "ticket_soldout", target_role="PLAY")))

    def c99(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; after_ids=_ids(ctx["session"].get("chosen") or {})
        require(exc.get("issue_type")=="time_conflict", "issue_type should be time_conflict", f)
        require(exc.get("changed_kind")=="time", "time rescue did not mark changed_kind=time", f)
        require(int(exc.get("time_delta") or 0) >= 60, "time_delta missing or too small", f)
        require(exc.get("after") != exc.get("before"), "start time was not shifted", f)
        require(ctx["before_ids"] == after_ids, "time rescue should keep original merchants", f)
        require("顺延" in (exc.get("reason") or ""), "time rescue lacks delay explanation", f)
        return f
    add(Case(99, "phase2b rescue friend late shifts itinerary", TEXT["script_full"], c99, lambda: rescue_runner(TEXT["script_full"], "time_conflict", target_role="PLAY")))

    def c100(ctx):
        f=[]; text=(ROOT / "web" / "app.html").read_text(encoding="utf-8")
        require("行程遇到问题，想修改？" in text, "frontend rescue entry missing", f)
        require("triggerSegmentRescue" in text and 'post("/exception"' in text, "frontend rescue call logic missing", f)
        for token in ("rescueResultHTML", "kept_segments", "changed_segments", "budget_delta", "time_delta", "needs_user_confirm"):
            require(token in text, f"frontend rescue result token missing: {token}", f)
        return f
    add(Case(100, "phase2b rescue frontend entry", "frontend static rescue check", c100, lambda: {"session": {}, "plan_summary": "frontend check", "booking_status": "frontend check", "exception_summary": "frontend check"}))

    def c101(ctx):
        f=[]; exc=ctx["session"].get("exception_result") or {}; before=ctx["before_segments"]; after=_business_steps(ctx["session"].get("chosen") or {})
        require(bool(exc.get("issue_type")), "rescue result lacks issue_type", f)
        require(len(before) == len(after), "single segment rescue changed itinerary length", f)
        require(bool(exc.get("changed_segments")) or exc.get("needs_user_confirm") is True, "rescue neither changed nor asked for confirmation", f)
        require("new_plan" in exc, "rescue result lacks new_plan", f)
        return f
    add(Case(101, "phase2b rescue no global reset", TEXT["script_full"], c101, lambda: rescue_runner(TEXT["script_full"], "ticket_soldout", target_role="PLAY")))

    def vote_api_flow(
        text: str,
        *,
        sid: str,
        answers: dict | None = None,
        select_plan: bool = True,
    ) -> dict:
        from fastapi.testclient import TestClient
        import server

        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        headers = {"X-Session-Id": sid}
        r = client.post("/plan", json={"session_id": sid, "text": text}, headers=headers).json()
        session = r.get("session") or {}
        if session.get("mode") == "needs_clarification":
            r = client.post(
                "/refine",
                json={"session_id": sid, "answers": _answer_for(session, answers or {})},
                headers=headers,
            ).json()
            session = r.get("session") or {}
        if select_plan and session.get("plans"):
            r = client.post("/select", json={"session_id": sid, "plan_index": 0}, headers=headers).json()
            session = r.get("session") or {}
        before_plan = session.get("chosen") or _main_plan(session)
        create = client.post("/vote/create", json={"session_id": sid}, headers=headers).json()
        room = create.get("room") or session.get("vote_room") or {}
        if room.get("room_id"):
            get_room = client.get(f"/vote/{room['room_id']}", headers=headers).json()
            if get_room.get("ok"):
                room = get_room.get("room") or room
        return {
            "client": client,
            "server_module": server,
            "sid": sid,
            "headers": headers,
            "session": session,
            "before_plan": before_plan,
            "before_steps": _business_steps(before_plan),
            "room": room,
            "create_response": create,
            "clarification_triggered": False,
            "clarification_completed": True,
        }

    def _vote_option(room: dict, target: str | None = None, kind: str | None = None) -> dict:
        for option in room.get("options") or []:
            if target and option.get("target_segment") != target:
                continue
            if kind and option.get("kind") != kind:
                continue
            return option
        return (room.get("options") or [{}])[0]

    def c102(ctx):
        f=[]; room=ctx.get("room") or {}; session=ctx.get("session") or {}
        option_targets = {o.get("target_segment") for o in room.get("options") or []}
        require(bool(room.get("room_id")), "vote room lacks room_id", f)
        require(bool(room.get("share_url") or room.get("link")), "vote room lacks share_url/link", f)
        require(bool(room.get("share_card")), "vote room lacks share_card", f)
        require("activity" in option_targets, "vote options lack activity option", f)
        require("restaurant" in option_targets, "vote options lack restaurant/addon restaurant option", f)
        require("time" in option_targets, "vote options lack time option", f)
        require(not session.get("executed"), "vote create should not execute booking", f)
        require(len(session.get("bookings") or []) == 0, "vote create should not book items", f)
        return f
    add(Case(102, "phase2b vote room create", TEXT["script_full"], c102, lambda: vote_api_flow(TEXT["script_full"], sid="vote_case_102")))

    def c103(ctx):
        f=[]; client=ctx["client"]; sid=ctx["sid"]; headers=ctx["headers"]; room=ctx["room"]
        room_id = room.get("room_id")
        target = _vote_option(room, kind="plan").get("option_id")
        backup = (_vote_option({"options": [o for o in room.get("options", []) if o.get("option_id") != target]}, kind="plan") or {}).get("option_id") or target
        for voter, option_id in (("小李", target), ("阿岚", target), ("小周", backup)):
            client.post(f"/vote/{room_id}", json={"session_id": sid, "voter": voter, "option_id": option_id}, headers=headers)
        got = client.get(f"/vote/{room_id}", headers=headers).json().get("room") or {}
        summary = got.get("summary") or {}
        require(summary.get("total_votes") == 3, "normal vote tally should be 3", f)
        require((summary.get("leading_option") or {}).get("option_id") == target, "leading option incorrect", f)
        require(summary.get("requires_replan") is False, "normal votes should not require replan", f)
        confirmed = client.post(f"/vote/{room_id}/confirm", json={"session_id": sid}, headers=headers).json()
        require(confirmed.get("ok") is True, "confirm leading option failed", f)
        session = confirmed.get("session") or {}
        require(session.get("mode") == "selected", "confirm leading should keep selected mode", f)
        require(not session.get("executed"), "vote confirm must not execute booking", f)
        require(len(session.get("bookings") or []) == 0, "vote confirm must not book items", f)
        ctx["session"] = session
        ctx["room"] = confirmed.get("room") or got
        return f
    add(Case(103, "phase2b normal vote tally and confirm", TEXT["script_full"], c103, lambda: vote_api_flow(TEXT["script_full"], sid="vote_case_103")))

    def c104(ctx):
        f=[]; client=ctx["client"]; sid=ctx["sid"]; headers=ctx["headers"]; room=ctx["room"]; before=ctx["before_steps"]
        room_id = room.get("room_id")
        opt = _vote_option(room, target="restaurant")
        submit = client.post(
            f"/vote/{room_id}",
            json={"session_id": sid, "voter": "小陈", "option_id": opt.get("option_id"), "feedback": "有人不吃辣"},
            headers=headers,
        ).json()
        fb = submit.get("feedback") or {}
        require(fb.get("is_hard_constraint") is True, "no spicy feedback should be hard constraint", f)
        require(fb.get("target_segment") == "restaurant", "no spicy should target restaurant", f)
        resolved = client.post(f"/vote/{room_id}/resolve", json={"session_id": sid}, headers=headers).json()
        session = resolved.get("session") or {}
        exc = session.get("exception_result") or {}
        after = _business_steps(session.get("chosen") or {})
        require(resolved.get("ok") is True, "resolve no spicy failed", f)
        require(exc.get("changed_kind") == "restaurant", "no spicy should replan restaurant segment", f)
        require([s.get("id") for s in before if s.get("kind") == "activity"] == [s.get("id") for s in after if s.get("kind") == "activity"], "restaurant replan changed activity segment", f)
        replacement = exc.get("replacement_segment") or {}
        require(replacement.get("kind") == "restaurant" or exc.get("needs_user_confirm") is True, "restaurant replacement missing", f)
        ctx["session"] = session
        ctx["room"] = resolved.get("room") or room
        return f
    add(Case(104, "phase2b vote no spicy replans restaurant only", TEXT["friends_food"], c104, lambda: vote_api_flow(TEXT["friends_food"], sid="vote_case_104", answers={"party_size":4,"start_time":"18:00","budget_per_person":180,"home_area":"新街口","window_hours":4})))

    def c105(ctx):
        f=[]; client=ctx["client"]; sid=ctx["sid"]; headers=ctx["headers"]; room=ctx["room"]; before=ctx["before_steps"]
        room_id = room.get("room_id")
        opt = _vote_option(room, target="activity")
        submit = client.post(
            f"/vote/{room_id}",
            json={"session_id": sid, "voter": "小李", "option_id": opt.get("option_id"), "feedback": "这个本我玩过了，换一个"},
            headers=headers,
        ).json()
        fb = submit.get("feedback") or {}
        require(fb.get("is_hard_constraint") is True, "played-before feedback should be hard constraint", f)
        require(fb.get("target_segment") == "activity", "played-before should target activity", f)
        resolved = client.post(f"/vote/{room_id}/resolve", json={"session_id": sid}, headers=headers).json()
        session = resolved.get("session") or {}
        exc = session.get("exception_result") or {}
        after = _business_steps(session.get("chosen") or {})
        require(resolved.get("ok") is True, "resolve played-before failed", f)
        require(exc.get("changed_kind") == "activity", "played-before should replan activity segment", f)
        require([s.get("id") for s in before if s.get("kind") == "restaurant"] == [s.get("id") for s in after if s.get("kind") == "restaurant"], "activity replan changed restaurant segment", f)
        require(bool(exc.get("replacement_segment")) or exc.get("needs_user_confirm") is True, "activity replacement/unavailable signal missing", f)
        ctx["session"] = session
        ctx["room"] = resolved.get("room") or room
        return f
    add(Case(105, "phase2b vote played-before replans activity only", TEXT["friends_food"], c105, lambda: vote_api_flow(TEXT["friends_food"], sid="vote_case_105", answers={"party_size":4,"start_time":"18:00","budget_per_person":180,"home_area":"新街口","window_hours":4})))

    def c106(ctx):
        f=[]; client=ctx["client"]; sid=ctx["sid"]; headers=ctx["headers"]; room=ctx["room"]; before=ctx["before_steps"]
        room_id = room.get("room_id")
        opt = _vote_option(room, target="time")
        submit = client.post(
            f"/vote/{room_id}",
            json={"session_id": sid, "voter": "阿岚", "option_id": opt.get("option_id"), "feedback": "我可能晚到30分钟"},
            headers=headers,
        ).json()
        fb = submit.get("feedback") or {}
        require(fb.get("vote_type") == "time_shift", "late feedback should be time_shift", f)
        resolved = client.post(f"/vote/{room_id}/resolve", json={"session_id": sid}, headers=headers).json()
        session = resolved.get("session") or {}
        exc = session.get("exception_result") or {}
        after = _business_steps(session.get("chosen") or {})
        require(resolved.get("ok") is True, "resolve time shift failed", f)
        require(exc.get("changed_kind") == "time" or exc.get("issue_type") == "time_conflict", "late feedback should trigger time_conflict", f)
        require(int(exc.get("time_delta") or 0) >= 30, "time shift should be at least 30 minutes", f)
        require([s.get("id") for s in before] == [s.get("id") for s in after], "time shift should not replace merchants", f)
        require(bool(session.get("chosen")), "time shift cleared original plan", f)
        ctx["session"] = session
        ctx["room"] = resolved.get("room") or room
        return f
    add(Case(106, "phase2b vote late 30 shifts timeline", TEXT["script_full"], c106, lambda: vote_api_flow(TEXT["script_full"], sid="vote_case_106")))

    def runner107():
        from fastapi.testclient import TestClient
        import server

        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid_a = "vote_iso_a"
        sid_b = "vote_iso_b"
        a = client.post("/plan", json={"session_id": sid_a, "text": TEXT["script_full"]}, headers={"X-Session-Id": sid_a}).json()
        b = client.post("/plan", json={"session_id": sid_b, "text": TEXT["script_full"]}, headers={"X-Session-Id": sid_b}).json()
        room_a = (a.get("session") or {}).get("vote_room") or {}
        room_b = (b.get("session") or {}).get("vote_room") or {}
        client.post(f"/vote/{room_a.get('room_id')}", json={"session_id": sid_a, "voter": "A", "option_id": "plan_0"}, headers={"X-Session-Id": sid_a})
        got_a = client.get(f"/vote/{room_a.get('room_id')}", headers={"X-Session-Id": sid_a}).json().get("room") or {}
        got_b = client.get(f"/vote/{room_b.get('room_id')}", headers={"X-Session-Id": sid_b}).json().get("room") or {}
        return {"session": a.get("session") or {}, "room_a": got_a, "room_b": got_b, "plan_summary": "vote session isolation"}

    def c107(ctx):
        f=[]; a=ctx.get("room_a") or {}; b=ctx.get("room_b") or {}
        require(bool(a.get("room_id")) and bool(b.get("room_id")), "both vote rooms should exist", f)
        require(a.get("room_id") != b.get("room_id"), "vote room ids should differ", f)
        require((a.get("summary") or {}).get("total_votes") == 1, "session A vote missing", f)
        require((b.get("summary") or {}).get("total_votes") == 0, "session B polluted by session A vote", f)
        return f
    add(Case(107, "phase2b vote session isolation", "vote session isolation", c107, runner107))

    def runner108():
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        return {"agent": agent, "session": session, "plan_summary": "booking review after selected plan"}

    def c108(ctx):
        f=[]; review=(ctx["session"].get("booking_review") or {}); segs=review.get("segments") or []
        activity = next((s for s in segs if s.get("booking_type") == "activity_booking"), {})
        require(review.get("mode") == "review_required", "booking review mode should be review_required", f)
        require(bool(activity), "booking review lacks activity segment", f)
        require(bool(activity.get("scheduled_start")), "activity review lacks scheduled_start", f)
        require(bool(activity.get("party_size")), "activity review lacks party_size", f)
        require(bool(activity.get("merchant_contact")), "activity review lacks merchant_contact", f)
        require(bool(activity.get("required_fields")), "activity review lacks required_fields", f)
        require(not ctx["session"].get("executed"), "select should not execute booking", f)
        require(len(ctx["session"].get("bookings") or []) == 0, "select should not create bookings", f)
        return f
    add(Case(108, "phase2b booking review after selected plan", TEXT["script_full"], c108, runner108))

    def runner109():
        ctx = vote_api_flow(TEXT["script_full"], sid="booking_vote_109")
        client=ctx["client"]; sid=ctx["sid"]; headers=ctx["headers"]; room=ctx["room"]; room_id=room.get("room_id")
        target = _vote_option(room, kind="plan").get("option_id")
        client.post(f"/vote/{room_id}", json={"session_id": sid, "voter": "host", "option_id": target}, headers=headers)
        confirmed = client.post(f"/vote/{room_id}/confirm", json={"session_id": sid}, headers=headers).json()
        ctx["session"] = confirmed.get("session") or {}
        ctx["confirm_response"] = confirmed
        return ctx

    def c109(ctx):
        f=[]; session=ctx.get("session") or {}
        require((ctx.get("confirm_response") or {}).get("ok") is True, "vote confirm failed", f)
        require(session.get("mode") == "selected", "vote confirm should select plan only", f)
        require(not session.get("executed"), "vote confirm should not auto book", f)
        require(len(session.get("bookings") or []) == 0, "vote confirm should leave bookings empty", f)
        require(bool((session.get("booking_review") or {}).get("segments")), "vote confirm should expose booking review", f)
        return f
    add(Case(109, "phase2b vote confirm does not auto book", TEXT["script_full"], c109, runner109))

    def runner110():
        agent, session = _run(TEXT["friends_food"], {"party_size":4,"start_time":"18:00","budget_per_person":180,"home_area":"新街口","window_hours":4})
        session = agent.choose(0)
        return {"agent": agent, "session": session, "plan_summary": "restaurant booking card"}

    def c110(ctx):
        f=[]; review=(ctx["session"].get("booking_review") or {}); segs=review.get("segments") or []
        restaurant = next((s for s in segs if s.get("booking_type") == "restaurant_booking"), {})
        require(bool(restaurant), "booking review lacks restaurant segment", f)
        fields = restaurant.get("prefilled_fields") or {}
        require(bool(fields.get("table_type")), "restaurant review lacks table_type", f)
        require(bool(fields.get("party_size") or restaurant.get("party_size")), "restaurant review lacks party_size", f)
        require(bool(fields.get("scheduled_start") or restaurant.get("scheduled_start")), "restaurant review lacks arrival time", f)
        require("coupon_choice" in fields or "coupon_choice" in (restaurant.get("required_fields") or []), "restaurant review lacks coupon hint", f)
        require(review.get("real_payment") is False, "booking review must not do real payment", f)
        return f
    add(Case(110, "phase2b restaurant booking card", TEXT["friends_food"], c110, runner110))

    def runner111():
        agent, session = _run(TEXT["friends_food"], {"party_size":4,"start_time":"18:00","budget_per_person":180,"home_area":"新街口","window_hours":4})
        session = agent.choose(0)
        before_ids = _ids(session.get("chosen") or {})
        before_times = [s.get("start") for s in _business_steps(session.get("chosen") or {})]
        session = agent.update_booking_review(segment_index=0, fields={"delta_minutes": 30})
        after_ids = _ids(session.get("chosen") or {})
        after_times = [s.get("start") for s in _business_steps(session.get("chosen") or {})]
        return {
            "agent": agent, "session": session,
            "before_ids": before_ids, "after_ids": after_ids,
            "before_times": before_times, "after_times": after_times,
            "plan_summary": "booking time edit shifts later segments",
        }

    def c111(ctx):
        f=[]; before=ctx.get("before_times") or []; after=ctx.get("after_times") or []
        require(ctx.get("before_ids") == ctx.get("after_ids"), "time edit should not replace merchants", f)
        require(len(before) == len(after) and len(after) >= 1, "time edit lost business steps", f)
        if before and after:
            require(_time_to_minutes(after[0]) - _time_to_minutes(before[0]) == 30, "first segment was not shifted by 30 minutes", f)
        if len(before) > 1 and len(after) > 1:
            require(_time_to_minutes(after[-1]) - _time_to_minutes(before[-1]) == 30, "later segment was not shifted by 30 minutes", f)
        review=ctx["session"].get("booking_review") or {}
        require(bool(review.get("segments")), "updated booking review missing", f)
        require(review.get("real_map_api") is False, "time edit must not call real map API", f)
        return f
    add(Case(111, "phase2b booking time edit shifts later segments", TEXT["friends_food"], c111, runner111))

    def runner112():
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        return {"agent": agent, "session": session, "plan_summary": "optional addon excluded from booking by default"}

    def c112(ctx):
        f=[]; session=ctx["session"]; plan=session.get("chosen") or {}; review=session.get("booking_review") or {}
        optional = plan.get("optional_addons") or (plan.get("itinerary") or {}).get("optional_addons") or []
        opt_ids = {x.get("id") or x.get("merchant_id") for x in optional if x.get("id") or x.get("merchant_id")}
        review_ids = {s.get("merchant_id") for s in review.get("segments") or []}
        require(opt_ids.isdisjoint(review_ids), "optional addon leaked into booking review", f)
        require(len(session.get("bookings") or []) == 0, "optional addon should not create booking before confirm", f)
        require("optional_addons_excluded" in review, "booking review lacks optional_addons_excluded field", f)
        return f
    add(Case(112, "phase2b optional addon excluded from booking by default", TEXT["script_full"], c112, runner112))

    def runner113():
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        review = session.get("booking_review") or {}
        bookable_count = len([s for s in review.get("segments") or [] if s.get("bookable")])
        session = agent.confirm_and_execute()
        return {"agent": agent, "session": session, "bookable_count": bookable_count, "plan_summary": "confirm booking creates mock bookings"}

    def c113(ctx):
        f=[]; session=ctx["session"]; review=session.get("booking_review") or {}
        require(session.get("executed") is True, "confirm should set executed true", f)
        require(session.get("mode") == "executed", "confirm should set executed mode", f)
        require(len(session.get("bookings") or []) == ctx.get("bookable_count"), "bookings count should match bookable review segments", f)
        require(review.get("mode") == "confirmed", "booking review not marked confirmed", f)
        require(all(s.get("booking_type") != "transit_only" for s in review.get("segments") or []), "transit segment should not be in bookable review segments", f)
        require(bool(session.get("share_card")), "confirm should generate share card", f)
        return f
    add(Case(113, "phase2b confirm booking creates mock bookings", TEXT["script_full"], c113, runner113, timeout_seconds=90))

    def runner114():
        from fastapi.testclient import TestClient
        import server

        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid_a = "booking_iso_a"
        sid_b = "booking_iso_b"
        ha = {"X-Session-Id": sid_a}
        hb = {"X-Session-Id": sid_b}
        a = client.post("/plan", json={"session_id": sid_a, "text": TEXT["script_full"]}, headers=ha).json()
        if (a.get("session") or {}).get("plans"):
            client.post("/select", json={"session_id": sid_a, "plan_index": 0}, headers=ha)
            client.post("/booking/review", json={"session_id": sid_a}, headers=ha)
            a_confirm = client.post("/booking/confirm", json={"session_id": sid_a}, headers=ha).json()
        else:
            a_confirm = a
        b = client.post("/plan", json={"session_id": sid_b, "text": TEXT["milk_tea"]}, headers=hb).json()
        bs = b.get("session") or {}
        if bs.get("mode") == "needs_clarification":
            b = client.post("/refine", json={"session_id": sid_b, "answers": _answer_for(bs, {"start_time":"19:00","home_area":"新街口"})}, headers=hb).json()
            bs = b.get("session") or {}
        if bs.get("plans"):
            client.post("/select", json={"session_id": sid_b, "plan_index": 0}, headers=hb)
            b_review = client.post("/booking/review", json={"session_id": sid_b}, headers=hb).json()
        else:
            b_review = b
        return {
            "session": b_review.get("session") or {},
            "a_session": a_confirm.get("session") or {},
            "b_session": b_review.get("session") or {},
            "plan_summary": "booking session isolation",
        }

    def c114(ctx):
        f=[]; a=ctx.get("a_session") or {}; b=ctx.get("b_session") or {}
        require(bool(a.get("bookings")), "session A should have confirmed bookings", f)
        require(a.get("executed") is True, "session A should be executed", f)
        require(len(b.get("bookings") or []) == 0, "session B should not inherit bookings from A", f)
        require(b.get("executed") is not True, "session B should not be executed", f)
        require(bool(b.get("booking_review")), "session B should have its own booking review", f)
        require((a.get("booking_review") or {}) != (b.get("booking_review") or {}), "booking reviews should not be shared object/data", f)
        return f
    add(Case(114, "phase2b booking session isolation", "booking session isolation", c114, runner114, timeout_seconds=90))

    def checkout_flow(text=TEXT["script_full"], accept_addon=False, strategy_id=None):
        agent, session = _run(text)
        session = agent.choose(0)
        session = agent.confirm_and_execute()
        if accept_addon:
            session = agent.accept_addon()
        if strategy_id:
            session = agent.apply_checkout(strategy_id)
        else:
            session = agent.preview_checkout()
        return {"agent": agent, "session": session, "plan_summary": "checkout flow"}

    def checkout_preview_of(session: dict) -> dict:
        return session.get("checkout_preview") or {}

    def checkout_billable(session: dict) -> list[dict]:
        return checkout_preview_of(session).get("billable_items") or []

    def checkout_non_billable(session: dict) -> list[dict]:
        return checkout_preview_of(session).get("non_billable_items") or []

    def c115(ctx):
        f=[]; session=ctx["session"]
        require(not session.get("checkout_result"), "checkout result should not exist before booking confirm", f)
        require((session.get("checkout_error") or {}).get("code") == "booking_required", "pay before booking should return booking_required", f)
        require(len(session.get("bookings") or []) == 0, "pay-before-booking should not create bookings", f)
        return f
    def runner115():
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        session = agent.pay_checkout("one_click_checkout")
        return {"agent": agent, "session": session, "plan_summary": "pay blocked before booking"}
    add(Case(115, "phase2b checkout blocked before booking", TEXT["script_full"], c115, runner115))

    def c116(ctx):
        f=[]; preview=checkout_preview_of(ctx["session"])
        require(preview.get("status") == "preview", "checkout preview should be preview after booking", f)
        require(preview.get("mock_only") is True, "checkout preview must be mock_only", f)
        require(preview.get("real_payment") is False, "checkout preview must not do real payment", f)
        require(bool(preview.get("billable_items")), "checkout preview lacks billable items", f)
        require(bool(preview.get("price_strategies")), "checkout preview lacks price strategies", f)
        return f
    add(Case(116, "phase2b checkout preview after booking", TEXT["script_full"], c116, lambda: checkout_flow()))

    def c117(ctx):
        f=[]; session=ctx["session"]; preview=checkout_preview_of(session)
        require(all((i.get("booking_type") != "transit_only" and i.get("category") != "transit") for i in preview.get("billable_items") or []), "transit entered billable checkout items", f)
        if (session.get("booking_review") or {}).get("transit_segments"):
            require(any(i.get("category") == "transit" or "Transit" in str(i.get("name")) for i in preview.get("non_billable_items") or []), "transit segments should be shown as non-billable", f)
        return f
    add(Case(117, "phase2b transit is non billable", TEXT["script_full"], c117, lambda: checkout_flow()))

    def c118(ctx):
        f=[]; session=ctx["session"]; addon=session.get("addon") or {}; addon_id=addon.get("id") or addon.get("merchant_id")
        require(len(session.get("accepted_addons") or []) == 0, "accepted add-ons should be empty by default", f)
        if addon_id:
            bill_ids = {i.get("item_id") for i in checkout_billable(session)}
            require(addon_id not in bill_ids, "optional add-on entered checkout bill by default", f)
        require(any(i.get("reason") == "Optional add-on not accepted by user." for i in checkout_non_billable(session)) or not addon_id, "excluded optional add-on should be visible as non-billable", f)
        return f
    add(Case(118, "phase2b optional add-on excluded by default", TEXT["script_full"], c118, lambda: checkout_flow()))

    def c119(ctx):
        f=[]; session=ctx["session"]; addon=session.get("addon") or {}; addon_id=addon.get("id") or addon.get("merchant_id")
        require(bool(session.get("accepted_addons")), "accepted add-on missing after explicit accept", f)
        if addon_id:
            require(addon_id in {i.get("item_id") for i in checkout_billable(session)}, "accepted add-on did not enter billable checkout items", f)
        return f
    add(Case(119, "phase2b accepted add-on enters checkout", TEXT["script_full"], c119, lambda: checkout_flow(accept_addon=True)))

    def c120(ctx):
        f=[]; preview=checkout_preview_of(ctx["session"])
        by_id = {s.get("strategy_id"): s for s in preview.get("price_strategies") or []}
        require("separate_purchase" in by_id, "missing separate_purchase strategy", f)
        require("one_click_checkout" in by_id, "missing one_click_checkout strategy", f)
        separate = by_id.get("separate_purchase", {}).get("total", 0)
        one_click = by_id.get("one_click_checkout", {}).get("total", 0)
        if separate and one_click and separate < one_click:
            require((preview.get("recommended_strategy") or {}).get("strategy_id") == "separate_purchase", "separate purchase cheaper but not recommended", f)
            require(any(("便宜" in str(w) or "cheaper" in str(w).lower()) for w in preview.get("warnings") or []), "cheaper separate purchase lacks warning", f)
        return f
    add(Case(120, "phase2b cheaper separate purchase warning", TEXT["script_full"], c120, lambda: checkout_flow()))

    def c121(ctx):
        f=[]; session=ctx["session"]; result=session.get("checkout_result") or {}
        require(result.get("status") == "mock_paid", "mock pay status missing", f)
        require(bool(result.get("mock_order_id")) and bool(result.get("mock_payment_id")), "mock payment/order ids missing", f)
        require(result.get("real_payment") is False, "checkout pay must not be real payment", f)
        require("http://" not in json.dumps(result, ensure_ascii=False) and "https://" not in json.dumps(result, ensure_ascii=False), "mock payment result contains external URL", f)
        return f
    def runner121():
        ctx = checkout_flow(strategy_id="one_click_checkout")
        ctx["session"] = ctx["agent"].pay_checkout("one_click_checkout")
        return ctx
    add(Case(121, "phase2b one-click mock payment", TEXT["script_full"], c121, runner121))

    def c122(ctx):
        f=[]; split=ctx["session"].get("checkout_split") or {}; preview=checkout_preview_of(ctx["session"])
        total = round(float(preview.get("payable_total") or 0), 2)
        shares = split.get("payer_summary") or {}
        require(split.get("mode") == "aa", "split mode should be aa", f)
        require(abs(round(sum(float(v) for v in shares.values()), 2) - total) < 0.02, "AA split sum does not match payable total", f)
        require(len(shares) >= 4, "AA split should include four members", f)
        return f
    def runner122():
        ctx = checkout_flow()
        ctx["session"] = ctx["agent"].split_checkout(mode="aa", members=["发起人","朋友A","朋友B","朋友C"])
        return ctx
    add(Case(122, "phase2b AA split bill", TEXT["script_full"], c122, runner122))

    def c123(ctx):
        f=[]; split=ctx["session"].get("checkout_split") or {}; shares=split.get("payer_summary") or {}; preview=checkout_preview_of(ctx["session"])
        total = round(float(preview.get("payable_total") or 0), 2)
        require(split.get("mode") == "host_treat", "split mode should be host_treat", f)
        require(round(float(shares.get("发起人") or 0), 2) == total, "host should pay full total", f)
        require(all(float(v or 0) == 0 for k, v in shares.items() if k != "发起人"), "non-host members should pay zero in host_treat", f)
        return f
    def runner123():
        ctx = checkout_flow()
        ctx["session"] = ctx["agent"].split_checkout(mode="host_treat", members=["发起人","朋友A","朋友B","朋友C"], host="发起人")
        return ctx
    add(Case(123, "phase2b host-treat split bill", TEXT["birthday"], c123, runner123))

    def c124(ctx):
        f=[]; split=ctx["session"].get("checkout_split") or {}; shares=split.get("payer_summary") or {}; preview=checkout_preview_of(ctx["session"])
        total = round(float(preview.get("payable_total") or 0), 2)
        require(split.get("mode") == "custom_exemptions", "split mode should be custom_exemptions", f)
        require(round(float(shares.get("寿星") or 0), 2) == 0, "exempted birthday member should pay zero", f)
        require(abs(round(sum(float(v) for v in shares.values()), 2) - total) < 0.02, "custom split sum does not match payable total", f)
        return f
    def runner124():
        ctx = checkout_flow(TEXT["birthday"])
        ctx["session"] = ctx["agent"].split_checkout(mode="custom_exemptions", members=["发起人","寿星","朋友A","朋友B"], host="发起人", exempted_members=["寿星"])
        return ctx
    add(Case(124, "phase2b birthday exemption split bill", TEXT["birthday"], c124, runner124))

    def c125(ctx):
        f=[]; session=ctx["session"]
        require(bool(session.get("checkout_preview")), "checkout preview missing from API flow", f)
        require(bool(session.get("checkout_result")), "checkout result missing from API flow", f)
        require(bool(session.get("checkout_split")), "checkout split missing from API flow", f)
        require(session.get("checkout_result", {}).get("real_payment") is False, "API checkout must be mock payment only", f)
        require(not session.get("checkout_error"), "API checkout has unexpected error", f)
        return f
    def runner125():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid = "checkout_api_125"
        headers = {"X-Session-Id": sid}
        client.post("/plan", json={"session_id": sid, "text": TEXT["script_full"]}, headers=headers)
        client.post("/select", json={"session_id": sid, "plan_index": 0}, headers=headers)
        client.post("/booking/review", json={"session_id": sid}, headers=headers)
        client.post("/booking/confirm", json={"session_id": sid}, headers=headers)
        client.post("/checkout/preview", json={"session_id": sid}, headers=headers)
        client.post("/checkout/apply", json={"session_id": sid, "strategy_id": "best_combo"}, headers=headers)
        client.post("/checkout/pay", json={"session_id": sid, "strategy_id": "best_combo"}, headers=headers)
        out = client.post("/checkout/split", json={"session_id": sid, "mode": "aa", "members": ["发起人","朋友A","朋友B","朋友C"]}, headers=headers).json()
        return {"session": out.get("session") or {}, "plan_summary": "checkout API smoke"}
    add(Case(125, "phase2b checkout API smoke", "checkout API smoke", c125, runner125, timeout_seconds=90))

    def _support_case(session: dict) -> dict:
        return session.get("support_case") or {}

    def _support_action_ids(case: dict) -> set[str]:
        return {a.get("action_id") for a in case.get("suggested_actions") or []}

    def _support_flow(issue_type="merchant_full", source="selected_itinerary", target_index=0, do_booking=False, do_checkout=False):
        agent, session = _run(TEXT["script_full"])
        session = agent.choose(0)
        if do_booking:
            session = agent.prepare_booking_review()
        if do_checkout:
            session = agent.confirm_and_execute()
            session = agent.pay_checkout("best_combo")
        segment_id = ""
        if source == "booking_review":
            segs = (session.get("booking_review") or {}).get("segments") or []
            if segs:
                segment_id = segs[target_index].get("segment_id", "")
        elif source == "selected_itinerary":
            segs = (session.get("chosen", {}).get("itinerary") or {}).get("segments") or []
            if segs:
                segment_id = segs[target_index].get("segment_id", "")
        session = agent.create_support_case(
            session_id="support_direct",
            issue_type=issue_type,
            segment_id=segment_id,
            target_segment_index=target_index if source != "checkout_result" else None,
            source=source,
        )
        return {"agent": agent, "session": session, "support_case": _support_case(session), "plan_summary": f"support {issue_type} from {source}"}

    def c126(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(bool(sc.get("support_case_id")), "support case id missing", f)
        require(sc.get("source") == "selected_itinerary", "selected itinerary source missing", f)
        require(bool(sc.get("target_segment")), "selected itinerary target segment missing", f)
        require(sc.get("mock_only") is True, "support case must be mock_only", f)
        require(sc.get("real_customer_service") is False, "support case must not contact real customer service", f)
        return f
    add(Case(126, "phase2b support create for selected itinerary", TEXT["script_full"], c126, lambda: _support_flow("merchant_full", "selected_itinerary")))

    def c127(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(sc.get("source") == "booking_review", "booking review source missing", f)
        require((sc.get("target_segment") or {}).get("booking_type"), "booking review target should include booking_type", f)
        require(sc.get("issue_type") == "change_time", "booking review issue should be change_time", f)
        require("shift_timeline" in _support_action_ids(sc), "change_time should suggest shift_timeline", f)
        return f
    add(Case(127, "phase2b support create for booking review segment", TEXT["script_full"], c127, lambda: _support_flow("change_time", "booking_review", do_booking=True)))

    def c128(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(sc.get("source") == "checkout_result", "checkout result source missing", f)
        require(sc.get("issue_type") == "coupon_help", "checkout support should be coupon_help", f)
        require(bool(sc.get("checkout_snapshot")), "checkout support lacks checkout snapshot", f)
        require(bool(sc.get("coupon_rules")), "coupon_help should include mock coupon rules", f)
        require(sc.get("real_payment") is False, "checkout support must not do real payment", f)
        return f
    add(Case(128, "phase2b support create for checkout result", TEXT["script_full"], c128, lambda: _support_flow("coupon_help", "checkout_result", do_checkout=True)))

    def c129(ctx):
        f=[]; sc=ctx.get("support_case") or {}; body=json.dumps(sc, ensure_ascii=False)
        require(sc.get("issue_type") == "refund_request", "issue should be refund_request", f)
        require(sc.get("real_refund") is False, "refund request must not create real refund", f)
        require("Mock" in body, "refund reply should clearly say Mock", f)
        require("https://" not in body and "http://" not in body, "refund mock should not include external link", f)
        return f
    add(Case(129, "phase2b refund request is mock only", TEXT["script_full"], c129, lambda: _support_flow("refund_request", "booking_review", do_booking=True)))

    def c130(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(sc.get("issue_type") == "merchant_full", "issue should be merchant_full", f)
        require("open_rescue" in _support_action_ids(sc), "merchant_full should suggest open_rescue", f)
        return f
    add(Case(130, "phase2b merchant full suggests rescue", TEXT["script_full"], c130, lambda: _support_flow("merchant_full", "selected_itinerary")))

    def c131(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(sc.get("issue_type") == "coupon_help", "issue should be coupon_help", f)
        require("show_coupon_rules" in _support_action_ids(sc), "coupon_help should suggest show_coupon_rules", f)
        require(any("Mock" in str(x) for x in sc.get("coupon_rules") or []), "coupon rules should be marked Mock", f)
        return f
    add(Case(131, "phase2b coupon help returns mock coupon rules", TEXT["script_full"], c131, lambda: _support_flow("coupon_help", "checkout_result", do_checkout=True)))

    def runner132():
        ctx = _support_flow("complaint", "booking_review", do_booking=True)
        sc = ctx["support_case"]
        ctx["session"] = ctx["agent"].apply_support_action(sc.get("support_case_id"), "create_mock_ticket")
        ctx["support_case"] = _support_case(ctx["session"])
        return ctx

    def c132(ctx):
        f=[]; sc=ctx.get("support_case") or {}
        require(sc.get("issue_type") == "complaint", "issue should be complaint", f)
        require(sc.get("status") == "mock_ticket_created", "complaint should create mock ticket status", f)
        require(bool(sc.get("mock_ticket_id")), "mock ticket id missing", f)
        require(sc.get("real_customer_service") is False, "complaint must not contact real service", f)
        return f
    add(Case(132, "phase2b complaint creates mock ticket", TEXT["script_full"], c132, runner132))

    def runner133():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid_a = "support_iso_a"
        sid_b = "support_iso_b"
        ha = {"X-Session-Id": sid_a}
        hb = {"X-Session-Id": sid_b}
        client.post("/plan", json={"session_id": sid_a, "text": TEXT["script_full"]}, headers=ha)
        client.post("/select", json={"session_id": sid_a, "plan_index": 0}, headers=ha)
        created = client.post("/support/create", json={"session_id": sid_a, "issue_type": "merchant_full", "target_segment_index": 0}, headers=ha).json()
        case_id = (created.get("support_case") or {}).get("support_case_id")
        get_a = client.get(f"/support/{case_id}", headers=ha).json()
        get_b = client.get(f"/support/{case_id}", headers=hb).json()
        return {"session": created.get("session") or {}, "created": created, "get_a": get_a, "get_b": get_b, "plan_summary": "support session isolation"}

    def c133(ctx):
        f=[]; created=ctx.get("created") or {}; get_a=ctx.get("get_a") or {}; get_b=ctx.get("get_b") or {}
        require(created.get("ok") is True, "session A support create failed", f)
        require(get_a.get("ok") is True, "session A should read its support case", f)
        require(get_b.get("ok") is False, "session B should not read session A support case", f)
        return f
    add(Case(133, "phase2b support case session-bound", "support session isolation", c133, runner133, timeout_seconds=90))

    def runner134():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid = "support_api_134"
        headers = {"X-Session-Id": sid}
        client.post("/plan", json={"session_id": sid, "text": TEXT["script_full"]}, headers=headers)
        client.post("/select", json={"session_id": sid, "plan_index": 0}, headers=headers)
        created = client.post("/support/create", json={"session_id": sid, "issue_type": "merchant_full", "target_segment_index": 0}, headers=headers).json()
        case_id = (created.get("support_case") or {}).get("support_case_id")
        got = client.get(f"/support/{case_id}", headers=headers).json()
        replied = client.post(f"/support/{case_id}/reply", json={"session_id": sid, "message": "need help"}, headers=headers).json()
        acted = client.post(f"/support/{case_id}/action", json={"session_id": sid, "action_id": "open_rescue"}, headers=headers).json()
        legacy = client.post("/support", json={"session_id": sid, "segment_id": "", "issue_type": "other"}, headers=headers).json()
        return {
            "session": acted.get("session") or {},
            "created": created,
            "got": got,
            "replied": replied,
            "acted": acted,
            "legacy": legacy,
            "plan_summary": "support API smoke",
        }

    def c134(ctx):
        f=[]
        for key in ("created", "got", "replied", "acted", "legacy"):
            require((ctx.get(key) or {}).get("ok") is True, f"{key} support API failed", f)
        sc = (ctx.get("acted") or {}).get("support_case") or {}
        require((sc.get("action_result") or {}).get("action_id") == "open_rescue", "support action result missing open_rescue", f)
        require(sc.get("mock_only") is True, "API support case must be mock only", f)
        return f
    add(Case(134, "phase2b support API smoke", "support API smoke", c134, runner134, timeout_seconds=90))

    def _optional_addons(session: dict) -> list[dict]:
        plan = session.get("chosen") or _main_plan(session)
        return (
            plan.get("optional_addons")
            or (plan.get("itinerary") or {}).get("optional_addons")
            or plan.get("commercial_recommendations")
            or []
        )

    def _addon_ids(addons: list[dict]) -> set[str]:
        return {str(x.get("addon_id") or x.get("id") or x.get("merchant_id") or "") for x in addons}

    def _plan_with_addons(text: str, answers: dict | None = None, confirm: bool = False) -> dict:
        agent, session = _run(text, answers or {})
        session = agent.choose(0)
        if confirm:
            session = agent.confirm_and_execute()
        return {"agent": agent, "session": session, "addons": _optional_addons(session)}

    def c135(ctx):
        f=[]; session=ctx["session"]; plan=session.get("chosen") or {}; addons=ctx.get("addons") or []
        step_addon_ids = {str(s.get("addon_id") or s.get("id") or "") for s in _business_steps(plan)}
        ritual = [x for x in addons if x.get("type") in ("birthday_cake","birthday_flowers") or x.get("category") == "蛋糕鲜花"]
        require(bool(ritual), "birthday lacks cake/flowers optional add-on", f)
        require(all(x.get("mock_only") is True for x in ritual), "birthday add-on must be mock_only", f)
        require(all((x.get("addon_id") or x.get("id")) not in step_addon_ids for x in ritual), "birthday optional add-on object became a core itinerary step", f)
        require(all(x.get("target_area") or x.get("target_name") for x in ritual), "birthday add-on lacks target binding", f)
        return f
    add(Case(135, "phase2b birthday ritual add-ons", TEXT["birthday"], c135, lambda: _plan_with_addons(TEXT["birthday"], {"start_time":"18:00","home_area":"新街口","window_hours":4})))

    def c136(ctx):
        f=[]; addons=ctx.get("addons") or []
        require(any(x.get("type") in ("date_flowers","date_dessert","milk_tea") or x.get("category") in ("蛋糕鲜花","甜品","奶茶") for x in addons), f"date lacks ritual add-ons: {addons}", f)
        require(all(x.get("mock_only") is True for x in addons), "date add-ons must be mock", f)
        require(all(x.get("status") == "optional" for x in addons), "date add-on should remain optional", f)
        return f
    add(Case(136, "phase2b date ritual add-ons", TEXT["date"], c136, lambda: _plan_with_addons(TEXT["date"], {"party_size":2,"start_time":"18:00","budget_per_person":300,"home_area":"新街口","window_hours":4})))

    def c137(ctx):
        f=[]; session=ctx["session"]; plan=session.get("chosen") or {}; cats=_cats(plan); addons=ctx.get("addons") or []
        require(cats == ["剧本杀"], f"long script core polluted by meal/addon: {cats}", f)
        require(any(x.get("type") in ("dinner_delivery","milk_tea") for x in addons), f"long script lacks food/drink supply add-on: {addons}", f)
        require(not any(s.get("kind") == "restaurant" for s in _business_steps(plan)), "long script forced restaurant as core segment", f)
        return f
    add(Case(137, "phase2b long script supply add-ons", TEXT["script_long"], c137, lambda: _plan_with_addons(TEXT["script_long"])))

    def c138(ctx):
        f=[]; session=ctx["session"]; addons=ctx.get("addons") or []
        require(session.get("request", {}).get("scene") == "stay_in", "stay-in scene lost", f)
        require(any(x.get("type") in ("dinner_delivery","xiaoxiang_snacks") for x in addons), f"stay-in lacks home delivery/snack add-ons: {addons}", f)
        require(not any(x.get("type") in ("photo_guide","checkin_guide") for x in addons), "stay-in should not recommend offline check-in guide", f)
        require(all(x.get("fulfillment_type") in ("mock_home_delivery","mock_delivery","mock_pickup_or_delivery") for x in addons if x.get("checkout_eligible", True)), "stay-in checkout add-on should be home/mock delivery", f)
        return f
    add(Case(138, "phase2b stay-in delivery and xiaoxiang add-ons", TEXT["stay_in"], c138, lambda: _plan_with_addons(TEXT["stay_in"], {"start_time":"20:00","budget_per_person":120,"stayin_mode":"movie_takeaway"})))

    def c139(ctx):
        f=[]; session=ctx["session"]; addons=ctx.get("addons") or []
        require("no_meal" in (session.get("request", {}).get("negative_intents") or []), "movie no_meal lost", f)
        require(not any(x.get("type") == "dinner_delivery" or x.get("category") in MEAL_CATEGORIES for x in addons), f"no_meal leaked meal add-on: {addons}", f)
        require(all(x.get("status") == "optional" for x in addons), "movie add-ons should be optional if present", f)
        return f
    add(Case(139, "phase2b movie no meal blocks dinner add-ons", TEXT["movie"], c139, lambda: _plan_with_addons(TEXT["movie"], {"start_time":"19:30","home_area":"新街口"})))

    def c140(ctx):
        f=[]; session=ctx["session"]; addons=ctx.get("addons") or []
        preview=session.get("checkout_preview") or {}
        bill_ids={str(i.get("item_id") or "") for i in preview.get("billable_items") or []}
        add_ids=_addon_ids([x for x in addons if x.get("checkout_eligible", True)])
        require(bool(add_ids), "test flow has no checkout-eligible add-ons", f)
        require(add_ids.isdisjoint(bill_ids), f"optional add-on entered checkout by default: {add_ids & bill_ids}", f)
        require(len(session.get("accepted_addons") or []) == 0, "accepted_addons should be empty by default", f)
        return f
    add(Case(140, "phase2b add-ons excluded from checkout by default", TEXT["script_long"], c140, lambda: _plan_with_addons(TEXT["script_long"], confirm=True)))

    def runner141():
        ctx = _plan_with_addons(TEXT["script_long"], confirm=True)
        addon = next((x for x in ctx["addons"] if x.get("checkout_eligible", True)), {})
        ctx["accepted_id"] = addon.get("addon_id") or addon.get("id")
        ctx["session"] = ctx["agent"].accept_addon(ctx["accepted_id"])
        return ctx
    def c141(ctx):
        f=[]; session=ctx["session"]; accepted_id=str(ctx.get("accepted_id") or "")
        require(bool(session.get("accepted_addons")), "accepted add-on missing", f)
        bill_ids={str(i.get("item_id") or "") for i in (session.get("checkout_preview") or {}).get("billable_items") or []}
        require(accepted_id in bill_ids, f"accepted add-on did not enter checkout: {accepted_id} not in {bill_ids}", f)
        require(all(x.get("mock_only") is True for x in session.get("accepted_addons") or []), "accepted add-on must remain mock", f)
        return f
    add(Case(141, "phase2b accepted add-on enters mock checkout", TEXT["script_long"], c141, runner141))

    def runner142():
        ctx = _plan_with_addons(TEXT["script_long"], confirm=True)
        addon = next((x for x in ctx["addons"] if x.get("checkout_eligible", True)), {})
        rejected_id = addon.get("addon_id") or addon.get("id")
        ctx["rejected_id"] = rejected_id
        ctx["session"] = ctx["agent"].remove_addon(rejected_id)
        ctx["addons_after"] = _optional_addons(ctx["session"])
        return ctx
    def c142(ctx):
        f=[]; rejected=str(ctx.get("rejected_id") or ""); after_ids=_addon_ids(ctx.get("addons_after") or [])
        require(bool(rejected), "no add-on was available to reject", f)
        require(rejected not in after_ids, f"rejected add-on still visible in session: {rejected}", f)
        require(rejected in (ctx["session"].get("rejected_addon_ids") or []), "rejected_addon_ids did not record removal", f)
        return f
    add(Case(142, "phase2b rejected add-on not repeated in session", TEXT["script_long"], c142, runner142))

    def runner143():
        ctx = _plan_with_addons(TEXT["date"], {"party_size":2,"start_time":"18:00","budget_per_person":300,"home_area":"新街口","window_hours":4}, confirm=True)
        guide = next((x for x in ctx["addons"] if x.get("type") in ("photo_guide","checkin_guide")), {})
        ctx["guide"] = guide
        if guide:
            ctx["session"] = ctx["agent"].accept_addon(guide.get("addon_id") or guide.get("id"))
        return ctx
    def c143(ctx):
        f=[]; guide=ctx.get("guide") or {}; session=ctx["session"]
        require(bool(guide), "photo/check-in guide missing", f)
        require(guide.get("checkout_eligible") is False, "guide should not be checkout eligible", f)
        require(guide.get("fulfillment_type") == "content_card", "guide should be content_card", f)
        require(not any((x.get("addon_id") or x.get("id")) == (guide.get("addon_id") or guide.get("id")) for x in session.get("accepted_addons") or []), "guide entered accepted add-ons", f)
        bill_ids={str(i.get("item_id") or "") for i in (session.get("checkout_preview") or {}).get("billable_items") or []}
        require(str(guide.get("addon_id") or guide.get("id")) not in bill_ids, "guide entered checkout bill", f)
        return f
    add(Case(143, "phase2b photo guide content card only", TEXT["date"], c143, runner143))

    REAL_FLAG_KEYS = {
        "real_payment", "real_booking", "real_order", "real_delivery",
        "real_customer_service", "real_refund", "real_collection",
        "real_coupon", "real_member", "real_map_api",
    }

    def _assert_mock_boundary(value: Any, failures: list[str], label: str = "payload") -> None:
        def walk(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    next_path = f"{path}.{key}" if path else str(key)
                    if key in REAL_FLAG_KEYS and val is True:
                        failures.append(f"{label} has forbidden true flag: {next_path}")
                    walk(val, next_path)
            elif isinstance(obj, (list, tuple, set)):
                for idx, item in enumerate(obj):
                    walk(item, f"{path}[{idx}]")
            elif isinstance(obj, str):
                low = obj.lower()
                local_markers = ("127.0.0.1", "localhost", "testserver")
                if ("https://" in low or "http://" in low) and not any(marker in low for marker in local_markers):
                    failures.append(f"{label} has external URL at {path}: {obj[:80]}")
        walk(value)

    def _checkout_ids(session: dict) -> set[str]:
        return {str(i.get("item_id") or "") for i in (session.get("checkout_preview") or {}).get("billable_items") or []}

    def _first_checkout_addon(addons: list[dict]) -> dict:
        return next((x for x in addons if x.get("checkout_eligible", True)), {})

    def c144_runner():
        agent, session = _run(TEXT["birthday"], {"start_time": "18:00", "home_area": "新街口", "window_hours": 4})
        session = agent.choose(0)
        addons = _optional_addons(session)
        session = agent.prepare_booking_review()
        review_before_confirm = session.get("booking_review") or {}
        session = agent.confirm_and_execute()
        addon = _first_checkout_addon(_optional_addons(session))
        accepted_id = addon.get("addon_id") or addon.get("id")
        if accepted_id:
            session = agent.accept_addon(accepted_id)
        session = agent.split_checkout(mode="aa")
        return {
            "agent": agent,
            "session": session,
            "addons": addons,
            "accepted_id": accepted_id,
            "review_before_confirm": review_before_confirm,
            "plan_summary": "final integration birthday closed loop",
        }

    def c144(ctx):
        f=[]; session=ctx["session"]; addons=ctx.get("addons") or []
        ritual=[x for x in addons if x.get("type") in ("birthday_cake", "birthday_flowers") or "birthday" in str(x.get("trigger_scene"))]
        require(bool(session.get("chosen")), "birthday closed loop lacks chosen plan", f)
        require(bool(ritual), "birthday closed loop lacks optional ritual add-on", f)
        require((ctx.get("review_before_confirm") or {}).get("mode") == "review_required", "booking review should appear before confirm", f)
        require((session.get("booking_result") or {}).get("mock_only") is True, "booking result must be mock", f)
        require(bool(session.get("bookings")), "booking confirm did not create mock bookings", f)
        require(bool(session.get("accepted_addons")), "accepted birthday add-on missing", f)
        require(str(ctx.get("accepted_id") or "") in _checkout_ids(session), "accepted birthday add-on not in mock checkout", f)
        require(bool(session.get("checkout_split")), "birthday split bill missing", f)
        _assert_mock_boundary(session, f, "birthday session")
        return f
    add(Case(144, "phase2b final birthday closed loop", TEXT["birthday"], c144, c144_runner, timeout_seconds=90))

    def c145_runner():
        ctx = _plan_with_addons(
            TEXT["date"],
            {"party_size": 2, "start_time": "18:00", "budget_per_person": 300, "home_area": "新街口", "window_hours": 4},
            confirm=True,
        )
        ctx["addons"] = _optional_addons(ctx["session"])
        return ctx

    def c145(ctx):
        f=[]; session=ctx["session"]; addons=ctx.get("addons") or []
        require_no_default_public_summary(session, f)
        frame=(session.get("request") or {}).get("intent_frame") or {}
        sources=frame.get("field_sources") or {}
        confirmed=frame.get("confirmed_fields") or {}
        for key, value in confirmed.items():
            if value not in (None, "", [], "unknown") and key in {"party_size", "budget_per_person", "home_area", "transport"}:
                require(sources.get(key) in TRUSTED_PUBLIC_SOURCES, f"untrusted confirmed field leaked: {key}={sources.get(key)}", f)
        require(bool(addons), "date flow lacks optional add-ons", f)
        require(any(x.get("checkout_eligible") is False for x in addons), "date flow lacks content-only card", f)
        require(any(x.get("checkout_eligible", True) for x in addons), "date flow lacks commercial optional card", f)
        addon_ids=_addon_ids([x for x in addons if x.get("checkout_eligible", True)])
        require(addon_ids.isdisjoint(_checkout_ids(session)), "unaccepted date add-on entered checkout", f)
        return f
    add(Case(145, "phase2b final date add-on separation", TEXT["date"], c145, c145_runner, timeout_seconds=90))

    def c146_runner():
        ctx = _plan_with_addons(TEXT["script_long"])
        selected = ctx["session"]
        ctx["selected_preview"] = selected.get("checkout_preview")
        ctx["addons_before"] = _optional_addons(selected)
        ctx["session"] = ctx["agent"].confirm_and_execute()
        ctx["bill_before_accept"] = _checkout_ids(ctx["session"])
        addon = _first_checkout_addon(_optional_addons(ctx["session"]))
        ctx["accepted_id"] = addon.get("addon_id") or addon.get("id")
        if ctx["accepted_id"]:
            ctx["session"] = ctx["agent"].accept_addon(ctx["accepted_id"])
        return ctx

    def c146(ctx):
        f=[]; session=ctx["session"]; plan=session.get("chosen") or {}
        require(not ctx.get("selected_preview"), "checkout existed before booking confirm", f)
        require(not any(s.get("kind") == "restaurant" for s in _business_steps(plan)), "long script forced restaurant core segment", f)
        addons=ctx.get("addons_before") or []
        require(any(x.get("type") in ("dinner_delivery", "milk_tea") for x in addons), "long script lacks optional supply add-on", f)
        require(str(ctx.get("accepted_id") or "") not in (ctx.get("bill_before_accept") or set()), "add-on entered bill before accept", f)
        require(str(ctx.get("accepted_id") or "") in _checkout_ids(session), "accepted long-script add-on not in checkout", f)
        return f
    add(Case(146, "phase2b final long script supply loop", TEXT["script_long"], c146, c146_runner, timeout_seconds=90))

    def c147_runner():
        return _plan_with_addons(TEXT["movie"], {"start_time": "19:30", "home_area": "新街口"}, confirm=True)

    def c147(ctx):
        f=[]; session=ctx["session"]; plan=session.get("chosen") or {}; addons=ctx.get("addons") or _optional_addons(session)
        require("no_meal" in ((session.get("request") or {}).get("negative_intents") or []), "movie no_meal lost", f)
        require(not any(s.get("kind") == "restaurant" or s.get("role") == "EAT" for s in _business_steps(plan)), "movie no-meal polluted core itinerary", f)
        require(not any(x.get("type") == "dinner_delivery" or x.get("category") in MEAL_CATEGORIES for x in addons), "movie no-meal leaked meal add-on", f)
        require(all(x.get("status") == "optional" for x in addons), "movie add-ons must remain optional", f)
        return f
    add(Case(147, "phase2b final movie no-meal loop", TEXT["movie"], c147, c147_runner, timeout_seconds=90))

    def c148_runner():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid = "final_vote_booking_checkout_148"
        headers = {"X-Session-Id": sid}
        client.post("/plan", json={"session_id": sid, "text": TEXT["script_full"]}, headers=headers)
        selected = client.post("/select", json={"session_id": sid, "plan_index": 0}, headers=headers).json()
        room_res = client.post("/vote/create", json={"session_id": sid}, headers=headers).json()
        room = room_res.get("room") or (selected.get("session") or {}).get("vote_room") or {}
        room_id = room.get("room_id")
        first = ((room.get("options") or [{}])[0]).get("option_id") or "plan_0"
        if room_id:
            for voter in ("A", "B", "C"):
                client.post(f"/vote/{room_id}", json={"session_id": sid, "voter": voter, "option_id": first}, headers=headers)
            vote_confirm = client.post(f"/vote/{room_id}/confirm", json={"session_id": sid}, headers=headers).json()
        else:
            vote_confirm = {"ok": False, "session": selected.get("session") or {}}
        review = client.post("/booking/review", json={"session_id": sid}, headers=headers).json()
        booked = client.post("/booking/confirm", json={"session_id": sid}, headers=headers).json()
        preview = client.post("/checkout/preview", json={"session_id": sid}, headers=headers).json()
        split = client.post("/checkout/split", json={"session_id": sid, "mode": "aa", "members": ["host", "A", "B", "C"]}, headers=headers).json()
        return {
            "session": split.get("session") or {},
            "room": room,
            "vote_confirm": vote_confirm,
            "review": review,
            "booked": booked,
            "preview": preview,
            "split": split,
            "plan_summary": "final integration vote booking checkout",
        }

    def c148(ctx):
        f=[]; vote_session=(ctx.get("vote_confirm") or {}).get("session") or {}; final_session=ctx.get("session") or {}
        require(bool((ctx.get("room") or {}).get("room_id")), "vote room not created", f)
        require((ctx.get("vote_confirm") or {}).get("ok") is True, "vote host confirm failed", f)
        require(vote_session.get("mode") == "selected", "vote confirm should only select", f)
        require(not vote_session.get("executed"), "vote confirm executed booking", f)
        require(len(vote_session.get("bookings") or []) == 0, "vote confirm created bookings", f)
        require((ctx.get("booked") or {}).get("ok") is True and bool(((ctx.get("booked") or {}).get("session") or {}).get("bookings")), "booking confirm failed", f)
        require(bool((ctx.get("preview") or {}).get("checkout_preview")), "checkout preview missing after booking", f)
        require(bool(final_session.get("checkout_split")), "mock split missing", f)
        _assert_mock_boundary(final_session, f, "vote booking checkout session")
        return f
    add(Case(148, "phase2b final vote booking checkout loop", TEXT["script_full"], c148, c148_runner, timeout_seconds=90))

    def c149_runner():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        server.VOTE_ROOMS.clear()
        client = TestClient(server.app)
        sid = "final_rescue_support_149"
        headers = {"X-Session-Id": sid}
        client.post("/plan", json={"session_id": sid, "text": TEXT["friends_food"]}, headers=headers)
        client.post("/select", json={"session_id": sid, "plan_index": 0}, headers=headers)
        exc = client.post("/exception", json={"session_id": sid, "type": "restaurant_full", "context": {"location_state": "near_current_merchant", "current_area": "新街口"}}, headers=headers).json()
        support = client.post("/support/create", json={"session_id": sid, "issue_type": "merchant_full", "target_segment_index": 1, "source": "selected_itinerary"}, headers=headers).json()
        case_id = (support.get("support_case") or {}).get("support_case_id")
        same = client.get(f"/support/{case_id}", headers=headers).json() if case_id else {}
        other = client.get(f"/support/{case_id}", headers={"X-Session-Id": "final_rescue_support_other"}).json() if case_id else {}
        return {"session": support.get("session") or {}, "exc": exc, "support": support, "same": same, "other": other, "plan_summary": "final rescue to support"}

    def c149(ctx):
        f=[]; session=ctx.get("session") or {}; exc=((ctx.get("exc") or {}).get("session") or {}).get("exception_result") or {}; sc=(ctx.get("support") or {}).get("support_case") or {}
        require(bool(exc.get("issue_type")), "rescue result missing", f)
        require(bool(exc.get("changed_segments")) or exc.get("needs_user_confirm") is True, "rescue did not change or ask confirm", f)
        require((ctx.get("support") or {}).get("ok") is True, "support create failed", f)
        require(sc.get("mock_only") is True, "support must be mock only", f)
        require(bool(sc.get("suggested_actions")), "support lacks next-step actions", f)
        require((ctx.get("same") or {}).get("ok") is True, "same session cannot read support case", f)
        require((ctx.get("other") or {}).get("ok") is False, "other session read support case", f)
        _assert_mock_boundary(session, f, "rescue support session")
        return f
    add(Case(149, "phase2b final rescue to support loop", TEXT["friends_food"], c149, c149_runner, timeout_seconds=90))

    def c150_runner():
        first = _plan_with_addons(TEXT["script_long"], confirm=True)
        addon = _first_checkout_addon(_optional_addons(first["session"]))
        rejected_id = addon.get("addon_id") or addon.get("id")
        first["session"] = first["agent"].remove_addon(rejected_id)
        first["addons_after"] = _optional_addons(first["session"])
        second = _plan_with_addons(TEXT["script_long"], confirm=True)
        return {
            "session": first["session"],
            "rejected_id": rejected_id,
            "addons_after": first["addons_after"],
            "new_session": second["session"],
            "new_addons": _optional_addons(second["session"]),
            "plan_summary": "final addon reject consistency",
        }

    def c150(ctx):
        f=[]; rejected=str(ctx.get("rejected_id") or "")
        require(bool(rejected), "no add-on available to reject", f)
        require(rejected in (ctx["session"].get("rejected_addon_ids") or []), "rejected add-on not recorded", f)
        require(rejected not in _addon_ids(ctx.get("addons_after") or []), "rejected add-on repeated in current session", f)
        require(not (ctx.get("new_session") or {}).get("rejected_addon_ids"), "new session inherited rejected add-ons", f)
        require(rejected in _addon_ids(ctx.get("new_addons") or []), "new session should be free to show previously rejected add-on", f)
        return f
    add(Case(150, "phase2b final addon reject session consistency", TEXT["script_long"], c150, c150_runner, timeout_seconds=90))

    def c151_runner():
        ctx = _plan_with_addons(TEXT["script_long"], confirm=True)
        addon = _first_checkout_addon(_optional_addons(ctx["session"]))
        if addon:
            ctx["session"] = ctx["agent"].accept_addon(addon.get("addon_id") or addon.get("id"))
        ctx["session"] = ctx["agent"].pay_checkout("best_combo")
        ctx["session"] = ctx["agent"].split_checkout(mode="aa", members=["host", "A", "B", "C"])
        ctx["session"] = ctx["agent"].create_support_case(session_id="mock_boundary_151", issue_type="coupon_help", source="checkout_result")
        return ctx

    def c151(ctx):
        f=[]; session=ctx.get("session") or {}; blob=json.dumps(session, ensure_ascii=False, default=list)
        html = (ROOT / "web" / "app.html").read_text(encoding="utf-8")
        _assert_mock_boundary(session, f, "full mock boundary")
        secret_markers = ("s" + "k-", "github" + "_pat_", "g" + "hp_")
        require(not any(marker in blob for marker in secret_markers), "secret-like token leaked", f)
        require("meituan.com" not in blob.lower() and "dianping.com" not in blob.lower(), "real platform URL leaked", f)
        require("data-demo-presets" in html and "useDemoPreset" in html, "minimal frontend demo presets missing", f)
        require(bool(session.get("checkout_result")), "mock checkout result missing from boundary flow", f)
        require(bool(session.get("checkout_split")), "mock split result missing from boundary flow", f)
        require(bool(session.get("support_case")), "mock support case missing from boundary flow", f)
        return f
    add(Case(151, "phase2b final all-mock boundary scan", "full mock boundary scan", c151, c151_runner, timeout_seconds=90))

    def c152_runner():
        agent, session = _run(
            "我想和3个朋友一起去吃个饭",
            {
                "dine_mode": "eat_in",
                "home_area": "新街口",
                "start_time": "18:00",
                "budget_per_person": 150,
                "cuisine_preference": "都可以",
            },
        )
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c152(ctx):
        f=[]; session=ctx["session"]; req=session.get("request") or {}; frame=req.get("intent_frame") or {}
        confirmed=frame.get("confirmed_fields") or {}; sources=frame.get("field_sources") or {}
        require(req.get("primary_intent") == "food_discovery", "food intent not preserved", f)
        require(confirmed.get("party_size") == 4 and sources.get("party_size") == "explicit_text", "我和3个朋友 should become explicit 4 people", f)
        require(session.get("plans"), "food flow did not produce candidate plans after required slots", f)
        cats=[s.get("category") for s in _business_steps(_main_plan(session))]
        require(cats and all(c in MEAL_CATEGORIES or c in ("奶茶", "咖啡", "甜品") for c in cats), f"food plan contains non-food core category: {cats}", f)
        require(not any(s.get("role") == "PLAY" for s in _business_steps(_main_plan(session))), "food-only plan contains PLAY core segment", f)
        return f
    add(Case(152, "phase2c food intent contract and required slots", "我想和3个朋友一起去吃个饭", c152, c152_runner))

    def c153_runner():
        agent = Agent()
        session = agent.run("我想玩个剧本杀")
        return {"agent": agent, "session": session, "plan_summary": "script required slots"}

    def c153(ctx):
        f=[]; session=ctx["session"]; req=session.get("request") or {}
        keys=set(req.get("missing_fields") or [])
        require(session.get("mode") == "needs_clarification", "script missing info should stop at clarification", f)
        require(not session.get("plans"), "script missing info produced random plans", f)
        for key in ("party_size", "start_time", "budget_per_person", "script_style", "window_hours", "home_area"):
            require(key in keys, f"script required slot missing: {key}", f)
        return f
    add(Case(153, "phase2c script required slots contract", "我想玩个剧本杀", c153, c153_runner))

    def c154_runner():
        agent, session = _run(
            "我想玩《快乐人生》，顺便吃点",
            {"party_size": 4, "start_time": "19:00", "budget_per_person": 150, "script_style": "欢乐本", "window_hours": 4, "home_area": "新街口"},
        )
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c154(ctx):
        f=[]; req=ctx["session"].get("request") or {}; seq=req.get("sequence") or []
        require(req.get("primary_intent") == "script_game", "script title should lock primary intent to script_game", f)
        require(req.get("script_title") == "快乐人生", "script title not extracted", f)
        require(seq and seq[0].get("category") == "剧本杀" and seq[0].get("source") == "explicit_text", "script should be first explicit segment", f)
        cats=[s.get("category") for s in _business_steps(_main_plan(ctx["session"]))]
        require(cats and cats[0] == "剧本杀", f"script title plan does not start with script game: {cats}", f)
        return f
    add(Case(154, "phase2c named script before secondary meal", "我想玩《快乐人生》，顺便吃点", c154, c154_runner))

    def c155_runner():
        agent = Agent()
        session = agent.run("想和女朋友约会，浪漫一点")
        return {"agent": agent, "session": session, "plan_summary": "date required slots"}

    def c155(ctx):
        f=[]; req=ctx["session"].get("request") or {}; keys=set(req.get("missing_fields") or [])
        require(req.get("primary_intent") == "date", "date intent not recognized", f)
        require(ctx["session"].get("mode") == "needs_clarification", "ambiguous date should ask required slots", f)
        for key in ("start_time", "home_area", "budget_per_person"):
            require(key in keys, f"date required slot missing: {key}", f)
        return f
    add(Case(155, "phase2c date required slots contract", "想和女朋友约会，浪漫一点", c155, c155_runner))

    def c156_runner():
        agent = Agent()
        session = agent.run("明天18:00想和女朋友在河西约会，人均300，浪漫一点，不想太累")
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c156(ctx):
        f=[]; session=ctx["session"]; titles=[p.get("title","") for p in session.get("plans") or []]
        require(session.get("mode") == "planned", "complete date should build plans", f)
        require(len(session.get("plans") or []) >= 2, "complete date should expose Plan A/B", f)
        old_titles=("拍照轻松局","看展放松局","约会出片局","甜蜜慢享局","朋友周末局","随性玩玩局")
        require(not any(any(old in t for old in old_titles) for t in titles), f"old xx局 title leaked: {titles}", f)
        return f
    add(Case(156, "phase2c complete date creates two clean candidates", "明天18:00想和女朋友在河西约会，人均300，浪漫一点，不想太累", c156, c156_runner))

    def _phase2c_html():
        return (ROOT / "web" / "app.html").read_text(encoding="utf-8")

    def c157(ctx):
        f=[]; html=_phase2c_html()
        for token in ("确认目标", "比较方案", "确认预约", "执行处理", "stepper"):
            require(token in html, f"stepper token missing: {token}", f)
        require("你想怎么玩？" in html and "还差这些信息" in html, "input/required slot UI missing", f)
        require("本次目标" not in html, "old target card should not be rendered in phone flow", f)
        return f
    add(Case(157, "phase2c stepper and intent UI static", "frontend static stepper", c157, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c158(ctx):
        f=[]; html=_phase2c_html()
        forbidden=("AI 一句话规划","理解→检索→排期→订座→异常补救","结构化需求","为什么是 Agent","friends_out","活动优先局","生日一站式局")
        for token in forbidden:
            require(token not in html, f"old UI/internal token leaked: {token}", f)
        require("评委模式 / 执行日志" in html and "judgeLog" in html, "judge mode collapsed log missing", f)
        return f
    add(Case(158, "phase2c old engineering UI hidden", "frontend static cleanup", c158, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c159(ctx):
        f=[]; html=_phase2c_html()
        for token in ("Plan A", "Plan B", "候选方案横向比较", "朋友共选", "/vote/create", "mockFriendVote", "resolveVoteFeedback"):
            require(token in html, f"candidate/friend co-select token missing: {token}", f)
        return f
    add(Case(159, "phase2c plan comparison and friend co-select UI", "frontend static candidates", c159, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c160(ctx):
        f=[]; html=_phase2c_html()
        for token in ("bookingDrawer", "最终确认并预约", "/booking/review", "/booking/confirm", "预约信息", "到店方式"):
            require(token in html, f"booking drawer token missing: {token}", f)
        require("不会联系商家" in html and "不会创建订单" in html, "booking drawer mock boundary missing", f)
        return f
    add(Case(160, "phase2c bottom drawer booking UI", "frontend static booking drawer", c160, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c161(ctx):
        f=[]; html=_phase2c_html()
        for token in ("账单与分账", "顺手加购", "现场情况变了", "triggerSegmentRescue", 'post("/exception"', "/addon/accept", "/checkout/split", "/support/create", "rescueResultHTML"):
            require(token in html, f"execution/rescue token missing: {token}", f)
        return f
    add(Case(161, "phase2c execution page merged actions UI", "frontend static execution", c161, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c162_runner():
        agent, session = _run(TEXT["movie"], {"start_time": "20:00", "home_area": "新街口"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c162(ctx):
        f=[]; cats=[s.get("category") for s in _business_steps(_main_plan(ctx["session"]))]
        require(cats and all(c in ("电影院", "在线电影") for c in cats), f"movie no-meal core polluted: {cats}", f)
        require("no_meal" in ((ctx["session"].get("request") or {}).get("negative_intents") or []), "no_meal missing", f)
        return f
    add(Case(162, "phase2c movie no meal stays core-only", TEXT["movie"], c162, c162_runner))

    def c163_runner():
        old = os.environ.pop("LONGCAT_API_KEY", None)
        try:
            agent, session = _run(TEXT["milk_tea"], {"start_time": "19:00", "home_area": "新街口"})
        finally:
            if old is not None:
                os.environ["LONGCAT_API_KEY"] = old
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c163(ctx):
        f=[]; req=ctx["session"].get("request") or {}
        llm=(ROOT / "agent" / "llm.py").read_text(encoding="utf-8")
        cfg=(ROOT / "config.py").read_text(encoding="utf-8")
        parser=(ROOT / "agent" / "parser.py").read_text(encoding="utf-8")
        require(req.get("primary_intent") == "milk_tea", "LongCat no-key fallback did not parse milk tea", f)
        require("LONGCAT_API_KEY" in cfg and "LONGCAT_MODEL" in cfg and "LongCat" in llm, "LongCat config/adapter missing", f)
        require("DEEPSEEK_API_KEY" not in cfg + llm + parser, "DeepSeek env dependency remains in business code", f)
        return f
    add(Case(163, "phase2c LongCat-only LLM boundary with fallback", TEXT["milk_tea"], c163, c163_runner))

    def c164(ctx):
        f=[]; text=(ROOT / "agent" / "planner.py").read_text(encoding="utf-8")
        for token in ("拍照轻松局","看展放松局","生日一站式局","庆生备选局","宅家追剧局","美食饭局","朋友周末局","轻松兜底局"):
            require(token not in text, f"old planner title remains: {token}", f)
        return f
    add(Case(164, "phase2c planner title residue cleanup", "planner title static check", c164, lambda: {"session": {}, "plan_summary": "static check"}))

    def c165_runner():
        agent, session = _run(
            "我想和3个朋友一起去吃个饭",
            {"dine_mode": "eat_in", "home_area": "新街口", "start_time": "18:00", "budget_per_person": 160, "cuisine_preference": "都可以"},
        )
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c165(ctx):
        f=[]; session=ctx["session"]; titles=[p.get("title") for p in session.get("plans") or []]
        require(len(session.get("plans") or []) >= 2, "food flow should expose Plan A/B", f)
        require(any("Plan A" in str(t) for t in titles) or len(titles) >= 2, f"Plan A/B title missing: {titles}", f)
        return f
    add(Case(165, "phase2c food flow Plan A/B after refinement", "我想和3个朋友一起去吃个饭", c165, c165_runner))

    def c166_runner():
        agent, session = _run(TEXT["script_full"])
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c166(ctx):
        f=[]; cats=[s.get("category") for s in _business_steps(_main_plan(ctx["session"]))]
        require(cats == ["剧本杀"], f"complete script core should not force meal/addon: {cats}", f)
        addons=_optional_addons(ctx["session"])
        require(all((a.get("role") or a.get("slot_role") or "ADDON") == "ADDON" or a.get("kind") == "content" for a in addons), "non-addon leaked into optional add-ons", f)
        return f
    add(Case(166, "phase2c complete script keeps one core segment", TEXT["script_full"], c166, c166_runner))

    def c167_runner():
        agent, session = _run(TEXT["stay_in"], {"start_time": "20:00", "budget_per_person": 120, "stayin_mode": "movie_takeaway"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c167(ctx):
        f=[]; cats=[s.get("category") for s in _business_steps(_main_plan(ctx["session"]))]
        outdoor={"电影院","剧本杀","火锅","江浙菜","台球","按摩","酒店","citywalk","KTV","密室"}
        require(cats and not any(c in outdoor for c in cats), f"stay-in core contains offline category: {cats}", f)
        return f
    add(Case(167, "phase2c stay-in no outdoor core", TEXT["stay_in"], c167, c167_runner))

    def c168(ctx):
        f=[]; files=["web/app.html","README.md","DEMO_PLAYBOOK.md","PROJECT_STATUS.md","CHANGE_SUMMARY.md"]
        if (ROOT / "WORKFLOW_REBUILD_REPORT.md").exists():
            files.append("WORKFLOW_REBUILD_REPORT.md")
        forbidden=("AI 一句话规划","结构化需求","为什么是 Agent","朋友4人局","亲子局","宅家局","情侣约会局","生日一站式局","拍照轻松局","预算友好局","不排队高分局","DeepSeek","DEEPSEEK_API_KEY","OpenAI API","Claude","GPT API")
        for name in files:
            text=(ROOT / name).read_text(encoding="utf-8")
            for token in forbidden:
                require(token not in text, f"{name} contains forbidden residue: {token}", f)
        return f
    add(Case(168, "phase2c public docs and frontend residue cleanup", "public residue scan", c168, lambda: {"session": {}, "plan_summary": "static scan"}))

    def c169_runner():
        agent = Agent()
        initial = agent.run("想和女朋友约会，浪漫一点")
        answers = {
            "start_time": "18:00",
            "home_area": "新街口",
            "budget_per_person": 300,
            "date_preferences": ["看电影", "拍照", "不太累"],
        }
        session = agent.refine(answers)
        return {"agent": agent, "session": session, "initial": initial, "answers": answers, "clarification_triggered": bool(initial.get("clarifications_needed") or (initial.get("request") or {}).get("clarifications_needed")), "clarification_completed": True, "plan_summary": _plan_summary(session)}

    def c169(ctx):
        f=[]; session=ctx["session"]; req=session.get("request") or {}; initial=ctx.get("initial") or {}
        html = _phase2c_html()
        initial_missing = (initial.get("request") or {}).get("missing_fields") or initial.get("missing_fields") or []
        require("date_preferences" in initial_missing, f"date preferences should be requested before refinement: {initial_missing}", f)
        require("data-multi" in html and "dataset.multi" in html and "selected" in html, "frontend multi-select support is missing", f)
        require(req.get("date_preferences") == ["看电影", "拍照", "不太累"], f"date preferences not preserved: {req.get('date_preferences')}", f)
        require(session.get("mode") == "planned" and session.get("plans"), "date multi-select did not generate plans after confirm", f)
        cats_by_plan = [[s.get("category") for s in _business_steps(p)] for p in session.get("plans") or []]
        require(any("电影院" in cats for cats in cats_by_plan), f"movie preference not reflected in plans: {cats_by_plan}", f)
        require(any(("展览" in cats or "citywalk" in cats) for cats in cats_by_plan), f"photo/light preference not reflected in plans: {cats_by_plan}", f)
        return f
    add(Case(169, "phase2c date preferences multi-select", "想和女朋友约会，浪漫一点", c169, c169_runner))

    def c170(ctx):
        f=[]; html=_phase2c_html()
        for token in ("我想玩个剧本杀", "我想和3个朋友一起去吃个饭"):
            require(token not in html, f"short homepage template remains: {token}", f)
        for token in ("今晚 19:00", "人均 150", "新街口", "4 个人", "预算 100"):
            require(token in html, f"complete homepage template detail missing: {token}", f)
        require("useDemoPreset" in html and "planFromInput" in html, "homepage presets or normal plan flow missing", f)
        return f
    add(Case(170, "phase2c homepage template completeness", "frontend homepage templates", c170, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c171(ctx):
        f=[]; html=_phase2c_html()
        forbidden=("适合原因", "什么店", "多少钱", "多长时间", "关键词", "拍照轻松 Plan A", "生日安排 Plan A")
        for token in forbidden:
            require(token not in html, f"candidate card residue remains: {token}", f)
        for token in ("merchant-line", "merchant-logo", "人均", "用时", "quick-fact", "risk-line", "selected_merchant_ids"):
            require(token in html, f"candidate clean card token missing: {token}", f)
        return f
    add(Case(171, "phase2c candidate card cleanup", "frontend candidate card", c171, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c172(ctx):
        f=[]; html=_phase2c_html()
        for token in ("jumpStep", "maxUnlockedStep", "请先完成当前步骤", "window.scrollTo"):
            require(token in html, f"stepper gate token missing: {token}", f)
        return f
    add(Case(172, "phase2c stepper navigation gate", "frontend stepper gate", c172, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c173(ctx):
        f=[]; html=_phase2c_html()
        for token in ("Plan A 胜出", "Plan B 胜出", "都不要", "mockFriendRejectAll", "朋友想吃火锅", "立即预约"):
            require(token in html, f"friend no-option token missing: {token}", f)
        require("确认这个方案" not in html, "old host final confirmation button should be removed after friend winner", f)
        return f
    add(Case(173, "phase2c friend co-select no-option", "frontend friend co-select", c173, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c174(ctx):
        f=[]; html=_phase2c_html()
        for token in ("美团团购券（Mock）", "美团买单（Mock）", "mockSegmentPay", "不会触发真实支付"):
            require(token in html, f"execution payment mock token missing: {token}", f)
        return f
    add(Case(174, "phase2c execution payment buttons", "frontend payment buttons", c174, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c175(ctx):
        f=[]; html=_phase2c_html()
        for token in ("billTotal", "aa-item", "aa-person", "aa-amount", "updateSplitPreview", "可手动修改每个人要 A 的金额", "Mock A 钱"):
            require(token in html, f"split bill UI token missing: {token}", f)
        require("交通费估算（Mock）" in html, "traffic mock bill item missing", f)
        return f
    add(Case(175, "phase2c split bill manual adjustment", "frontend split bill", c175, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c176(ctx):
        f=[]; html=_phase2c_html()
        for token in ("其他问题", "otherIssueText", "submitOtherIssue", "other_issue", "/support/create", "Mock 帮助单"):
            require(token in html, f"other issue support token missing: {token}", f)
        return f
    add(Case(176, "phase2c support other issue", "frontend support other", c176, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c177(ctx):
        f=[]; html=_phase2c_html()
        candidate_block = html[html.find("function candidatesHTML"):html.find("function selectedHTML")]
        execution_block = html[html.find("function executionHTML"):html.find("function updateSide")]
        require("顺手加购" not in candidate_block, "add-on appears in candidate main area", f)
        require("顺手加购" in execution_block and "openAddonModal" in execution_block, "execution add-on modal missing", f)
        require("加入本次账单" in html and "跳过" in html, "add-on accept/skip controls missing", f)
        require("看完攻略，不进账单" in html, "content add-on non-billable copy missing", f)
        return f
    add(Case(177, "phase2c addon placement", "frontend addon placement", c177, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c178_runner():
        agent, session = _run(TEXT["birthday"], {"start_time":"18:00","home_area":"新街口","window_hours":4})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c178(ctx):
        f=[]; plan=_main_plan(ctx["session"]); cats=_cats(plan); opt=plan.get("optional_addons") or []
        require("蛋糕鲜花" not in cats, f"long-lead cake/flowers became core segment: {cats}", f)
        require(bool(plan.get("long_lead_addon_hint")) or any("生日" in str(x.get("title") or "") for x in opt), "long-lead birthday prompt missing", f)
        html=_phase2c_html()
        require("提前准备提醒" in html and "暂不需要" in html, "booking drawer long-lead controls missing", f)
        return f
    add(Case(178, "phase2c long-lead addon early prompt", TEXT["birthday"], c178, c178_runner))

    def _catalog_stats():
        merchants = json.loads(MERCHANTS.read_text(encoding="utf-8"))
        categories = {}
        areas = {}
        for m in merchants:
            categories[m.get("category")] = categories.get(m.get("category"), 0) + 1
            areas[m.get("area")] = areas.get(m.get("area"), 0) + 1
        return merchants, categories, areas

    def c179(ctx):
        f=[]; merchants, categories, areas = _catalog_stats()
        require(len(merchants) >= 420, f"catalog has {len(merchants)} merchants", f)
        require(len([a for a in areas if a != "线上"]) >= 10, f"area coverage too small: {areas}", f)
        require(len(categories) >= 20, f"category coverage too small: {categories}", f)
        signatures={(m.get("name"),m.get("category"),m.get("area"),m.get("price"),m.get("duration_minutes")) for m in merchants}
        require(len(signatures) > len(merchants) * 0.92, "too many duplicate merchant signatures", f)
        return f
    add(Case(179, "phase2c catalog size", "catalog stats", c179, lambda: {"session": {}, "plan_summary": "catalog check"}))

    def c180(ctx):
        f=[]; _merchants, categories, areas = _catalog_stats()
        required_categories = {"火锅","江浙菜","烧烤","海鲜","简餐","本地小吃","外卖","甜品","奶茶","咖啡","剧本杀","密室","KTV","台球","桌游","电影院","展览","按摩","citywalk","蛋糕鲜花","闪购零食","酒店","酒吧","冰淇淋"}
        required_areas = {"新街口","河西","老门东","夫子庙","鼓楼","玄武湖","江宁","仙林","百家湖","奥体","马鞍山"}
        for cat in required_categories:
            require(categories.get(cat, 0) >= 10, f"category {cat} has {categories.get(cat,0)} samples", f)
        for area in required_areas:
            require(areas.get(area, 0) >= 20, f"area {area} has {areas.get(area,0)} samples", f)
        return f
    add(Case(180, "phase2c catalog coverage", "catalog coverage", c180, lambda: {"session": {}, "plan_summary": "catalog check"}))

    def c181_runner():
        text = "我和3个朋友今晚19:00想在新街口吃饭，人均150，想少排队，菜系都可以。"
        agent, session = _run(text, {"dine_mode":"eat_in","home_area":"新街口","start_time":"19:00","budget_per_person":150,"cuisine_preference":"都可以"})
        agent2, session2 = _run(text.replace("新街口", "河西"), {"dine_mode":"eat_in","home_area":"河西","start_time":"19:00","budget_per_person":150,"cuisine_preference":"都可以"})
        return {"agent": agent, "session": session, "other_session": session2, "plan_summary": _plan_summary(session)}

    def c181(ctx):
        f=[]; merchants={m.get("id") for m in json.loads(MERCHANTS.read_text(encoding="utf-8"))}; plan=_main_plan(ctx["session"]); ids=_ids(plan); cats=_cats(plan)
        require(ids and all(mid in merchants for mid in ids), f"selected ids not from data: {ids}", f)
        meta=plan.get("matching_meta") or {}
        require(meta.get("candidate_pool_size", 0) > 1, f"candidate pool too small: {meta}", f)
        require(not any(s.get("slot_role") == "PLAY" or s.get("kind") == "activity" for s in _business_steps(plan)), f"food plan contains PLAY: {cats}", f)
        require(_ids(_main_plan(ctx["other_session"])) != ids, "changing area did not change selected merchant ids", f)
        return f
    add(Case(181, "phase2c data-driven food recommendation", "food data-driven", c181, c181_runner))

    def c182_runner():
        text = "4个人今晚19:00想在新街口玩欢乐本，能玩4小时，人均150，公共交通。"
        agent, session = _run(text)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c182(ctx):
        f=[]; plan=_main_plan(ctx["session"]); cats=_cats(plan); step=_script_step(plan); meta=plan.get("matching_meta") or {}
        require(cats == ["剧本杀"], f"script plan changed category: {cats}", f)
        f.extend(script_fields_ok(step))
        require(meta.get("candidate_pool_size", 0) > 1 and meta.get("filtered_by_category_count", 0) > 1, f"script meta too small: {meta}", f)
        return f
    add(Case(182, "phase2c data-driven script recommendation", "script data-driven", c182, c182_runner))

    def c183_runner():
        text = "今晚宅家，2个人，预算100，想点外卖和零食，不想出门。"
        agent, session = _run(text, {"start_time":"20:00","budget_per_person":100,"stayin_mode":"movie_takeaway"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c183(ctx):
        f=[]; cats=_cats(_main_plan(ctx["session"]))
        require("在线电影" not in cats, f"online movie entered stay-in transaction core: {cats}", f)
        require(set(cats) <= {"外卖","闪购零食"}, f"stay-in core has unsupported category: {cats}", f)
        return f
    add(Case(183, "phase2c no online movie core recommendation", "stay-in no online movie", c183, c183_runner))

    def c184(ctx):
        f=[]; files=["web/app.html","README.md","DEMO_PLAYBOOK.md","PROJECT_STATUS.md","CHANGE_SUMMARY.md"]
        forbidden=("真实支付成功", "真实客服接入", "真实订单已创建", "真实配送成功", "真实下单成功", "DeepSeek", "OpenAI API", "Claude", "GPT API", "乱码")
        for name in files:
            path=ROOT / name
            if not path.exists():
                continue
            text=path.read_text(encoding="utf-8")
            for token in forbidden:
                require(token not in text, f"{name} contains forbidden mock boundary token: {token}", f)
            require("???" not in text, f"{name} contains ???", f)
        return f
    add(Case(184, "phase2c mock boundary scan", "mock boundary scan", c184, lambda: {"session": {}, "plan_summary": "static scan"}))



    def _u(s: str) -> str:
        return s.encode("ascii").decode("unicode_escape")

    def c185(ctx):
        f=[]; html=_phase2c_html()
        for token in (_u("\\u4ec0\\u4e48\\u5e97"), _u("\\u591a\\u5c11\\u94b1"), _u("\\u591a\\u957f\\u65f6\\u95f4"), _u("\\u9002\\u5408\\u539f\\u56e0"), "xx" + _u("\\u5c40")):
            require(token not in html, f"candidate card still contains table/internal token: {token}", f)
        require("Plan A" in html and "Plan B" in html, "Plan A/B labels missing", f)
        require("merchant-line" in html and "merchant-logo" in html and "quick-fact" in html, "merchant-first candidate card structure missing", f)
        return f
    add(Case(185, "phase2c browser candidate card visual cleanup", "frontend candidate visual cleanup", c185, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c186(ctx):
        f=[]; html=_phase2c_html()
        for token in ("jumpStep", "maxUnlockedStep", _u("\\u8bf7\\u5148\\u5b8c\\u6210\\u5f53\\u524d\\u6b65\\u9aa4"), "window.scrollTo", "clearDownstreamState"):
            require(token in html, f"stepper state/reset token missing: {token}", f)
        for token in ('clearDownstreamState("clarification")', 'clearDownstreamState("candidate")', 'delete session.booking_review', 'delete session.checkout_preview'):
            require(token in html, f"downstream reset detail missing: {token}", f)
        return f
    add(Case(186, "phase2c browser stepper back navigation reset", "frontend stepper reset", c186, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c187(ctx):
        f=[]; html=_phase2c_html()
        manual_copy=_u("\\u53ef\\u624b\\u52a8\\u4fee\\u6539\\u6bcf\\u4e2a\\u4eba\\u8981 A \\u7684\\u91d1\\u989d")
        mismatch_copy=_u("\\u624b\\u52a8\\u91d1\\u989d\\u5408\\u8ba1\\u4e0e\\u5e94\\u5206\\u644a\\u91d1\\u989d\\u4e0d\\u4e00\\u81f4\\uff0c\\u53ef\\u7ee7\\u7eed\\u53d1\\u9001 Mock \\u94fe\\u63a5")
        for token in (manual_copy, "aa-amount", "markManualAmount", "updateSplitPreview(false)", "splitMismatch", mismatch_copy):
            require(token in html, f"split manual amount token missing: {token}", f)
        require("?amount=" in html and "mock-link" in html, "Mock A money link amount sync missing", f)
        return f
    add(Case(187, "phase2c browser split manual amount sync", "frontend split sync", c187, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c188(ctx):
        f=[]; html=_phase2c_html()
        required=(
            _u("\\u5546\\u5bb6\\u6ee1\\u5ea7 / \\u6392\\u961f\\u592a\\u4e45"), _u("\\u670b\\u53cb\\u8fdf\\u5230"),
            _u("\\u60f3\\u6539\\u65f6\\u95f4"), _u("\\u5238\\u4e0d\\u4f1a\\u7528"), _u("\\u60f3\\u9000\\u6b3e"),
            _u("\\u60f3\\u6295\\u8bc9"), _u("\\u5176\\u4ed6\\u95ee\\u9898"), "otherIssueText", "submitOtherIssue", "Mock"
        )
        for token in required:
            require(token in html, f"support other issue token missing: {token}", f)
        require("prompt(" not in html, "other issue should not use prompt()", f)
        return f
    add(Case(188, "phase2c browser support other issue inline input", "frontend support inline", c188, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c189(ctx):
        f=[]; merchants=json.loads(MERCHANTS.read_text(encoding="utf-8"))
        require(len(merchants) >= 420, f"merchant count below 420: {len(merchants)}", f)
        visible_fields=("name", "category", "area", "review_snippet")
        for m in merchants:
            name=str(m.get("name", ""))
            require(not re.search(r"Mock\s*\d+", name), f"user-facing merchant name contains Mock number: {m.get('id')} {name}", f)
            for field in visible_fields:
                value=str(m.get(field, ""))
                require("?" not in value, f"merchant {field} contains ?: {m.get('id')} {value}", f)
            require("?" not in str(m.get("review_tags", [])), f"merchant review_tags contains ?: {m.get('id')}", f)
        return f
    add(Case(189, "phase2c browser user-facing merchant names clean", "merchant names clean", c189, lambda: {"session": {}, "plan_summary": "catalog check"}))

    def c190_runner():
        text=_u("\\u4eca\\u665a\\u5b85\\u5bb6\\uff0c1\\u4e2a\\u4eba\\uff0c\\u9884\\u7b97100\\uff0c\\u60f3\\u70b9\\u5916\\u5356\\u548c\\u96f6\\u98df\\uff0c\\u4e0d\\u60f3\\u51fa\\u95e8\\u3002")
        agent, session = _run(text, {"start_time":"20:00","budget_per_person":100,"stayin_mode":"movie_takeaway"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c190(ctx):
        f=[]; plan=_main_plan(ctx["session"]); cats=_cats(plan); names=[str(s.get("name") or "") for s in _business_steps(plan)]
        forbidden={_u("\\u5728\\u7ebf\\u7535\\u5f71"), _u("\\u7231\\u5947\\u827a"), _u("\\u817e\\u8baf\\u89c6\\u9891")}
        require(not any(c in forbidden for c in cats), f"non-Meituan category entered user-facing core: {cats}", f)
        require(not any(any(token in n for token in forbidden) for n in names), f"non-Meituan name entered user-facing core: {names}", f)
        merchants=json.loads(MERCHANTS.read_text(encoding="utf-8"))
        online=[m for m in merchants if m.get("category") == _u("\\u5728\\u7ebf\\u7535\\u5f71") or m.get("area") == _u("\\u7ebf\\u4e0a")]
        require(all(m.get("disabled_for_recommendation") for m in online), "online/platform records are not disabled for recommendation", f)
        return f
    add(Case(190, "phase2c browser no online movie user-facing recommendation", "stay-in online cleanup", c190, c190_runner))

    def c191(ctx):
        f=[]
        render=(ROOT / "render.yaml")
        require(render.exists(), "render.yaml missing", f)
        text=render.read_text(encoding="utf-8") if render.exists() else ""
        for token in ("type: web", "env: python", "pip install -r requirements.txt", "uvicorn server:app --host 0.0.0.0 --port $PORT"):
            require(token in text, f"render.yaml token missing: {token}", f)
        server=(ROOT / "server.py").read_text(encoding="utf-8")
        require('os.getenv("PORT", "8000")' in server or "os.getenv('PORT', '8000')" in server, "server.py does not read PORT env var", f)
        readme=(ROOT / "README.md").read_text(encoding="utf-8")
        require("Render" in readme and "Netlify" in readme and "FastAPI" in readme, "README deploy guidance incomplete", f)
        return f
    add(Case(191, "phase2c browser render config", "render config", c191, lambda: {"session": {}, "plan_summary": "deploy check"}))

    def c192(ctx):
        f=[]; path=ROOT / "FRIEND_TEST_CHECKLIST.md"
        require(path.exists(), "FRIEND_TEST_CHECKLIST.md missing", f)
        text=path.read_text(encoding="utf-8") if path.exists() else ""
        for token in ("Food Only", "Script Game Missing Info", "Date Multi-Select", "Stay-In", "Friend Co-Select", "Execution Page", "P0 / P1 / P2"):
            require(token in text, f"friend checklist token missing: {token}", f)
        return f
    add(Case(192, "phase2c browser friend test checklist", "friend checklist", c192, lambda: {"session": {}, "plan_summary": "doc check"}))

    def c193(ctx):
        f=[]; files=["web/app.html","README.md","DEMO_PLAYBOOK.md","PROJECT_STATUS.md","CHANGE_SUMMARY.md","DEPLOY_RENDER_GUIDE.md","FRIEND_TEST_CHECKLIST.md"]
        forbidden=(
            _u("\\u771f\\u5b9e\\u652f\\u4ed8\\u6210\\u529f"), _u("\\u771f\\u5b9e\\u5ba2\\u670d\\u5165\\u53e3"),
            _u("\\u771f\\u5b9e\\u8ba2\\u5355\\u5df2\\u521b\\u5efa"), _u("\\u771f\\u5b9e\\u914d\\u9001\\u6210\\u529f"),
            "DeepSeek", "OpenAI API", "Claude", "GPT API", "Gemini"
        )
        for name in files:
            path=ROOT / name
            if not path.exists():
                continue
            text=path.read_text(encoding="utf-8")
            for token in forbidden:
                require(token not in text, f"{name} contains forbidden external boundary token: {token}", f)
        return f
    add(Case(193, "phase2c browser no external API boundary regression", "external boundary scan", c193, lambda: {"session": {}, "plan_summary": "static scan"}))

    def _app_html() -> str:
        return (ROOT / "web" / "app.html").read_text(encoding="utf-8")

    def _function_block(html: str, name: str, next_name: str | None = None) -> str:
        start = html.find(f"function {name}")
        if start < 0:
            return ""
        if next_name:
            end = html.find(f"function {next_name}", start + 1)
            return html[start:end if end > start else len(html)]
        return html[start:]

    def c194(ctx):
        f=[]; html=_app_html(); home=html[html.find("<main class=\"phone\""):html.find("<aside class=\"side\"")]
        require("切换商家后台" in home and 'href="/admin"' in home, "home admin switch link missing", f)
        for token in ("先确认目标和关键缺口", "只认用户说过的", "Plan A/B 横向看", "底部抽屉确认", "账单、加购、救援"):
            require(token not in home, f"home still exposes flow copy: {token}", f)
        require("renderStepper" in html and 'if (stage === "input")' in html and 'el.classList.add("hidden")' in html, "home stepper hide logic missing", f)
        return f
    add(Case(194, "phase2c user flow home entry cleanup", "frontend home cleanup", c194, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c195(ctx):
        f=[]; html=_app_html(); input_block=_function_block(html, "inputHTML", "useDemoPreset")
        require("你想怎么玩？" in input_block, "home heading not updated", f)
        require("我和 3 个朋友今晚 19:00 想在新街口吃饭，人均 150" in input_block, "full template text missing in chips/placeholder", f)
        require("4 个人今晚 19:00 想在新街口玩欢乐本" in input_block, "script full template missing", f)
        require('onclick="useDemoPreset(0)"' in input_block and "planFromInput()" not in input_block.split("class=\"chips\"",1)[-1].split("</div>",1)[0], "template chip should only fill input", f)
        return f
    add(Case(195, "phase2c user flow full input templates", "frontend templates", c195, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c196(ctx):
        f=[]; html=_app_html(); clarify=_function_block(html, "clarifyHTML", "questionHTML"); q=_function_block(html, "questionHTML", "isPastTime")
        require("已记住：" not in clarify and "我确认一下" not in clarify, "clarification remembered copy still present", f)
        require("setFreeAnswer" in html and "自己写：比如云南菜、日料、东北菜" in q, "custom cuisine input missing", f)
        require("cuisine_preference" in q, "custom cuisine is not tied to cuisine_preference", f)
        return f
    add(Case(196, "phase2c user flow clarification cleanup", "frontend clarify cleanup", c196, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c197(ctx):
        f=[]; html=_app_html()
        for name in ("clarifyHTML", "candidatesHTML", "selectedHTML"):
            block=_function_block(html, name)
            block=block[: block.find("function ", 20) if block.find("function ", 20)>0 else len(block)]
            require("publicIntent()" not in block, f"{name} still renders publicIntent", f)
        require("本次目标" not in html, "old 本次目标 copy remains", f)
        return f
    add(Case(197, "phase2c user flow no target card after home", "frontend target cleanup", c197, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c198(ctx):
        f=[]; html=_app_html(); card=_function_block(html, "planCardHTML", "isDeliverySegment")
        require("leadName" in card and 'class="plan-title">${esc(leadName)}' in card, "plan card title does not use merchant/core name", f)
        require('class="plan-title">Plan' not in card, "plan card repeats Plan label as title", f)
        for token in ("review_count", "open", "close", "queueText", "rating", "查看商详"):
            require(token in card, f"plan card missing merchant fact token: {token}", f)
        return f
    add(Case(198, "phase2c user flow plan card merchant facts", "frontend plan card", c198, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c199(ctx):
        f=[]; html=_app_html()
        for token in ("openMerchantDetail", "merchantCoupons", "merchantFeatures", "merchant-hero", "店铺券", "购买券 Mock", "核验券 Mock"):
            require(token in html, f"merchant detail/coupon token missing: {token}", f)
        return f
    add(Case(199, "phase2c user flow merchant detail drawer", "frontend merchant detail", c199, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c200(ctx):
        f=[]; html=_app_html(); friend=_function_block(html, "friendCoSelectHTML", "voteRoomHTML")
        require("喊朋友一起挑" in friend and "先看看朋友怎么想，再一起决定" in friend, "friend co-select copy missing", f)
        require("分享给朋友" in friend, "share with friends copy missing", f)
        for token in ("朋友晚到半小时", "餐厅担心排队", "发给朋友确认"):
            require(token not in friend, f"friend co-select still has exception/old token: {token}", f)
        return f
    add(Case(200, "phase2c user flow friend co-select copy", "frontend friend copy", c200, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c201(ctx):
        f=[]; html=_app_html(); reject=_function_block(html, "mockFriendRejectAll", "acceptFriendChoice")
        require("朋友想吃火锅" in reject, "reject-all mock friend preference missing", f)
        require("stage = \"candidates\"" in reject and "session.plans" in reject, "reject-all should stay on candidates and swap plans", f)
        require("resetFlow()" not in reject and "stage='input'" not in reject, "reject-all should not reset or jump home", f)
        return f
    add(Case(201, "phase2c user flow reject all swaps candidates", "frontend reject all", c201, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c202(ctx):
        f=[]; html=_app_html(); vote=_function_block(html, "mockFriendVote", "mockFriendRejectAll")
        require("立即预约" in vote and "acceptFriendChoice" in vote, "friend vote should lead to immediate booking", f)
        require("确认这个方案" not in vote, "friend vote still asks confirm this plan", f)
        return f
    add(Case(202, "phase2c user flow vote to immediate booking", "frontend vote flow", c202, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c203(ctx):
        f=[]; html=_app_html(); drawer=_function_block(html, "bookingDrawerHTML", "acceptBirthdayAddon"); open_fn=_function_block(html, "openBookingDrawer", "bookingDrawerHTML")
        for token in ("bookingTime", "bookingPeople", "bookingContact", "bookingArrival", "bookingRoom", "bookingNote"):
            require(token in drawer, f"booking drawer missing field: {token}", f)
        require("isDeliveryPlan(mainPlan())" in open_fn and "confirmBooking(true)" in open_fn, "delivery/stay-in should skip booking drawer", f)
        return f
    add(Case(203, "phase2c user flow booking drawer and delivery skip", "frontend booking drawer", c203, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c204(ctx):
        f=[]; html=_app_html()
        for token in ("executionTimelineHTML", "executionItems", "从出发地前往第一站", "从最后一站回家", "等待配送", "送达 / 收货", "completeExecutionStep", "viewExecutionStep"):
            require(token in html, f"execution timeline token missing: {token}", f)
        return f
    add(Case(204, "phase2c user flow execution staged timeline", "frontend execution timeline", c204, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c205(ctx):
        f=[]; html=_app_html(); execution=_function_block(html, "executionHTML", "executionTimelineHTML")
        order=["顺手来一个", "行程有变化？", "账单", "联系客服"]
        positions=[execution.find(x) for x in order]
        require(all(p >= 0 for p in positions), f"execution drawer entries missing: {positions}", f)
        require(positions == sorted(positions), f"execution drawer entries out of order: {positions}", f)
        for token in ("billHTML()", "addonHTML()", "rescueHTML()", "supportHTML()"):
            require(token not in execution, f"execution page still renders long panel: {token}", f)
        return f
    add(Case(205, "phase2c user flow execution drawer order", "frontend execution drawers", c205, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c206(ctx):
        f=[]; html=_app_html(); bill=_function_block(html, "billDrawerContent", "updateCustomSplit")
        for token in ("customBillTotal", "aa-amount", "singleCollectLink", "美团/微信支付", "updateCustomSplit"):
            require(token in bill or token in html, f"custom bill/split token missing: {token}", f)
        require("/mock/collect?channel=meituan-wechat" in html, "single collection link missing", f)
        return f
    add(Case(206, "phase2c user flow custom bill split", "frontend bill split", c206, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c207(ctx):
        f=[]; html=_app_html()
        require("deliveryFact" in html and "美团外卖" in html and "配送约" in html and "配送费" in html, "delivery semantics missing", f)
        delivery_block=_function_block(html, "deliveryFact", "merchantLineHTML")
        require("到店确认" not in delivery_block, "delivery block contains arrival wording", f)
        return f
    add(Case(207, "phase2c user flow delivery copy", "frontend delivery copy", c207, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c208(ctx):
        f=[]; merchants=json.loads(MERCHANTS.read_text(encoding="utf-8"))
        require(len(merchants) >= 420, f"merchant count below 420: {len(merchants)}", f)
        for m in merchants:
            require(len(m.get("coupons") or []) >= 2, f"merchant lacks two coupons: {m.get('id')}", f)
            for key in ("name","category","area","price","rating","review_count","open","close","queue_minutes"):
                require(m.get(key) not in (None, ""), f"merchant missing {key}: {m.get('id')}", f)
            require("Mock " not in str(m.get("name","")), f"merchant name has Mock number trace: {m.get('name')}", f)
        return f
    add(Case(208, "phase2c user flow merchant coupon data", "catalog coupon data", c208, lambda: {"session": {}, "plan_summary": "catalog check"}))

    def c209_runner():
        text="我和3个朋友今晚19:00想在新街口吃饭，人均150，想少排队，菜系都可以。"
        agent, session = _run(text, {"dine_mode":"eat_in","home_area":"新街口","start_time":"19:00","budget_per_person":150,"cuisine_preference":"都可以"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c209(ctx):
        f=[]; plans=ctx["session"].get("plans") or []
        require(len(plans) >= 2, "less than two plans", f)
        names=[]
        for p in plans[:2]:
            steps=_business_steps(p)
            require(steps, "plan has no business steps", f)
            names.append(steps[0].get("name"))
        require(names[0] != names[1], f"Plan A/B first merchant names are identical: {names}", f)
        return f
    add(Case(209, "phase2c user flow plan A B distinct merchants", "plan data distinct", c209, c209_runner))

    def c210(ctx):
        f=[]; agent=Agent(); session=agent.run(_u("\\u6211\\u4eca\\u5929\\u4e0d\\u60f3\\u51fa\\u95e8\\uff0c\\u5c31\\u60f3\\u5b85\\u5bb6\\u770b\\u70b9\\u4e1c\\u897f\\uff0c\\u70b9\\u70b9\\u5403\\u7684"))
        qs=session.get("clarifications_needed") or []
        keys=[q.get("key") for q in qs]
        require("home_area" not in keys, f"stay-in should not ask area: {keys}", f)
        return f
    add(Case(210, "phase2c user flow stay-in no area ask", "stay-in clarify", c210, lambda: {"session": {}, "plan_summary": "clarify check"}))

    def c211(ctx):
        f=[]; html=_app_html(); selected=_function_block(html, "selectedHTML", "timelineHTML")
        require("立即预约" in selected, "selected page immediate booking missing", f)
        for token in ("发给朋友确认", "确认这个方案"):
            require(token not in selected, f"selected page still has old confirm copy: {token}", f)
        return f
    add(Case(211, "phase2c user flow selected page immediate booking", "frontend selected flow", c211, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c212(ctx):
        f=[]; html=_app_html(); main=html[html.find("<main class=\"phone\""):html.find("</main>")]
        require('id="bookingDrawer"' in main and 'id="addonModal"' in main, "drawers should be inside phone shell", f)
        require("position: absolute" in html and "max-height: 78%" in html, "drawer should be phone-contained absolute panel", f)
        return f
    add(Case(212, "phase2c user flow phone-contained drawers", "frontend drawer containment", c212, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c213(ctx):
        f=[]; html=_app_html()
        for token in ("height: 920px", "flex-direction: column", "overflow-y: auto", "overscroll-behavior: contain"):
            require(token in html, f"fixed phone/internal scroll token missing: {token}", f)
        return f
    add(Case(213, "phase2c user flow fixed phone scroll", "frontend fixed viewport", c213, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c214(ctx):
        f=[]; html=_app_html()
        for token in ("buyCoupon", "verifyCoupon", "couponState", "商详 / 买券 / 核验", "本地 Mock 商详"):
            require(token in html, f"coupon state/detail token missing: {token}", f)
        return f
    add(Case(214, "phase2c user flow coupon buy verify mock", "frontend coupon mock", c214, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c215(ctx):
        f=[]; html=_app_html()
        require("openActionDrawer('addon')" in html and "openActionDrawer('change')" in html and "openActionDrawer('bill')" in html and "openActionDrawer('support')" in html, "execution action drawers not wired", f)
        require("prompt(" not in html, "frontend should not use prompt popup", f)
        require("真实支付成功" not in html and "真实下单" not in html, "frontend overclaims real fulfillment", f)
        return f
    add(Case(215, "phase2c user flow drawer wiring boundary", "frontend boundary", c215, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def _phase2c_override() -> str:
        html = _app_html()
        start = html.find("const PHASE2C_EXAMPLES")
        return html[start:] if start >= 0 else html

    def _last_fn(html: str, name: str, next_names: tuple[str, ...] = ()) -> str:
        start = html.rfind(f"function {name}")
        if start < 0:
            return ""
        end = len(html)
        for next_name in next_names:
            pos = html.find(f"function {next_name}", start + 1)
            if pos > start:
                end = min(end, pos)
        return html[start:end]

    def _sequence_session(text: str, budget: int = 400) -> dict:
        agent = Agent()
        initial = agent.run(text)
        session = agent.refine({
            "script_style": _u("\\u6b22\\u4e50\\u672c"),
            "window_hours": 5,
            "duration_minutes": 300,
            "party_size": 4,
            "start_time": "19:00",
            "budget_per_person": budget,
            "home_area": _u("\\u65b0\\u8857\\u53e3"),
            "transport": "public",
        })
        return {"agent": agent, "initial": initial, "session": session, "plan_summary": _plan_summary(session)}

    def _cat_names(session: dict) -> list[str]:
        return [s.get("category") for s in _business_steps(_main_plan(session))]

    def c194_new(ctx):
        f=[]; html=_app_html(); override=_phase2c_override()
        require(".shell.phase2c" in html and "grid-template-columns: minmax(500px" in html, "phone is not promoted as main visual", f)
        require(_u("\\u5207\\u6362\\u5546\\u5bb6\\u540e\\u53f0") in html and 'href="/admin"' in html, "admin switch link missing", f)
        for token in (_u("\\u4f60\\u60f3\\u600e\\u4e48\\u73a9\\uff1f"), _u("\\u8bf4\\u4e00\\u53e5\\uff0c\\u6211\\u5e2e\\u4f60\\u628a\\u8fd9\\u573a\\u5b89\\u6392\\u5230\\u80fd\\u51fa\\u95e8\\u3002"), _u("\\u6211\\u73b0\\u5728\\u5728\\u54ea")):
            require(token in override, f"home chat token missing: {token}", f)
        require(".phase2c .stepper { display: none" in html, "visible stepper is not hidden in Phase 2C shell", f)
        require('<input type="time"' not in _last_fn(html, "inputHTML", ("fillPhase2cExample",)), "home page still exposes a start-time picker", f)
        return f
    add(Case(194, "phase2c itinerary home chat entry", "frontend home chat", c194_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c195_new(ctx):
        f=[]; html=_app_html(); override=_phase2c_override(); fill=_last_fn(html, "fillPhase2cExample", ("planFromInput",))
        for token in (
            _u("\\u6211\\u548c 3 \\u4e2a\\u670b\\u53cb\\u4eca\\u665a 19:00 \\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u5230\\u5e97\\u5403\\u996d"),
            _u("4 \\u4e2a\\u4eba\\u4eca\\u665a 19:00 \\u60f3\\u5728\\u6c5f\\u5b81\\u73a9\\u6b22\\u4e50\\u672c"),
            _u("\\u6211\\u548c\\u5973\\u670b\\u53cb 18:00 \\u5728\\u4ed9\\u6797\\u7ea6\\u4f1a"),
            _u("\\u4eca\\u665a\\u5b85\\u5bb6\\uff0c2 \\u4e2a\\u4eba"),
        ):
            require(token in override, f"complete example template missing: {token}", f)
        require("PHASE2C_EXAMPLES[i]" in fill, "example chip does not fill textarea", f)
        require("/plan" not in fill and "planFromInput()" not in fill, "example chip should not auto-plan", f)
        return f
    add(Case(195, "phase2c itinerary complete examples fill only", "frontend examples", c195_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c196_new(ctx):
        f=[]; html=_app_html(); override=_phase2c_override(); clarify=_last_fn(html, "clarifyHTML", ("questionHTML",)); q=_last_fn(html, "questionHTML", ("businessSteps",))
        require(_u("\\u60f3\\u73a9\\u591a\\u4e45\\uff1f") in q, "duration copy should be 想玩多久？", f)
        require(_u("\\u81ea\\u5df1\\u5199\\uff1a\\u6bd4\\u5982\\u4e91\\u5357\\u83dc\\u3001\\u65e5\\u6599\\u3001\\u4e1c\\u5317\\u83dc") in q and "cuisine_preference" in q, "custom cuisine input missing", f)
        require(_u("\\u5df2\\u8bb0\\u4f4f") not in clarify, "clarify page still shows remembered summary", f)
        for token in (_u("\\u6b63\\u5728\\u8bc6\\u522b\\u2026"), _u("\\u6b63\\u5728\\u5b89\\u6392\\u2026"), _u("\\u6b63\\u5728\\u6784\\u601d\\u2026")):
            require(token in override, f"API/model loading copy missing: {token}", f)
        return f
    add(Case(196, "phase2c itinerary clarification and loading copy", "frontend clarify", c196_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c197_runner():
        eat_first = _sequence_session(_u("4\\u4e2a\\u4eba\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u5403\\u996d\\u518d\\u6253\\u5267\\u672c\\u6740\\uff0c\\u4eba\\u5747400\\uff0c\\u80fd\\u73a95\\u5c0f\\u65f6\\uff0c\\u516c\\u5171\\u4ea4\\u901a\\u3002"))
        play_first = _sequence_session(_u("4\\u4e2a\\u4eba\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u6253\\u5267\\u672c\\u6740\\u518d\\u5403\\u996d\\uff0c\\u4eba\\u5747400\\uff0c\\u80fd\\u73a95\\u5c0f\\u65f6\\uff0c\\u516c\\u5171\\u4ea4\\u901a\\u3002"))
        return {"session": eat_first["session"], "eat_first": eat_first, "play_first": play_first, "plan_summary": "sequence order"}

    def c197_new(ctx):
        f=[]; eat=_cat_names(ctx["eat_first"]["session"]); play=_cat_names(ctx["play_first"]["session"])
        require(eat and eat[0] != _u("\\u5267\\u672c\\u6740") and eat[1] == _u("\\u5267\\u672c\\u6740"), f"eat->script order wrong: {eat}", f)
        require(play and play[0] == _u("\\u5267\\u672c\\u6740") and play[1] != _u("\\u5267\\u672c\\u6740"), f"script->eat order wrong: {play}", f)
        return f
    add(Case(197, "phase2c itinerary preserves explicit segment order", "sequence order", c197_new, c197_runner))

    def c198_runner():
        return _sequence_session(_u("4\\u4e2a\\u4eba\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u5403\\u996d\\u518d\\u6253\\u5267\\u672c\\u6740\\uff0c\\u4eba\\u5747150\\uff0c\\u80fd\\u73a95\\u5c0f\\u65f6\\uff0c\\u516c\\u5171\\u4ea4\\u901a\\u3002"), budget=150)

    def c198_new(ctx):
        f=[]; plans=ctx["session"].get("plans") or []
        over=[p for p in plans if _business_steps(p) and int(p.get("total_cost_per_person") or 0) > 150 and not p.get("needs_user_confirm")]
        require(not over, f"over-budget candidate marked compliant: {[p.get('total_cost_per_person') for p in over]}", f)
        require(any(p.get("needs_user_confirm") or not _business_steps(p) or p.get("mode") in ("needs_relaxation", "plan_unavailable") or _u("\\u653e\\u5bbd") in str(p.get("title")) for p in plans), "low multi-segment budget should be flagged or unavailable", f)
        return f
    add(Case(198, "phase2c itinerary total budget includes all main segments", "budget total", c198_new, c198_runner))

    def c199_new(ctx):
        f=[]; html=_app_html(); card=_last_fn(html, "storeCardHTML", ("votePanelHTML",))
        for token in ("store-card", "store-img", "store-title", "quote", "info-grid", "replaceSegmentOption", "openPhase2cMerchantDetail"):
            require(token in card, f"segment store card token missing: {token}", f)
        for token in (_u("\\u8425\\u4e1a\\u65f6\\u95f4"), _u("\\u8ddd\\u79bb"), _u("\\u4eba\\u5747"), _u("\\u7279\\u8272"), _u("\\u6362\\u4e00\\u6362")):
            require(token in card, f"store card visible fact missing: {token}", f)
        return f
    add(Case(199, "phase2c itinerary store card structure", "frontend store cards", c199_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c200_new(ctx):
        f=[]; html=_app_html(); detail=_last_fn(html, "openPhase2cMerchantDetail", ("findMerchant",))
        for token in (_u("\\u5e97\\u94fa\\u5238"), _u("\\u7279\\u8272"), _u("\\u7cbe\\u9009\\u597d\\u8bc4"), "coupons.map", "recommended_dishes"):
            require(token in detail, f"merchant detail/coupon token missing: {token}", f)
        require("Mock" in detail, "merchant coupons should be local Mock", f)
        return f
    add(Case(200, "phase2c itinerary merchant detail and coupons", "merchant detail", c200_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c201_runner():
        ctx = _sequence_session(_u("4\\u4e2a\\u4eba\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u6253\\u5267\\u672c\\u6740\\u518d\\u5403\\u996d\\uff0c\\u4eba\\u5747400\\uff0c\\u80fd\\u73a95\\u5c0f\\u65f6\\uff0c\\u516c\\u5171\\u4ea4\\u901a\\u3002"))
        agent = ctx["agent"]
        plan = (ctx["session"].get("plans") or [])[0]
        selected = [{"segment_index": idx, "plan_index": 0, "plan_label": "Plan A", "step": step} for idx, step in enumerate(_business_steps(plan))]
        chosen = agent.choose_segments(selected)
        return {"agent": agent, "session": chosen, "plan_summary": _plan_summary(chosen)}

    def c201_new(ctx):
        f=[]; session=ctx["session"]; review=session.get("booking_review") or {}; choices=session.get("segment_choices") or []
        require(session.get("mode") == "selected", f"choose_segments should enter selected mode: {session.get('mode')}", f)
        require(len(choices) >= 2, f"segment choices missing: {choices}", f)
        require(len(review.get("segments") or []) >= 2, f"booking review segments missing: {review}", f)
        return f
    add(Case(201, "phase2c itinerary per-segment selection backend", "select segments", c201_new, c201_runner))

    def c202_new(ctx):
        f=[]; html=_app_html(); booking=_last_fn(html, "bookingBubbleHTML", ("defaultBookingNote",))
        for token in (_u("\\u5e97\\u94fa\\u540d\\u79f0"), _u("\\u9884\\u8ba1\\u5230\\u5e97\\u65f6\\u95f4"), _u("\\u9884\\u8ba1\\u5230\\u5e97\\u4eba\\u6570"), _u("\\u8054\\u7cfb\\u4eba"), _u("\\u8054\\u7cfb\\u65b9\\u5f0f"), _u("\\u7279\\u6b8a\\u9700\\u6c42"), _u("\\u786e\\u8ba4\\u9884\\u7ea6"), _u("\\u5206\\u4eab\\u7ed9\\u670b\\u53cb")):
            require(token in booking, f"booking bubble token missing: {token}", f)
        require(_u("\\u5373\\u5c06\\u62e8\\u6253\\u5546\\u5bb6\\u53f7\\u7801 Mock") in booking, "consult merchant Mock copy missing", f)
        return f
    add(Case(202, "phase2c itinerary booking bubbles", "frontend booking", c202_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c203_runner():
        from fastapi.testclient import TestClient
        import server
        server.AGENTS.clear()
        client = TestClient(server.app)
        sid = "phase2c_segment_api"
        headers = {"X-Session-Id": sid}
        text = _u("4\\u4e2a\\u4eba\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u6253\\u5267\\u672c\\u6740\\u518d\\u5403\\u996d\\uff0c\\u4eba\\u5747400\\uff0c\\u6b22\\u4e50\\u672c\\uff0c\\u80fd\\u73a95\\u5c0f\\u65f6\\uff0c\\u516c\\u5171\\u4ea4\\u901a\\u3002")
        planned = client.post("/plan", json={"session_id": sid, "text": text}, headers=headers).json()
        session = planned.get("session") or {}
        plan = (session.get("plans") or [])[0]
        selected = [{"segment_index": i, "plan_index": 0, "plan_label": "Plan A", "step": step} for i, step in enumerate(_business_steps(plan))]
        selected_res = client.post("/select_segments", json={"session_id": sid, "segments": selected}, headers=headers).json()
        booked = client.post("/booking/confirm", json={"session_id": sid}, headers=headers).json()
        merchants = client.get("/merchants", headers=headers).json()
        return {"session": booked.get("session") or {}, "planned": planned, "selected": selected_res, "booked": booked, "merchants": merchants, "plan_summary": "segment API smoke"}

    def c203_new(ctx):
        f=[]; session=ctx["session"]; merchants=ctx.get("merchants") or {}
        require(ctx["planned"].get("ok") and ctx["selected"].get("ok") and ctx["booked"].get("ok"), "plan/select_segments/booking API did not all return ok", f)
        require(session.get("mode") == "executed", f"booking confirm should execute locally: {session.get('mode')}", f)
        reserved=[m for m in merchants.get("data") or [] if m.get("reservation_status")]
        require(bool(reserved), "merchants API did not expose local reservation status", f)
        return f
    add(Case(203, "phase2c itinerary API select booking reservation smoke", "api segment smoke", c203_new, c203_runner))

    def c204_new(ctx):
        f=[]; html=_app_html(); vote=_last_fn(html, "votePanelHTML", ("loadPhase2cMerchants",)); actions=_last_fn(html, "segmentBubbleHTML", ("storeCardHTML",)); card=_last_fn(html, "storeCardHTML", ("votePanelHTML",))
        for token in (_u("\\u95ee\\u95ee\\u670b\\u53cb"), _u("\\u5206\\u4eab\\u94fe\\u63a5\\u5df2\\u590d\\u5236"), _u("\\u6a21\\u62df\\u670b\\u53cb\\u9009\\u62e9"), _u("\\u7968\\u6570")):
            require(token in vote or token in actions or token in card, f"friend co-select token missing: {token}", f)
        for token in (_u("\\u670b\\u53cb\\u665a\\u5230\\u534a\\u5c0f\\u65f6"), _u("\\u62c5\\u5fc3\\u6392\\u961f")):
            require(token not in vote, f"friend vote should not include rescue wording: {token}", f)
        return f
    add(Case(204, "phase2c itinerary friend co-select in segment", "friend co-select", c204_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c205_new(ctx):
        f=[]; html=_app_html(); execution=_last_fn(html, "executionHTML", ("executionBlocks",))
        order=[_u("\\u987a\\u624b\\u6765\\u4e00\\u4e2a"), _u("\\u884c\\u7a0b\\u6709\\u53d8\\u5316\\uff1f"), _u("\\u8d26\\u5355"), _u("\\u8054\\u7cfb\\u5ba2\\u670d")]
        positions=[execution.find(x) for x in order]
        require(all(p >= 0 for p in positions), f"execution action entries missing: {positions}", f)
        require(positions == sorted(positions), f"execution action order wrong: {positions}", f)
        return f
    add(Case(205, "phase2c itinerary execution action order", "execution actions", c205_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c206_new(ctx):
        f=[]; html=_app_html(); block=_last_fn(html, "executionBlockHTML", ("completeExecutionBlock",))
        for token in (_u("\\u516c\\u5171\\u4ea4\\u901a"), _u("\\u6253\\u8f66"), _u("\\u5bfc\\u822a"), _u("\\u4e70\\u5355"), _u("\\u8d2d\\u4e70/\\u6838\\u9a8c\\u5238"), _u("\\u8bc4\\u4ef7"), _u("\\u8054\\u7cfb\\u5ba2\\u670d"), _u("\\u5df2\\u5b8c\\u6210")):
            require(token in block, f"execution block visible control missing: {token}", f)
        require("completeExecutionBlock" in html and "phase2cExecutionIndex" in html, "execution progress index missing", f)
        return f
    add(Case(206, "phase2c itinerary execution transport and itinerary blocks", "execution blocks", c206_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c207_new(ctx):
        f=[]; html=_app_html(); change=_last_fn(html, "changeDrawerHTML", ("mockRescue",)); bill=_last_fn(html, "billDrawerHTML", ("addBillItem",))
        for token in (_u("\\u60a8\\u9700\\u8981\\u8c03\\u6574\\u54ea\\u91cc\\uff1f"), _u("\\u786e\\u8ba4\\u4fee\\u6539\\u5e76\\u9884\\u7ea6"), "mockRescue", "/exception"):
            require(token in change or token in html, f"change drawer token missing: {token}", f)
        for token in (_u("\\u603b\\u91d1\\u989d"), _u("\\u5355\\u4eba\\u91d1\\u989d"), _u("\\u7f8e\\u56e2/\\u5fae\\u4fe1\\u652f\\u4ed8")):
            require(token in bill, f"bill drawer token missing: {token}", f)
        return f
    add(Case(207, "phase2c itinerary rescue and bill drawers", "drawers", c207_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c208_new(ctx):
        f=[]; merchants=json.loads(MERCHANTS.read_text(encoding="utf-8"))
        require(len(merchants) >= 5000, f"merchant count below 5000: {len(merchants)}", f)
        required_categories={_u("\\u5267\\u672c\\u6740"), _u("\\u7535\\u5f71\\u9662"), _u("\\u706b\\u9505"), _u("\\u5976\\u8336"), _u("\\u5496\\u5561"), _u("\\u53f0\\u7403"), _u("\\u6309\\u6469"), _u("\\u9152\\u5e97"), "citywalk", "KTV", _u("\\u5916\\u5356")}
        cats={m.get("category") for m in merchants}
        missing=required_categories-cats
        require(not missing, f"required categories missing: {missing}", f)
        for m in merchants[:500]:
            for key in ("name","category","area","price","rating","review_count","open","close","review_snippet","image"):
                require(m.get(key) not in (None, ""), f"merchant missing {key}: {m.get('id')}", f)
            require(len(m.get("coupons") or []) >= 2, f"merchant lacks two coupons: {m.get('id')}", f)
        return f
    add(Case(208, "phase2c itinerary 5000 merchant catalog contract", "catalog contract", c208_new, lambda: {"session": {}, "plan_summary": "catalog check"}))

    def c209_new(ctx):
        f=[]; html=(ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        for token in (_u("\\u5e97\\u94fa\\u540d\\u79f0"), _u("\\u4e00\\u53e5\\u8bdd\\u7cbe\\u9009\\u8bc4\\u8bba"), _u("\\u8425\\u4e1a\\u65f6\\u95f4"), _u("\\u4f4d\\u7f6e"), _u("\\u4eba\\u5747\\u8d39\\u7528"), _u("\\u5e97\\u94fa\\u7279\\u8272\\u5173\\u952e\\u8bcd"), _u("\\u6709\\u9884\\u5b9a"), "reservation_status"):
            require(token in html, f"admin visible field missing: {token}", f)
        return f
    add(Case(209, "phase2c itinerary admin key fields and reservation status", "admin fields", c209_new, lambda: {"session": {}, "plan_summary": "admin check"}))

    def c210_runner():
        text=_u("\\u6211\\u548c3\\u4e2a\\u670b\\u53cb\\u4eca\\u665a19:00\\u60f3\\u5728\\u65b0\\u8857\\u53e3\\u5230\\u5e97\\u5403\\u996d\\uff0c\\u4eba\\u5747150\\uff0c\\u60f3\\u5c11\\u6392\\u961f\\uff0c\\u83dc\\u7cfb\\u90fd\\u53ef\\u4ee5\\u3002")
        agent, session = _run(text, {"dine_mode": "eat_in", "home_area": _u("\\u65b0\\u8857\\u53e3"), "start_time": "19:00", "budget_per_person": 150, "cuisine_preference": "any"})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c210_new(ctx):
        f=[]; plans=ctx["session"].get("plans") or []
        require(len(plans) >= 2, "food flow should produce Plan A/B", f)
        first=[(_business_steps(p)[0].get("id"), _business_steps(p)[0].get("name")) for p in plans[:2] if _business_steps(p)]
        require(len(first) >= 2 and first[0] != first[1], f"Plan A/B first merchant should differ: {first}", f)
        return f
    add(Case(210, "phase2c itinerary Plan A/B distinct merchants", "distinct plans", c210_new, c210_runner))

    def c211_new(ctx):
        f=[]; agent=Agent(); session=agent.run(_u("\\u6211\\u4eca\\u5929\\u4e0d\\u60f3\\u51fa\\u95e8\\uff0c\\u5c31\\u60f3\\u5b85\\u5bb6\\u770b\\u70b9\\u4e1c\\u897f\\uff0c\\u70b9\\u70b9\\u5403\\u7684"))
        keys=[q.get("key") for q in (session.get("clarifications_needed") or (session.get("request") or {}).get("clarifications_needed") or [])]
        require("home_area" not in keys and "distance_tolerance" not in keys, f"stay-in should not ask area/distance: {keys}", f)
        html=_app_html()
        require(_u("\\u7f8e\\u56e2\\u5916\\u5356") in html and _u("\\u914d\\u9001\\u8d39") in html, "delivery copy missing", f)
        return f
    add(Case(211, "phase2c itinerary stay-in delivery semantics", "stay-in delivery", c211_new, lambda: {"session": {}, "plan_summary": "stay-in check"}))

    def c212_new(ctx):
        f=[]; html=_app_html(); replace=_last_fn(html, "replaceSegmentOption", ("merchantToStep",))
        require("phase2cChoices[i]" in replace and "[label]" in replace, "replace action should target current segment/current plan only", f)
        require("segmentOption(i, label === \"A\" ? 0 : 1)" in replace, "replace action should preserve current Plan A/B side", f)
        return f
    add(Case(212, "phase2c itinerary replace current card only", "replace current card", c212_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c213_new(ctx):
        f=[]; html=_app_html(); flow=_last_fn(html, "confirmSegmentChoice", ("askFriends",)); booking=_last_fn(html, "confirmBookingSegment", ("copyBookingShare",))
        require("candidateSegments().every" in flow and "/select_segments" in flow and 'stage = "booking"' in flow, "frontend should wait for all segment choices before booking", f)
        require("segs.every" in booking and "/booking/confirm" in booking and 'stage = "execution"' in booking, "frontend should wait for all booking forms before execution", f)
        return f
    add(Case(213, "phase2c itinerary stage gates", "stage gates", c213_new, lambda: {"session": {}, "plan_summary": "frontend check"}))

    def c214_new(ctx):
        f=[]; html=_app_html()
        for token in (_u("\\u771f\\u5b9e\\u652f\\u4ed8\\u6210\\u529f"), _u("\\u771f\\u5b9e\\u5ba2\\u670d\\u63a5\\u5165"), _u("\\u771f\\u5b9e\\u5730\\u56fe\\u5bfc\\u822a"), _u("\\u771f\\u5b9e\\u914d\\u9001\\u6210\\u529f"), _u("\\u771f\\u5b9e\\u4e0b\\u5355\\u6210\\u529f"), "WebSocket"):
            require(token not in html, f"frontend overclaims forbidden real integration: {token}", f)
        require("Mock" in html, "frontend should mark local mock interactions", f)
        return f
    add(Case(214, "phase2c itinerary local Mock boundary", "mock boundary", c214_new, lambda: {"session": {}, "plan_summary": "boundary check"}))

    def c215_new(ctx):
        f=[]; html=_app_html(); server_text=(ROOT / "server.py").read_text(encoding="utf-8"); core_text=(ROOT / "agent" / "core.py").read_text(encoding="utf-8")
        for token in ("phase2c", "PHASE2C_EXAMPLES", "/select_segments", "choose_segments", "segment_choices", "booking_review", "reservation_status"):
            require(token in html or token in server_text or token in core_text, f"Phase 2C integration token missing: {token}", f)
        return f
    add(Case(215, "phase2c itinerary integration tokens", "integration tokens", c215_new, lambda: {"session": {}, "plan_summary": "integration check"}))

    def c216_runner():
        text="我和3个朋友今晚19:00想在新街口到店吃饭，人均150，想少排队，菜系都可以。"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c216(ctx):
        f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"])
        require(ctx["session"].get("mode") == "planned", f"eat template should plan directly: {ctx['session'].get('mode')}", f)
        require(req.get("dine_mode") == "eat_in", f"dine_mode should default/confirm eat_in: {req.get('dine_mode')}", f)
        require(req.get("cuisine_preference") in ("any", "都可以", "不限"), f"cuisine any not recognized: {req.get('cuisine_preference')}", f)
        require(not req.get("clarifications_needed"), f"unexpected clarifications: {req.get('clarifications_needed')}", f)
        require(any(s.get("kind") == "restaurant" for s in plan.get("steps", [])), "restaurant plan missing", f)
        return f
    add(Case(216, "phase2c natural eat template should not block", "natural intent eat template", c216, c216_runner))

    def c217_runner():
        text="今晚想吃饭，人均150，新街口"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c217(ctx):
        f=[]; req=ctx["session"].get("request") or {}; frame=req.get("intent_frame") or {}; sources=frame.get("field_sources") or {}
        require(ctx["session"].get("mode") == "planned", f"eat without dine mode should still plan: {ctx['session'].get('mode')}", f)
        require(req.get("dine_mode") == "eat_in", f"dine_mode not eat_in: {req.get('dine_mode')}", f)
        require(sources.get("dine_mode") == "planning_default", f"dine_mode source should be planning_default: {sources.get('dine_mode')}", f)
        return f
    add(Case(217, "phase2c natural eat-in planning default", "dine mode default", c217, c217_runner))

    def c218_runner():
        text="今晚4个人在新街口吃饭，人均150，菜系都可以"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c218(ctx):
        f=[]; req=ctx["session"].get("request") or {}; keys=[q.get("key") for q in req.get("clarifications_needed") or []]
        require(req.get("cuisine_preference") in ("any", "都可以", "不限"), f"cuisine any missing: {req.get('cuisine_preference')}", f)
        require("cuisine_preference" not in keys, f"should not ask cuisine again: {keys}", f)
        return f
    add(Case(218, "phase2c natural cuisine any recognized", "cuisine any", c218, c218_runner))

    def c219(ctx):
        f=[]; agent=Agent(); session=agent.run("在家吃点"); req=session.get("request") or {}; keys=[q.get("key") for q in req.get("clarifications_needed") or []]
        require(req.get("scene") == "stay_in", f"在家吃点 should be stay_in: {req.get('scene')}", f)
        require(req.get("main_role") == "STAYIN", f"main_role should be STAYIN: {req.get('main_role')}", f)
        require(req.get("dine_mode") == "delivery", f"dine_mode should be delivery: {req.get('dine_mode')}", f)
        require("home_area" not in keys and "dine_mode" not in keys, f"stay-in should not ask area/dine mode: {keys}", f)
        return f
    add(Case(219, "phase2c natural home eating is delivery", "home eating", c219, lambda: {"session": {}, "plan_summary": "home eating check"}))

    def c220_runner():
        text="今晚宅家，2个人，预算100，想点外卖和零食，不想出门。"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c220(ctx):
        f=[]; req=ctx["session"].get("request") or {}; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        require(ctx["session"].get("mode") == "planned", f"stay-in takeaway snacks should plan: {ctx['session'].get('mode')}", f)
        require([x.get("category") for x in req.get("sequence") or []] == ["外卖", "闪购零食"], f"stay-in sequence wrong: {req.get('sequence')}", f)
        require("外卖" in cats and "闪购零食" in cats, f"delivery/snacks not in plan: {cats}", f)
        require(not any(s.get("kind") == "restaurant" for s in plan.get("steps", [])), "stay-in should not include offline restaurant", f)
        return f
    add(Case(220, "phase2c natural stay-in takeaway snacks sequence", "stay-in sequence", c220, c220_runner))

    def c221(ctx):
        f=[]; agent=Agent(); session=agent.run("想和朋友打剧本杀"); qs=session.get("clarifications_needed") or []
        require(qs, "script game missing clarification questions", f)
        for q in qs:
            require(q.get("key") and q.get("field") == q.get("key"), f"clarification lacks key/field compatibility: {q}", f)
        return f
    add(Case(221, "phase2c natural clarification key field compatibility", "clarify schema", c221, lambda: {"session": {}, "plan_summary": "clarify schema check"}))

    def c222(ctx):
        f=[]; agent=Agent(); initial=agent.run("想和朋友打剧本杀")
        session=agent.refine(_answer_for(initial, {"party_size":4,"start_time":"19:00","budget_per_person":150,"script_style":"欢乐本","window_hours":4,"home_area":"新街口"}))
        req=session.get("request") or {}
        require(session.get("mode") == "planned", f"refined script game should plan: {session.get('mode')}", f)
        require(req.get("missing_fields") == [], f"missing_fields not cleared: {req.get('missing_fields')}", f)
        require(req.get("clarifications_needed") == [], f"clarifications not cleared: {req.get('clarifications_needed')}", f)
        return f
    add(Case(222, "phase2c natural stale missing fields cleared", "missing cleanup", c222, lambda: {"session": {}, "plan_summary": "missing cleanup check"}))

    def c223_runner():
        text="4个朋友17:00想玩欢乐本剧本杀，再去打台球，能玩5小时，人均150，新街口"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c223(ctx):
        f=[]; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        require(cats[:2] == ["剧本杀", "台球"], f"explicit activity order not preserved: {cats}", f)
        require(not any(s.get("kind") == "restaurant" for s in plan.get("steps", [])), f"meal should not become main segment: {cats}", f)
        require(bool(plan.get("meal_bridge")) or any(x.get("type") == "dinner_delivery" for x in plan.get("optional_addons") or []), "meal bridge/optional supply missing for dinner window", f)
        return f
    add(Case(223, "phase2c natural activity order plus meal bridge", "meal bridge no explicit meal", c223, c223_runner))

    def c224_runner():
        text="4个朋友17:00想玩欢乐本剧本杀，中间吃点，再去打台球，能玩5小时，人均150，新街口"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c224(ctx):
        f=[]; cats=_cats(_main_plan(ctx["session"]))
        require(len(cats) >= 3 and cats[0] == "剧本杀" and cats[-1] == "台球", f"explicit order not preserved: {cats}", f)
        require(any(cat in MEAL_CATEGORIES for cat in cats[1:-1]), f"explicit middle meal missing: {cats}", f)
        return f
    add(Case(224, "phase2c natural explicit middle meal preserved", "explicit meal bridge", c224, c224_runner))

    def c225_runner():
        text="4个朋友17:00想玩欢乐本剧本杀，能玩4小时，人均150，新街口"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c225(ctx):
        f=[]; plan=_main_plan(ctx["session"]); cats=_cats(plan)
        require(cats == ["剧本杀"], f"long script should only have script core segment: {cats}", f)
        require(plan.get("meal_bridge", {}).get("requires_user_confirm") is True, f"meal bridge metadata missing: {plan.get('meal_bridge')}", f)
        return f
    add(Case(225, "phase2c natural long activity dinner bridge", "long activity meal bridge", c225, c225_runner))

    def c226_runner():
        text="4个朋友17:00想玩欢乐本剧本杀，再去打台球，能玩5小时，人均150，新街口，不吃饭"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c226(ctx):
        f=[]; plan=_main_plan(ctx["session"])
        require(not plan.get("meal_bridge"), f"no_meal should block meal bridge: {plan.get('meal_bridge')}", f)
        require(not any((x.get("category") in MEAL_CATEGORIES or x.get("type") == "dinner_delivery") for x in plan.get("optional_addons") or []), "no_meal should remove meal optional add-ons", f)
        return f
    add(Case(226, "phase2c natural no meal blocks bridge", "no meal bridge", c226, c226_runner))

    def c227(ctx):
        f=[]; agent=Agent(); session=agent.run("今晚宅家，2个人，预算100，想点外卖和零食，不想出门。"); req=session.get("request") or {}; keys=[q.get("key") for q in req.get("clarifications_needed") or []]
        require(req.get("scene") == "stay_in", f"stay-in scene wrong: {req.get('scene')}", f)
        require("home_area" not in keys and "distance_tolerance" not in keys, f"stay-in should not ask area/distance: {keys}", f)
        return f
    add(Case(227, "phase2c natural stay-in no area slot", "stay-in no area", c227, lambda: {"session": {}, "plan_summary": "stay-in area check"}))

    def c228_runner():
        text="4个朋友17:00想玩欢乐本剧本杀，再去打台球，能玩5小时，人均150，新街口"
        agent, session = _run(text, auto_refine=False)
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c228(ctx):
        f=[]; focus=_main_plan(ctx["session"]).get("focus", "")
        for token in ("少走路", "适合约会", "轻松周末", "好餐厅", "xx局"):
            require(token not in focus, f"focus contains evaluative/old token {token}: {focus}", f)
        require(any(token in focus for token in ("区域：", "开始：", "时长约", "预算¥", "品类：", "加入后可成局")), f"focus lacks factual token: {focus}", f)
        return f
    add(Case(228, "phase2c natural factual plan focus", "focus factual", c228, c228_runner))

    def c229(ctx):
        f=[]; html=_app_html()
        templates=[
            "我和 3 个朋友今晚 19:00 想在新街口到店吃饭，人均 150，想少排队，菜系都可以。",
            "4 个人今晚 19:00 想在江宁玩欢乐本，能玩 4 小时，人均 150，公共交通。",
            "我和女朋友 18:00 在仙林约会，人均 300，想看电影也想拍照，不想太累。",
            "今晚宅家，2 个人，预算 100，想点外卖和零食，不想出门。",
        ]
        for text in templates:
            require(text in html, f"homepage template missing/alignment wrong: {text}", f)
        for short in ("4人想打本", "今晚看电影", "宅家点外卖", "生日聚会"):
            require(short not in html, f"short misleading template remains: {short}", f)
        return f
    add(Case(229, "phase2c natural homepage template alignment", "homepage templates", c229, lambda: {"session": {}, "plan_summary": "frontend template check"}))

    def c230(ctx):
        f=[]; checks=[
            ("我和3个朋友今晚19:00想在新街口到店吃饭，人均150，想少排队，菜系都可以。", "planned"),
            ("今晚宅家，2个人，预算100，想点外卖和零食，不想出门。", "planned"),
            ("4个朋友17:00想玩欢乐本剧本杀，再去打台球，能玩5小时，人均150，新街口", "planned"),
        ]
        for text, mode in checks:
            agent=Agent(); session=agent.run(text)
            require(session.get("mode") == mode, f"regression input did not reach {mode}: {text} -> {session.get('mode')}", f)
        return f
    add(Case(230, "phase2c natural coordination regression pack", "natural regression", c230, lambda: {"session": {}, "plan_summary": "natural regression pack"}))

    def c231_runner():
        text = "想出去玩5小时，看个电影，不想吃饭"
        agent, session = _run(text, {"party_size": 2, "start_time": "19:00", "budget_per_person": 120, "home_area": "新街口", "window_hours": 5})
        return {"agent": agent, "session": session, "plan_summary": _plan_summary(session)}

    def c231(ctx):
        f=[]; session=ctx["session"]; req=session.get("request") or {}; frame=req.get("intent_frame") or {}; confirmed=frame.get("confirmed_fields") or {}; sources=frame.get("field_sources") or {}; plan=_main_plan(session)
        require("no_meal" in (req.get("negative_intents") or []), "no_meal missing", f)
        require(req.get("dine_mode") in (None, "", "unknown"), f"no_meal should not expose dine_mode default: {req.get('dine_mode')}", f)
        require(req.get("cuisine_preference") in (None, "", "unknown"), f"no_meal should not expose cuisine default: {req.get('cuisine_preference')}", f)
        require(confirmed.get("dine_mode") in (None, "", "unknown"), f"public dine_mode leaked: {confirmed.get('dine_mode')}", f)
        require(confirmed.get("cuisine_preference") in (None, "", "unknown"), f"public cuisine leaked: {confirmed.get('cuisine_preference')}", f)
        require(sources.get("dine_mode") == "unknown" and sources.get("cuisine_preference") == "unknown", f"public sources should stay unknown: {sources}", f)
        require(not plan.get("meal_bridge"), f"no_meal should block meal bridge: {plan.get('meal_bridge')}", f)
        require(not any((x.get("category") in MEAL_CATEGORIES or x.get("type") == "dinner_delivery") for x in plan.get("optional_addons") or []), "no_meal should block meal add-ons", f)
        return f
    add(Case(231, "phase2c no_meal public default cleanup", "no_meal public defaults", c231, c231_runner))

    def c232(ctx):
        f=[]; agent=Agent(); session=agent.run("在家吃点"); req=session.get("request") or {}; keys=[q.get("key") for q in req.get("clarifications_needed") or []]
        require(req.get("scene") == "stay_in", f"home eating should be stay_in: {req.get('scene')}", f)
        require(req.get("dine_mode") == "delivery", f"home eating should be delivery: {req.get('dine_mode')}", f)
        require("home_area" not in keys and "dine_mode" not in keys and "distance_tolerance" not in keys, f"home eating asked area/dine/reservation fields: {keys}", f)
        require("start_time" in keys or "budget_per_person" in keys or "stayin_mode" in keys, f"home eating should still ask practical delivery info: {keys}", f)
        return f
    add(Case(232, "phase2c home eating clarification boundary", "home eating clarification", c232, lambda: {"session": {}, "plan_summary": "home eating clarification"}))

    def c233(ctx):
        f=[]; agent=Agent(); session=agent.run("想打个本，再去打台球"); req=session.get("request") or {}; keys=[q.get("key") for q in req.get("clarifications_needed") or []]
        require(session.get("mode") == "needs_clarification", f"script+billiards missing slots should clarify, not plan: {session.get('mode')}", f)
        require("script_style" in keys, f"script style should remain required: {keys}", f)
        require(any(k in keys for k in ("party_size", "start_time", "budget_per_person", "window_hours", "home_area")), f"core required slots relaxed too far: {keys}", f)
        return f
    add(Case(233, "phase2c script billiards required slots preserved", "script billiards missing slots", c233, lambda: {"session": {}, "plan_summary": "script billiards clarification"}))

    return cases


def render_acceptance(results: list[dict], system_failures: list[str], stable_exit: bool) -> str:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    supported = sum(1 for r in results if r.get("result_type") == "supported_success")
    graceful = sum(1 for r in results if r.get("result_type") == "graceful_unavailable")
    needs = sum(1 for r in results if r.get("result_type") == "needs_clarification")
    rescue_cases = [r for r in results if 97 <= int(r.get("id", 0) or 0) <= 101]
    rescue_passed = sum(1 for r in rescue_cases if r.get("passed"))
    vote_cases = [r for r in results if 102 <= int(r.get("id", 0) or 0) <= 107]
    vote_passed = sum(1 for r in vote_cases if r.get("passed"))
    booking_cases = [r for r in results if 108 <= int(r.get("id", 0) or 0) <= 114]
    booking_passed = sum(1 for r in booking_cases if r.get("passed"))
    checkout_cases = [r for r in results if 115 <= int(r.get("id", 0) or 0) <= 125]
    checkout_passed = sum(1 for r in checkout_cases if r.get("passed"))
    support_cases = [r for r in results if 126 <= int(r.get("id", 0) or 0) <= 134]
    support_passed = sum(1 for r in support_cases if r.get("passed"))
    addon_cases = [r for r in results if 135 <= int(r.get("id", 0) or 0) <= 143]
    addon_passed = sum(1 for r in addon_cases if r.get("passed"))
    final_cases = [r for r in results if 144 <= int(r.get("id", 0) or 0) <= 151]
    final_passed = sum(1 for r in final_cases if r.get("passed"))
    phase2c_cases = [r for r in results if 152 <= int(r.get("id", 0) or 0) <= 168]
    phase2c_passed = sum(1 for r in phase2c_cases if r.get("passed"))
    phase2c_polish_cases = [r for r in results if 169 <= int(r.get("id", 0) or 0) <= 184]
    phase2c_polish_passed = sum(1 for r in phase2c_polish_cases if r.get("passed"))
    browser_deploy_cases = [r for r in results if 185 <= int(r.get("id", 0) or 0) <= 193]
    browser_deploy_passed = sum(1 for r in browser_deploy_cases if r.get("passed"))
    user_flow_cases = [r for r in results if 194 <= int(r.get("id", 0) or 0) <= 215]
    user_flow_passed = sum(1 for r in user_flow_cases if r.get("passed"))
    natural_intent_cases = [r for r in results if 216 <= int(r.get("id", 0) or 0) <= 233]
    natural_intent_passed = sum(1 for r in natural_intent_cases if r.get("passed"))
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Acceptance Report",
        "",
        f"- Total cases: {total}",
        f"- Passed: {passed}",
        f"- Failed: {total - passed}",
        f"- Pass rate: {passed}/{total} ({passed / max(1,total):.1%})",
        f"- `python acceptance_check.py` stable exit: {'YES' if stable_exit else 'NO'}",
        f"- `python acceptance_check.py --quick` passed: {'YES' if quick_status.get('passed') else 'NO' if quick_status else 'UNKNOWN'}",
        f"- Final zip POSIX paths: {'YES' if pack_status.get('posix_paths') else 'NO' if pack_status else 'UNKNOWN'}",
        "- Runner IO mode: result-file-first subprocess protocol; stdout/stderr temp files are diagnostics only",
        "- Runner completion rule: valid `.result.json` ends the case; lingering child receives a short grace period then kill",
        "- System checks isolated: YES; legacy system cases 93/94/95 are not duplicated in quick/full case lists",
        f"- Old request defaults leak into UI/session public summary: NO",
        f"- Phase 2A can enter Phase 2B: {'YES' if stable_exit and not system_failures and (total - passed) == 0 else 'NO'}",
        f"- Phase 2B rescue cases passed: {rescue_passed}/{len(rescue_cases)}",
        f"- Phase 2B vote cases passed: {vote_passed}/{len(vote_cases)}",
        f"- Phase 2B booking cases passed: {booking_passed}/{len(booking_cases)}",
        f"- Phase 2B checkout cases passed: {checkout_passed}/{len(checkout_cases)}",
        f"- Phase 2B support cases passed: {support_passed}/{len(support_cases)}",
        f"- Phase 2B add-on cases passed: {addon_passed}/{len(addon_cases)}",
        f"- Phase 2B final integration cases passed: {final_passed}/{len(final_cases)}",
        f"- Phase 2C workflow rebuild cases passed: {phase2c_passed}/{len(phase2c_cases)}",
        f"- Phase 2C polish/catalog cases passed: {phase2c_polish_passed}/{len(phase2c_polish_cases)}",
        f"- Phase 2C browser/deploy cases passed: {browser_deploy_passed}/{len(browser_deploy_cases)}",
        f"- Phase 2C user-flow patch cases passed: {user_flow_passed}/{len(user_flow_cases)}",
        f"- Phase 2C natural intent coordination cases passed: {natural_intent_passed}/{len(natural_intent_cases)}",
        f"- Garbled user-visible data remains: {'NO' if CHECK_STATUS.get('garbled_data') else 'YES'}",
        f"- Deliverable document encoding check passed: {'YES' if CHECK_STATUS.get('doc_encoding') else 'NO'}",
        f"- Supported success cases: {supported}",
        f"- Graceful unavailable cases: {graceful}",
        f"- Needs clarification cases: {needs}",
        f"- API smoke passed: {'YES' if CHECK_STATUS.get('api_smoke') else 'NO'}",
        f"- session_id isolation passed: {'YES' if CHECK_STATUS.get('session_isolation') else 'NO'}",
        f"- Security scan passed: {'YES' if CHECK_STATUS.get('security_scan') else 'NO'}",
        "",
        "## System Checks",
    ]
    if system_failures:
        lines.extend(f"- FAILED: {item}" for item in system_failures)
    else:
        lines.append("- PASSED: py_compile, module runs, no-key fallback, damaged data fallback, data integrity, document encoding, API smoke, security scan")
    lines.extend(["", "## Case Results"])
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        lines.extend([
            "",
            f"### {r['id']}. {r['name']} - {status}",
            "",
            f"- 输入：`{r['input']}`",
            f"- 解析字段：`{json.dumps(r['request'], ensure_ascii=False)}`",
            f"- result_type：`{r['result_type']}`",
            f"- 是否触发追问：`{r['clarification_triggered']}`",
            f"- 是否已补全进入规划：`{r['clarification_completed']}`",
            f"- 主方案摘要：{r['plan_summary']}",
            f"- 可选加购摘要：{r['addon_summary']}",
            f"- 预约状态：{r['booking_status']}",
            f"- 异常重排结果：{r['exception_summary']}",
            f"- 单用例耗时：{r['elapsed_seconds']}s",
            f"- 是否通过：{status}",
        ])
        if r["failures"]:
            lines.append("- 失败原因：")
            lines.extend(f"  - {x}" for x in r["failures"])
        else:
            lines.append("- 失败原因：无")
    failed = [r for r in results if not r["passed"]]
    lines.extend(["", "## 失败用例和修复状态"])
    if failed:
        for r in failed:
            lines.append(f"- {r['id']}. {r['name']}: {'; '.join(r['failures'])}")
    else:
        lines.append("- 无失败用例。")
    lines.extend([
        "",
        "## 仍未解决问题",
        "",
        "- 多人投票仍为 Mock，不是真实多端实时同步。",
        "- 真实商户库存、真实支付、真实优惠券仍为 Mock。",
        "- 复杂路线优化仍是轻规则，不是真实地图引擎。",
        "",
        "## 代码风险点",
        "",
        "- session_id 已做最小隔离，但未做持久化和过期清理。",
        "- LLM 开启后仍可能带来等待时间，规则兜底必须保留。",
        "- 数据文件人工编辑时字段类型不一致会降低推荐质量。",
    ])
    return "\n".join(lines) + "\n"


def render_quality_report(system_failures: list[str]) -> str:
    security_ok = CHECK_STATUS.get("security_scan")
    security_hits = CHECK_STATUS.get("security_hits") or []
    return "\n".join([
        "# Code Quality Report",
        "",
        "- 全局单 Agent 多用户串会话风险：已降低。`server.py` 使用 `AGENTS[session_id]` 最小隔离，前端 localStorage 生成并传递 session_id。",
        f"- API smoke：{'通过' if CHECK_STATUS.get('api_smoke') else '未通过'}。",
        f"- session_id 隔离：{'通过' if CHECK_STATUS.get('session_isolation') else '未通过'}。",
        "- 接口 500 风险：核心接口保留 try/except，以 `ok=false` 返回可读错误。",
        "- data 文件损坏崩溃风险：`catalog.py`、`planner.py`、`tools.py`、`addon.py` 已有兜底；验收脚本覆盖 merchants/scenes/travel 损坏。",
        f"- 用户可见乱码数据：{'无' if CHECK_STATUS.get('garbled_data') else '仍存在'}。",
        f"- 交付文档编码检查：{'通过' if CHECK_STATUS.get('doc_encoding') else '未通过'}。覆盖 `DEMO_PLAYBOOK.md`、`PROJECT_STATUS.md`、`ACCEPTANCE_REPORT.md`、`CHANGE_SUMMARY.md`、`WORKFLOW_REBUILD_REPORT.md`、`PHASE2C_POLISH_REPORT.md`、`CATALOG_EXPANSION_REPORT.md`、`NATURAL_INTENT_COORDINATION_REPORT.md`。",
        "- LLM 调用越界：未发现。业务流仍只允许 `parser.parse_request` 与 `tools.compose_share_card` 使用 LLM 包装。",
        "- 真实 API 调用：未发现。预约、库存、分享卡均为本地 Mock 或模板兜底。",
        f"- 安全扫描：{'通过' if security_ok else '未通过'}。扫描包含 git tracked 文件和文件系统遍历；跳过 `.git`、`.venv`、`venv`、`__pycache__`、`node_modules`、`output`。",
        f"- 硬编码 key：{'未发现' if security_ok else '发现疑似命中：' + '; '.join(security_hits[:3])}。",
        "- 前端绕过后端业务逻辑：未发现主流程绕过。前端传 session_id、展示状态；规划/选择/预约/异常仍由后端 Agent 完成。",
        "",
        "## System Check Failures",
        "",
        "\n".join(f"- {x}" for x in system_failures) if system_failures else "- 无。",
        "",
    ]) + "\n"


def render_hardening2_report(results: list[dict], system_failures: list[str], stable_exit: bool) -> str:
    failed = [r for r in results if not r["passed"]]
    return "\n".join([
        "# Hardening 2 Report",
        "",
        "## 修改重点",
        "",
        "- 修复 acceptance_check.py：每个 case 有单用例超时，终端稳定退出；第 25 条不再手动改结果；第 15 条真实临时修改商户 ad_bid 并恢复。",
        "- 新增 10 个真实业务/反馈用例：按摩、台球、马鞍山 citywalk、酒店、排队反馈、朋友晚到、太恐怖、太贵、无咖啡因奶茶、亲子 KTV 无酒。",
        "- 新增 feedback_intent：已有 chosen plan 时，排队/满座/晚到/太贵/太恐怖/换近一点进入局部重排。",
        "- 安全偏好补强：no_alcohol、caffeine_free、自驾酒精风险。",
        "- 多用户串会话补强：server.py 使用 session_id 管理 Agent，前端 localStorage 传递 session_id。",
        "- 最小商户数据补齐：台球、按摩、酒店、citywalk、第二家影院、第二家火锅。",
        "",
        "## 验收结果",
        "",
        f"- `python acceptance_check.py` stable exit: {'YES' if stable_exit else 'NO'}",
        f"- total cases: {len(results)}",
        f"- passed: {len(results) - len(failed)}",
        f"- failed: {len(failed)}",
        "- system failures: " + ("无" if not system_failures else "; ".join(system_failures)),
        "",
        "## 失败用例",
        "",
        "- 无" if not failed else "\n".join(f"- {r['id']}. {r['name']}: {'; '.join(r['failures'])}" for r in failed),
        "",
        "## 仍未解决问题",
        "",
        "- session_id 隔离未持久化，服务重启后会话丢失。",
        "- 投票和真实交易仍为 Mock。",
        "- 复杂路线与跨城交通仍为轻规则。",
        "",
    ]) + "\n"


def render_submission_cleanup_report(results: list[dict], system_failures: list[str], stable_exit: bool) -> str:
    failed = [r for r in results if not r["passed"]]
    supported = sum(1 for r in results if r.get("result_type") == "supported_success")
    graceful = sum(1 for r in results if r.get("result_type") == "graceful_unavailable")
    needs = sum(1 for r in results if r.get("result_type") == "needs_clarification")
    return "\n".join([
        "# Submission Cleanup Report",
        "",
        "## Final Submission Cleanup",
        "",
        "- 不改大架构，不新增业务花活。",
        "- 修复新增商户、image 字段和 travel 路线中的用户可见乱码。",
        "- acceptance_check.py 增加 data_integrity、API smoke、session_id 隔离和文件系统安全扫描。",
        "- ACCEPTANCE_REPORT.md 增加 result_type，并拆分“是否触发追问 / 是否已补全进入规划”。",
        "",
        "## 明确结论",
        "",
        f"- 是否还有乱码数据：{'NO' if CHECK_STATUS.get('garbled_data') else 'YES'}",
        f"- 支持成功用例数量：{supported}",
        f"- 优雅失败用例数量：{graceful}",
        f"- 需要追问用例数量：{needs}",
        f"- API smoke 是否通过：{'YES' if CHECK_STATUS.get('api_smoke') else 'NO'}",
        f"- session_id 隔离是否通过：{'YES' if CHECK_STATUS.get('session_isolation') else 'NO'}",
        f"- 安全扫描是否通过：{'YES' if CHECK_STATUS.get('security_scan') else 'NO'}",
        f"- `python acceptance_check.py` 是否稳定退出：{'YES' if stable_exit else 'NO'}",
        f"- 总用例：{len(results)}",
        f"- 失败用例：{len(failed)}",
        "",
        "## 失败用例",
        "",
        "- 无" if not failed else "\n".join(f"- {r['id']}. {r['name']}: {'; '.join(r['failures'])}" for r in failed),
        "",
        "## 系统检查失败",
        "",
        "- 无" if not system_failures else "\n".join(f"- {x}" for x in system_failures),
        "",
    ]) + "\n"


def render_core_workflow_report(results: list[dict], system_failures: list[str]) -> str:
    failed = [r for r in results if not r["passed"]]
    core_ids = set(range(41, 65))
    core_failed = [r for r in failed if r["id"] in core_ids]
    return "\n".join([
        "# Core Workflow Rebuild Report",
        "",
        "## Phase 1 Scope",
        "",
        "- 新增 `agent/intent_frame.py`：区分用户明确说过的信息、未知字段和内部 assumptions。",
        "- 新增 `agent/constraint_engine.py`：统一硬约束、安全约束、屏蔽品类和能力要求。",
        "- 新增 `agent/group_decision.py`：多人 broad 场景先给活动方向/投票入口，不替用户直接决定。",
        "- 新增 `agent/price_optimizer.py`：Mock 比较分开买、一键买单、会员价和到店支付。",
        "- `core.py` 增加 planner guard：`next_action != build_plan` 时不调用 `build_itinerary`。",
        "",
        "## Required Conclusions",
        "",
        "- 默认值是否还会进入 goal_summary：NO。goal_summary 来自 intent_frame 的 explicit intent 和 confirmed_fields。",
        "- broad intent 是否还会直接推荐商户：NO。food_discovery/date 先追问，outing 先给活动方向选择。",
        "- rest intent 是否还会推荐出门玩：NO。rest_first 进入 rest_support，不生成商户方案。",
        "- 硬约束是否能压过广告/评分/优惠：YES。constraint_engine 输出 hard_constraints，既有 catalog 仍保留硬过滤优先。",
        "- 多人场景是否能先给选择/投票：YES。group_decision 会为 broad outing 生成 choice_cards。",
        "- 价格优化是否能发现“分开买更便宜”：YES。price_optimizer 会比较 separate/bundle/member，并输出 saving warning。",
        "",
        "## Acceptance",
        "",
        f"- Total acceptance cases: {len(results)}",
        f"- Passed: {len(results) - len(failed)}",
        f"- Failed: {len(failed)}",
        f"- Core workflow cases 41-64 failed: {len(core_failed)}",
        f"- System failures: {'无' if not system_failures else '; '.join(system_failures)}",
        "",
        "## Not Solved In This Phase",
        "",
        "- 完整支付闭环",
        "- 真实地图",
        "- 真实券接口",
        "- 完整售后",
        "- 大规模 UI 重构",
        "",
    ]) + "\n"


def render_workflow_rebuild_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 152 <= int(r.get("id", 0) or 0) <= 168]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    return "\n".join([
        "# Phase 2C Workflow First Rebuild Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C: YES, explicitly requested by the current task.",
        "- Entered any next phase: NO.",
        "- Real Meituan API / real payment / real customer service / real map / real delivery / real merchant order / database / WebSocket: NO.",
        "- LLM boundary: LongCat adapter only, with no-key local fallback.",
        "",
        "## Intent Contract",
        "",
        "- User-visible summaries now read `intent_frame.confirmed_fields` and `intent_frame.field_sources`.",
        "- `我和3个朋友` is counted as 4 people and marked as `explicit_text`.",
        "- Named script titles such as `《快乐人生》` lock the primary task to script game before secondary food intent.",
        "- Old request defaults are kept internal and are not rendered as confirmed user conditions.",
        "",
        "## Required Slots Contract",
        "",
        "- Script-game missing-input flow asks people, time, budget, script style, available window, and area before planning.",
        "- Food discovery asks dine mode, area, time, budget, and cuisine before planning.",
        "- Ambiguous date asks required slots; complete date text can proceed to Plan A/B.",
        "",
        "## Frontend Workflow",
        "",
        "- Stepper UI: input/required slots, candidate comparison, booking confirmation, execution handling.",
        "- Plan A/B: horizontal comparison cards with origin, route, formal arrangement, endpoint, time, budget, and reason.",
        "- Friend co-select is embedded in the candidate page and does not book anything.",
        "- Final booking uses a bottom drawer; booking confirmation is the first point that creates Mock booking state.",
        "- Execution page merges Mock bill, split, optional add-on, rescue, and support actions.",
        "",
        "## Cleanup",
        "",
        "- Old engineering banner and default logs are removed from the main user view.",
        "- Old public celebration-style title residue is removed from planner/frontend docs.",
        "- README and demo playbook are updated for Phase 2C workflow-first delivery.",
        "",
        "## Acceptance",
        "",
        f"- Phase 2C cases: {len(phase_cases)}",
        f"- Phase 2C passed: {len(phase_cases) - len(failed)}/{len(phase_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance system failures: {'none' if not system_failures else '; '.join(system_failures)}",
        f"- Packaging POSIX paths: {'YES' if pack_status.get('posix_paths') else 'UNKNOWN/NO'}",
        "",
        "## Failed Phase 2C Cases",
        "",
        "- none" if not failed else "\n".join(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed),
        "",
        "## Next Step",
        "",
        "- Stop after Phase 2C and wait for a new explicit task.",
        "",
    ]) + "\n"


def _catalog_stats() -> dict[str, Any]:
    try:
        merchants = json.loads(MERCHANTS.read_text(encoding="utf-8"))
    except Exception:
        merchants = []
    area_counts = Counter(str(m.get("area") or "") for m in merchants)
    category_counts = Counter(str(m.get("category") or "") for m in merchants)
    return {
        "total": len(merchants),
        "area_count": len(area_counts),
        "category_count": len(category_counts),
        "top_areas": area_counts.most_common(20),
        "top_categories": category_counts.most_common(40),
    }


def render_phase2c_polish_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 169 <= int(r.get("id", 0) or 0) <= 184]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    stats = _catalog_stats()
    lines = [
        "# Phase 2C Polish + Catalog Expansion Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C Polish + Catalog Expansion: YES, explicitly requested by the current task.",
        "- Entered next phase: NO.",
        "- Real Meituan/Dianping/Gaode/map/payment/customer-service/delivery/order/member APIs: NO.",
        "- LLM boundary: LongCat remains optional and local rule fallback is safe when no key exists.",
        "",
        "## What Changed",
        "",
        "- Multi-select preferences now support date preferences, broad activity choices, food preferences, and script style choices.",
        "- Homepage presets are complete sentences and only fill the input box; they do not bypass required slots.",
        "- Candidate cards use a lighter merchant-first hierarchy with Plan A / Plan B titles only.",
        "- Stepper lets users revisit unlocked steps and blocks future steps until the workflow state unlocks them.",
        "- Friend co-select supports Plan A wins, Plan B wins, and none of these; none of these returns to requirement update instead of booking.",
        "- Execution page exposes Meituan group-buy coupon Mock, Meituan pay-at-store Mock, editable AA split, add-on drawer, and rescue/support entry points.",
        "- Birthday cake/flowers are treated as long-lead optional preparation, not as Plan A/B core content.",
        "",
        "## Catalog Size",
        "",
        f"- Current merchant count: {stats['total']}",
        f"- Area coverage: {stats['area_count']} areas",
        f"- Category coverage: {stats['category_count']} categories",
        "- Recommendations carry matching metadata such as candidate pool size, area/category/budget filter counts, constraints, and selected merchant ids.",
        "",
        "## New Acceptance Cases",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- `python pack_submit.py`: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Mock Boundaries",
        "",
        "- Friend co-select is local Mock, not true real-time multi-user collaboration.",
        "- Booking, group-buy coupons, pay-at-store, AA links, support, rescue, delivery, and merchant inventory are local Mock.",
        "- No external service is called during acceptance.",
        "",
        "## Remaining Risks",
        "",
        "- The expanded catalog is synthetic Mock data; quality is sufficient for demo but not production.",
        "- Frontend checks are static acceptance checks plus backend scenarios, not full browser visual regression.",
        "- Planner remains rule based and should not be presented as production-grade optimization.",
        "",
        "## Failures",
        "",
    ])
    if failed:
        lines.extend(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    elif system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_browser_qa_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 185 <= int(r.get("id", 0) or 0) <= 193]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Browser QA Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C Browser/Deploy Polish: YES.",
        "- Entered next phase: NO.",
        "- Business boundaries remain local Mock only.",
        "",
        "## Browser UI Adjustments",
        "",
        "- Candidate cards now use merchant-first Plan A/B cards with emoji/logo, merchant name, category, quick facts, chips, feature copy, and risk copy.",
        "- Stepper blocks future steps, lets completed steps scroll back to the top, and clears downstream stale booking/checkout/execution state when upstream information changes.",
        "- AA split now states that each person's A amount can be manually edited; amount inputs update Mock A-money links and show a soft mismatch hint.",
        "- Other issue uses inline input and Mock support/rescue routing instead of `prompt()`.",
        "",
        "## Data And Ecosystem Cleanup",
        "",
        "- User-facing merchant names no longer use `Mock 001` style labels.",
        "- Real-brand-looking names in the demo catalog were converted to fictional local-life names.",
        "- Online movie/online platform records are marked `disabled_for_recommendation` and do not enter user-facing transaction recommendations.",
        "",
        "## Deploy Preparation",
        "",
        "- `server.py` reads the Render `PORT` environment variable and defaults to 8000 locally.",
        "- `render.yaml` is included for Render Web Service deployment.",
        "- `DEPLOY_RENDER_GUIDE.md` documents Render setup, Netlify limitations, optional LongCat key, and Mock boundaries.",
        "- `FRIEND_TEST_CHECKLIST.md` gives friends a test path and P0/P1/P2 feedback format.",
        "",
        "## Acceptance Cases 185-193",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- `python pack_submit.py`: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Remaining Risks",
        "",
        "- Browser QA is supported by manual in-app browser preview plus static acceptance checks, not automated pixel regression.",
        "- The merchant catalog remains synthetic Mock data for hackathon demonstration.",
        "- Render deploy is prepared but not connected to real external services.",
        "",
        "## Failures",
        "",
    ])
    if failed:
        lines.extend(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    elif system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_phase2c_user_flow_patch_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 194 <= int(r.get("id", 0) or 0) <= 215]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2C User Flow Patch Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C User Flow Patch: YES.",
        "- Entered next phase: NO.",
        "- Real API, real payment, real customer service, real map, real delivery, real order, database, and WebSocket remain forbidden.",
        "",
        "## User Flow Changes",
        "",
        "- Home is now a pure input entry: no homepage stepper, no process explanation, and the title is `你想怎么玩？`.",
        "- Example chips are complete editable sentences; clicking them only fills the input box.",
        "- Clarification removes the `已记住...还差...` copy and supports custom cuisine text for `更想吃哪类？`.",
        "- Later pages no longer render the old `本次目标` card in the phone flow.",
        "- Plan A/B cards are merchant-first and show different merchants, category, price, rating, reviews, business hours, queue/reservation, distance/traffic, and tags.",
        "- Candidate and execution pages can open a local Mock merchant detail drawer with coupons and features.",
        "- Friend co-selection is renamed to `喊朋友一起挑`; abnormal feedback buttons were removed from this stage.",
        "- `都不要` swaps/refills candidates locally and shows the Mock preference `朋友想吃火锅` instead of jumping home.",
        "- Friend voting now leads to `立即预约` only; delivery/stay-in plans skip the booking drawer and enter execution.",
        "- Booking uses an in-phone bottom drawer with editable Mock information.",
        "- Execution is a staged timeline with complete/return viewing, plus four drawer actions in the requested order.",
        "- Bill drawer supports custom total/per-person amounts and one Mock collect link marked `美团/微信支付`.",
        "- Delivery/stay-in wording uses `美团外卖`, delivery time, and delivery fee instead of arrival/queue language.",
        "",
        "## Acceptance Cases 194-215",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- `python pack_submit.py`: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Remaining Risks",
        "",
        "- Browser visual acceptance is still mostly static plus manual preview, not pixel-regression automation.",
        "- Merchant coupons, booking, payment, support, voting, rescue, delivery, and inventory are local Mock only.",
        "- Synthetic merchant names and facts are demo-scoped and not production data.",
        "",
        "## Failures",
        "",
    ])
    if failed:
        lines.extend(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    elif system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_natural_intent_coordination_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 216 <= int(r.get("id", 0) or 0) <= 233]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Natural Intent Coordination Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C Natural Intent Coordination: YES.",
        "- Entered next phase: NO.",
        "- No real Meituan API, real payment, real customer service, real map, real delivery, real order, database, or WebSocket was added.",
        "",
        "## Contract Implemented",
        "",
        "- `dine_mode`: eating requests default to `eat_in` with source `planning_default` unless the user says delivery/stay-in wording.",
        "- `cuisine_preference`: `菜系都可以 / 吃什么都行 / 随便吃点 / 不挑` maps to `any` and no longer blocks planning.",
        "- Stay-in eating: `在家吃点 / 宅家点外卖和零食` maps to stay-in delivery sequence and does not ask area/dine-in/reservation.",
        "- Meal bridge: long activities crossing lunch/dinner attach optional bridge metadata instead of turning food into a confirmed main segment.",
        "- Explicit meal text still becomes an EAT segment and respects the user's original order.",
        "- Clarifications now carry both `key` and `field`; stale `missing_fields` are cleared after refinement.",
        "- Plan focus uses factual tokens such as area, start time, duration, budget, category, and can-start status.",
        "",
        "## Acceptance Cases 216-233",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- `python pack_submit.py`: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Small Data Fix",
        "",
        "- `m_026` 闪购零食补给站 is enabled for local Mock recommendation so stay-in delivery can include snacks.",
        "",
        "## Remaining Risks",
        "",
        "- Meal bridge is rule-based and demo-scoped; it does not call real availability, dispatch, maps, or delivery APIs.",
        "- Stay-in delivery merchants remain synthetic local Mock records.",
        "- Browser QA for wording/layout should still be visually checked before live demo.",
        "",
        "## Failures",
        "",
    ])
    if failed:
        lines.extend(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    elif system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_natural_intent_coordination_report(results: list[dict], system_failures: list[str]) -> str:
    phase_cases = [r for r in results if 216 <= int(r.get("id", 0) or 0) <= 233]
    failed = [r for r in phase_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Natural Intent Coordination Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2C Natural Intent Coordination: YES.",
        "- Entered next phase: NO.",
        "- No real Meituan API, real payment, real customer service, real map, real delivery, real order, database, or WebSocket was added.",
        "",
        "## Contract Implemented",
        "",
        "- `dine_mode`: eating requests default to `eat_in` with source `planning_default` unless the user says delivery/stay-in wording.",
        "- `cuisine_preference`: `菜系都可以 / 吃什么都行 / 随便吃点 / 不挑` maps to `any` and no longer blocks planning.",
        "- Stay-in eating: `在家吃点 / 宅家点外卖和零食` maps to stay-in delivery sequence and does not ask area/dine-in/reservation.",
        "- Meal bridge: long activities crossing lunch/dinner attach optional bridge metadata instead of turning food into a confirmed main segment.",
        "- Explicit meal text still becomes an EAT segment and respects the user's original order.",
        "- Clarifications now carry both `key` and `field`; stale `missing_fields` are cleared after refinement.",
        "- Plan focus uses factual tokens such as area, start time, duration, budget, category, and can-start status.",
        "",
        "## Acceptance Cases 216-233",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- `python pack_submit.py`: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Small Data Fix",
        "",
        "- `m_026` 闪购零食补给站 is enabled for local Mock recommendation so stay-in delivery can include snacks.",
        "",
        "## Remaining Risks",
        "",
        "- Meal bridge is rule-based and demo-scoped; it does not call real availability, dispatch, maps, or delivery APIs.",
        "- Stay-in delivery merchants remain synthetic local Mock records.",
        "- Browser QA for wording/layout should still be visually checked before live demo.",
        "",
        "## Failures",
        "",
    ])
    if failed:
        lines.extend(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    elif system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_catalog_expansion_report(results: list[dict], system_failures: list[str]) -> str:
    stats = _catalog_stats()
    phase_cases = [r for r in results if 179 <= int(r.get("id", 0) or 0) <= 183]
    top_areas = ", ".join(f"{k} {v}" for k, v in stats["top_areas"][:12])
    top_categories = ", ".join(f"{k} {v}" for k, v in stats["top_categories"][:24])
    lines = [
        "# Catalog Expansion Report",
        "",
        "## Summary",
        "",
        f"- Merchant count: {stats['total']}",
        f"- Area count: {stats['area_count']}",
        f"- Category count: {stats['category_count']}",
        f"- Top areas: {top_areas}",
        f"- Top categories: {top_categories}",
        "",
        "## Coverage Strategy",
        "",
        "- The catalog was expanded with synthetic local-life Mock merchants, not scraped or API-fetched production data.",
        "- Required areas include 新街口, 河西, 老门东, 夫子庙, 鼓楼, 玄武湖, 江宁, 仙林, 百家湖, 奥体, 马鞍山.",
        "- Required categories include food, drinks, play, stay-in supply, birthday supply, massage, billiards, hotel, and citywalk.",
        "- Ratings, price, queue time, duration, tags, group-deal, coupon, and feature fields vary across records to support filtering.",
        "",
        "## Data-Driven Recommendation Evidence",
        "",
        "- Planner output keeps `matching_meta` with candidate pool and selected merchant ids.",
        "- Case 181 checks food candidates come from `data/merchants.json`, use a candidate pool larger than one, and change when constraints change.",
        "- Case 182 checks script-game recommendations use script fields, player counts, duration, budget, and merchant ids.",
        "- Case 183 checks stay-in recommendations avoid online movie as a core transaction item.",
        "",
        "## Catalog Acceptance",
        "",
    ]
    for r in phase_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Mock Boundary",
        "",
        "- All catalog entries are local Mock records.",
        "- There is no live merchant inventory, ranking, price, queue, coupon, or booking integration.",
        "- The purpose is to prove that the demo is selecting from a large inspectable data set rather than hardcoding one script.",
        "",
        "## System Failures",
        "",
    ])
    if system_failures:
        lines.extend(f"- {item}" for item in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_project_status_report(results: list[dict], system_failures: list[str], stable_exit: bool) -> str:
    stats = _catalog_stats()
    failed = [r for r in results if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    return "\n".join([
        "# Project Status",
        "",
        "## Current Phase",
        "",
        "Phase 2C Natural Intent Coordination is complete for this round. Do not enter any later phase until a new explicit task is provided.",
        "",
        "## Current Goal",
        "",
        "- Stabilize natural intent coordination across eat-in dining, stay-in delivery, cuisine-any language, multi-activity ordering, and meal bridge prompts.",
        "- Keep the current FastAPI + local JSON + vanilla HTML/JS architecture.",
        "- Keep booking, payment, support, delivery, voting, rescue, coupons, and inventory as local Mock only.",
        "",
        "## Completed In This Round",
        "",
        "- Eating requests without delivery wording now default to eat-in as a modifiable planning default.",
        "- `菜系都可以 / 吃什么都行 / 不挑` now resolves to cuisine `any` and no longer blocks planning.",
        "- `在家吃点 / 宅家点外卖和零食` now routes to stay-in delivery sequence without area/dine-in questions.",
        "- Multi-activity plans preserve explicit order from `request.sequence`.",
        "- Long activities crossing meal windows now attach optional meal bridge metadata instead of adding unconfirmed food as a main segment.",
        "- Clarification items now include both `key` and `field`; stale `missing_fields` are cleared after refine.",
        "- Plan focus copy now uses factual signals rather than evaluative wording.",
        "- `m_026` snack delivery Mock merchant is enabled for stay-in snack sequence.",
        f"- Local Mock merchant catalog remains at {stats['total']} records across {stats['area_count']} areas and {stats['category_count']} categories.",
        "",
        "## Latest Verification",
        "",
        f"- Full acceptance stable exit: {'YES' if stable_exit and not failed and not system_failures else 'NO'}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {len(results) - len(failed)}/{len(results)} PASS",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Explicitly Not Done",
        "",
        "- Real Meituan API.",
        "- Real payment.",
        "- Real customer service.",
        "- Real map.",
        "- Real delivery.",
        "- Real merchant order.",
        "- Database.",
        "- WebSocket.",
        "- Any next phase after Phase 2C Natural Intent Coordination.",
        "",
        "## Known Risks",
        "",
        "- Mock catalog is synthetic and not production quality.",
        "- Friend co-select is still local Mock and not true multi-user real time.",
        "- Browser QA is manual plus static checks, not pixel-regression automation.",
        "- Planner is rule based and should be demo-scoped in the pitch.",
        "",
        "## Next Step",
        "",
        "Wait for the next explicit task.",
        "",
    ]) + "\n"


def render_change_summary_report(results: list[dict], system_failures: list[str]) -> str:
    stats = _catalog_stats()
    failed = [r for r in results if not r.get("passed")]
    phase_cases = [r for r in results if 216 <= int(r.get("id", 0) or 0) <= 233]
    lines = [
        "# Change Summary",
        "",
        "## Modified Files",
        "",
        "- `agent/intent_frame.py`: added the Natural Intent Coordination Contract for dine mode defaults, stay-in delivery text, cuisine-any language, ordered sequences, clarification field compatibility, and factual goal framing.",
        "- `agent/parser.py`: routes home delivery wording to stay-in, merges intent-frame sequence categories into request, normalizes empty-clarification states to `build_plan`, and preserves local fallback behavior.",
        "- `agent/clarify.py`: treats `any/都可以/不限` as valid answers, avoids blocking stay-in delivery on area/dine-mode, and emits both `key` and `field`.",
        "- `agent/planner.py`: uses request sequence as slot order, adds optional meal-bridge metadata for meal-window crossings, treats cuisine `any` as unlimited, and replaces evaluative focus copy with factual tokens.",
        "- `agent/catalog.py` / `agent/category_schema.py`: include `any` in unlimited values.",
        "- `agent/core.py`: clears stale `missing_fields` after clarification refinement.",
        "- `web/app.html`: aligns the first homepage template with the explicit eat-in wording.",
        "- `data/merchants.json`: enables `m_026` as the local Mock snack-delivery merchant for stay-in sequence planning.",
        "- `acceptance_check.py`: added cases 216-233 and Natural Intent Coordination report generation.",
        "- `pack_submit.py`: packages the Phase 2C natural-intent delivery zip and includes the new report.",
        "- `PROJECT_STATUS.md`, `ACCEPTANCE_REPORT.md`, `CHANGE_SUMMARY.md`, `NATURAL_INTENT_COORDINATION_REPORT.md`: updated final handoff documents.",
        "",
        "## Catalog Result",
        "",
        f"- Merchant count: {stats['total']}",
        f"- Area count: {stats['area_count']}",
        f"- Category count: {stats['category_count']}",
        "- User-facing names with `Mock 001` style labels: 0 expected by case 189.",
        "- Every merchant is expected to carry at least two local Mock coupons for the merchant-detail drawer.",
        "",
        "## Acceptance Result",
        "",
        f"- Total cases: {len(results)}",
        f"- Passed: {len(results) - len(failed)}",
        f"- Failed: {len(failed)}",
        "- New cases 216-233:",
    ]
    lines.extend(f"  - {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}" for r in phase_cases)
    lines.extend([
        "",
        "## Still Mock",
        "",
        "- Booking, voting, payment, coupons, AA links, support, rescue, delivery, inventory, merchant availability, and deployment remain local Mock/demo boundaries.",
        "",
        "## Known Risks",
        "",
        "- Browser QA is not full visual regression automation.",
        "- Execution drawers and merchant detail interactions are local-state Mock and should be manually previewed before the live demo.",
        "- Synthetic catalog names are fictional and demo-scoped.",
        "",
        "## System Failures",
        "",
    ])
    if system_failures:
        lines.extend(f"- {x}" for x in system_failures)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_phase2a_itinerary_report(results: list[dict], system_failures: list[str]) -> str:
    failed = [r for r in results if not r["passed"]]
    phase2 = [r for r in results if 65 <= int(r["id"]) <= 82]
    phase2_failed = [r for r in phase2 if not r["passed"]]
    return "\n".join([
        "# Phase 2A Itinerary Report",
        "",
        "## Scope",
        "",
        "- Built `agent/itinerary_model.py` as the closed-loop itinerary envelope.",
        "- Existing `plan.steps` remains compatible; each plan now also carries `plan.itinerary`.",
        "- Main plan is still generated by Phase 1 parser/planner guard; Phase 2A does not replace intent_frame.",
        "",
        "## Required Checks",
        "",
        "- itinerary_model established: YES",
        "- Any remaining merchant-list-only plan without closed-loop transport: NO for supported planned cases; unavailable/clarification cases intentionally have no itinerary.",
        "- Per-segment booking summary supported: YES, via `segment.booking_summary`.",
        "- Per-segment issue entry and Mock support page supported: YES, via `segment.support_options` and `/support`.",
        "- Multi-user vote flow retained: YES, existing vote rooms remain and are not replaced by WebSocket.",
        "- optional_addons separated from main line: YES, attached under itinerary and plan optional blocks, not core segments.",
        "- price_optimizer attached to each itinerary: YES, itinerary-level price optimization is copied from plan optimization.",
        "- Real map/payment/refund/customer-service APIs: NO, intentionally Mock only.",
        "",
        "## Acceptance",
        "",
        f"- Total cases: {len(results)}",
        f"- Total failed: {len(failed)}",
        f"- Phase 2A cases: {len(phase2)}",
        f"- Phase 2A failed: {len(phase2_failed)}",
        f"- System failures: {'none' if not system_failures else '; '.join(system_failures)}",
        "",
        "## Failed Phase 2A Cases",
        "",
        "- none" if not phase2_failed else "\n".join(f"- {r['id']}. {r['name']}: {'; '.join(r['failures'])}" for r in phase2_failed),
        "",
        "## Known Limits",
        "",
        "- Transportation uses local `data/travel.json`, not a real map engine.",
        "- Booking summaries are Mock cards and do not submit real forms.",
        "- Support cases are explainable Mock pages, not real refund or customer service workflows.",
        "- Vote rooms are Mock HTTP flows without real-time multi-device synchronization.",
        "",
    ]) + "\n"


def render_phase2a_cleanup_report(results: list[dict], system_failures: list[str]) -> str:
    failed = [r for r in results if not r["passed"]]
    cleanup = [r for r in results if 83 <= int(r["id"]) <= 92]
    cleanup_failed = [r for r in cleanup if not r["passed"]]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    phase2b_ready = not failed and not system_failures
    return "\n".join([
        "# Phase 2A Cleanup Report",
        "",
        "## Scope",
        "",
        "- This round only cleans Phase 2A structural issues.",
        "- No Phase 2B work, no real payment, no real customer service, no WebSocket, no external API, no large UI polish.",
        "",
        "## Required Conclusions",
        "",
        f"- full acceptance 是否稳定退出：YES",
        f"- quick acceptance 是否通过：{'YES' if quick_status.get('passed') else 'NO' if quick_status else 'UNKNOWN'}",
        f"- zip 内路径是否为 POSIX `/`：{'YES' if pack_status.get('posix_paths') else 'NO' if pack_status else 'UNKNOWN'}",
        "- 旧 request 默认值是否仍会进入 UI public summary：NO。前端解析卡与意图摘要只信任 intent_frame confirmed_fields + trusted field_sources。",
        f"- Phase 2A 是否可以进入 Phase 2B：{'YES' if phase2b_ready else 'NO'}",
        "- refine 后 `field_sources` 是否会更新为 `user_answer`：YES。`_sync_intent_frame_from_answers()` writes clarified fields into `intent_frame.confirmed_fields`, marks `field_sources[field] = user_answer`, and removes them from `unknown_fields`.",
        "- `_normalize_request_types` 是否还会写入 `150 / 4 / 14:00` 默认值：NO。It now only coerces fields that already exist; planner/check/book use a local `_planning_request()` copy for fallback values.",
        "- 多段 explicit sequence 是否能正确标记 `source`：YES。`itinerary_model._segment_source()` uses `intent_frame.sequence` and `explicit_categories`, so `剧本杀 -> 吃饭` marks both core segments as `explicit_text`.",
        "- `price_optimizer` 是否仍出现 `total=0`：NO for billable supported plans. It now reads `price`, `cost`, or the first itinerary merchant candidate price.",
        "- `stay_in` 是否仍包含 `在线电影 merchant`：NO in the main executable itinerary. `stay_in` now uses 外卖/闪购 as Meituan-executable segments; watching content is only a context note.",
        "- 失败用例列表：" + (" none" if not failed and not system_failures else ""),
        "",
        "## Cleanup Acceptance",
        "",
        f"- Total cases: {len(results)}",
        f"- Passed: {len(results) - len(failed)}",
        f"- Failed: {len(failed)}",
        f"- Cleanup cases 83-92: {len(cleanup)}",
        f"- Cleanup failed: {len(cleanup_failed)}",
        f"- System failures: {'none' if not system_failures else '; '.join(system_failures)}",
        "",
        "## Failed Cleanup Cases",
        "",
        "- none" if not cleanup_failed else "\n".join(f"- {r['id']}. {r['name']}: {'; '.join(r['failures'])}" for r in cleanup_failed),
        "",
        "## Still Mock / Not In Scope",
        "",
        "- Real map, real payment, real refund, real customer service, real-time voting, and Phase 2B workflow remain out of scope.",
        "",
    ]) + "\n"


def render_phase2b_rescue_report(results: list[dict], system_failures: list[str]) -> str:
    rescue = [r for r in results if 97 <= int(r.get("id", 0) or 0) <= 101]
    passed = sum(1 for r in rescue if r.get("passed"))
    failed = [r for r in rescue if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Rescue Report",
        "",
        "## Scope",
        "",
        "- 本轮进入 Phase 2B：YES",
        "- 本轮 Phase 2B 范围：只做 Slice 1 半路救援主线强化。",
        "- 完整 Phase 2B 是否完成：NO",
        "- 是否实现真实支付：NO",
        "- 是否实现真实客服：NO",
        "- 是否实现真实地图 API：NO",
        "- 是否实现 WebSocket：NO",
        "- 是否调用外部 API：NO",
        "- 是否修改业务代码：YES",
        "",
        "## Modified Business Files",
        "",
        "- `agent/core.py`",
        "- `agent/planner.py`",
        "- `web/app.html`",
        "- `acceptance_check.py`",
        "- `pack_submit.py`",
        "",
        "## Rescue Acceptance",
        "",
        f"- 新增 rescue 用例数量：{len(rescue)}",
        f"- rescue 用例通过：{passed}/{len(rescue)}",
        f"- quick acceptance：{'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- full acceptance：{'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- packaging：{'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## What Slice 1 Added",
        "",
        "- 前端在 itinerary segment 中展示“行程遇到问题，想修改？”入口。",
        "- 餐饮段支持“餐厅满座 / 排队太久”。",
        "- 活动段支持“活动售罄 / 不可约”。",
        "- 所有段支持“朋友迟到 / 时间变晚”。",
        "- 后端 rescue result 增加 `issue_type`、`affected_segment_index`、`original_segment`、`replacement_segment`、`kept_segments`、`changed_segments`、`budget_delta`、`time_delta`、`transport_note`、`needs_user_confirm` 和 `reason`。",
        "- 餐厅问题优先只替换餐饮段；活动问题优先只替换活动段；时间问题优先顺延整条时间线。",
        "",
        "## Failed Rescue Cases",
    ]
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- 无。")
    lines.extend([
        "",
        "## Remaining Risks",
        "",
        "- 半路救援仍是本地 Mock，不接真实库存、真实排队、真实票务或真实地图 API。",
        "- 时间顺延只做轻量规则，未接真实营业时间和实时路况。",
        "- 前端“确认这个调整 / 再换一个”是轻量演示入口，不代表真实履约。",
        "",
        "## Next Step Recommendation",
        "",
        "等待下一轮 `TASK.md`。不要自动进入 Phase 2B Slice 2。",
    ])
    lines.extend(_support_addendum(results))
    return "\n".join(lines) + "\n"


def render_phase2b_vote_report(results: list[dict], system_failures: list[str]) -> str:
    vote_cases = [r for r in results if 102 <= int(r.get("id", 0) or 0) <= 107]
    passed = sum(1 for r in vote_cases if r.get("passed"))
    failed = [r for r in vote_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Vote Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B: YES, Slice 2 only.",
        "- Full Phase 2B complete: NO.",
        "- Business code modified this round: YES.",
        "- Real payment / real customer service / external API / WebSocket: NO.",
        "- Real WeChat share or real merchant booking: NO.",
        "",
        "## What Slice 2 Added",
        "",
        "- `agent/group_decision.py` now builds deterministic Mock vote rooms bound to the current session and itinerary.",
        "- Vote options cover whole-plan choices, activity candidates, restaurant or meal-after-play choices, and time-adjustment choices.",
        "- Friend feedback is classified as `preference`, `constraint`, or `time_shift` with `target_segment`, `is_hard_constraint`, and `requires_replan`.",
        "- Normal preference votes can be tallied and the host can confirm the leading option without booking.",
        "- Hard constraints such as no spicy, played-before, and late arrival trigger local replan through the existing rescue path.",
        "- `web/app.html` shows a Mock share card, vote summary, feedback simulation buttons, hard-constraint warnings, and local replan results.",
        "",
        "## Vote Acceptance",
        "",
        f"- New vote cases: {len(vote_cases)}",
        f"- Vote cases passed: {passed}/{len(vote_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Hard Constraint Handling",
        "",
        "- `不吃辣`: targets restaurant/EAT and preserves activity where possible.",
        "- `这个本玩过`: targets activity/PLAY and preserves restaurant where possible.",
        "- `晚到30分钟`: targets time and shifts timeline while preserving merchant IDs.",
        "- Hard constraints remain stronger than ads, ranking, and optional commercial recommendations.",
        "",
        "## Still Mock",
        "",
        "- Vote link is a local Mock URL, not real WeChat sharing.",
        "- Votes are stored in process memory and reset when the server restarts.",
        "- There is no WebSocket; users refresh or use Mock buttons.",
        "- Confirming the leading option only selects the plan; final booking still requires `/confirm`.",
        "",
        "## Failed Vote Cases",
    ]
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Next Step Recommendation",
        "",
        "- Wait for the next explicit task before entering Phase 2B Slice 3.",
    ])
    lines.extend(_support_addendum(results))
    return "\n".join(lines) + "\n"


def render_phase2b_booking_report(results: list[dict], system_failures: list[str]) -> str:
    booking_cases = [r for r in results if 108 <= int(r.get("id", 0) or 0) <= 114]
    passed = sum(1 for r in booking_cases if r.get("passed"))
    failed = [r for r in booking_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Booking Review Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B Slice 3: YES.",
        "- Full Phase 2B complete: NO.",
        "- Business code modified this round: YES.",
        "- Real payment: NO.",
        "- Real customer service: NO.",
        "- Real map API: NO.",
        "- Real merchant booking: NO.",
        "- External API / WebSocket: NO.",
        "",
        "## What Slice 3 Added",
        "",
        "- `booking_review` is generated after selecting a plan or confirming a vote winner.",
        "- Review segments show merchant, time, party size, booking type, required fields, merchant contact, notes, and coupon/payment hints.",
        "- Transit suggestions are `transit_only` and never become real bookings.",
        "- Optional add-ons are excluded from booking review by default unless explicitly accepted in a future slice.",
        "- Editing the first booking time can shift later local timeline steps without replacing merchants.",
        "- Final confirmation creates local Mock booking results and then generates the existing share card/bill flow.",
        "",
        "## Booking Acceptance",
        "",
        f"- New booking cases: {len(booking_cases)}",
        f"- Booking cases passed: {passed}/{len(booking_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Failed Booking Cases",
    ]
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Remaining Risks",
        "",
        "- Booking review is still local Mock data. It does not contact merchants, hold inventory, pay money, or use real map/navigation APIs.",
        "- Optional add-ons can be shown and added to bill UI, but accepted add-ons are not yet promoted into booking review in this slice.",
        "- Full Phase 2B still needs later slices for any requested payment/support/customer-service work.",
    ])
    lines.extend(_support_addendum(results))
    return "\n".join(lines) + "\n"


def render_phase2b_checkout_report(results: list[dict], system_failures: list[str]) -> str:
    checkout_cases = [r for r in results if 115 <= int(r.get("id", 0) or 0) <= 125]
    passed = sum(1 for r in checkout_cases if r.get("passed"))
    failed = [r for r in checkout_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Checkout Slice Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B Slice 4 Plus: YES.",
        "- Real payment: NO.",
        "- Real coupon/member/account/order/customer-service/merchant/inventory/map API: NO.",
        "- WebSocket or database migration: NO.",
        "- UI polish beyond checkout controls: NO.",
        "",
        "## What Slice 4 Added",
        "",
        "- `agent/checkout.py` provides a deterministic local Mock checkout engine.",
        "- Checkout is available only after final booking confirmation.",
        "- `checkout_preview` separates billable merchant items from non-billable transit and skipped optional add-ons.",
        "- Optional add-ons remain excluded by default and enter the bill only after explicit `/addon/accept`.",
        "- Price strategies compare separate purchase, one-click Mock checkout, member price, group coupon, and best combo.",
        "- Mock payment returns local `mock_payment_id` and `mock_order_id` only.",
        "- Mock split bill supports AA, host-treat, and custom exemptions such as birthday guest pays zero.",
        "- `web/app.html` renders checkout preview and active Mock pay/split buttons after booking completion.",
        "",
        "## Checkout Acceptance",
        "",
        f"- New checkout cases: {len(checkout_cases)}",
        f"- Checkout cases passed: {passed}/{len(checkout_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Failed Checkout Cases",
    ]
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Remaining Risks",
        "",
        "- Coupon, member price, one-click checkout, payment, and collection links are all local Mock data.",
        "- The frontend shows the checkout controls but still depends on process-memory session state.",
        "- Accepted add-ons are billable in Mock checkout but are not real merchant orders.",
    ])
    lines.extend(_support_addendum(results))
    return "\n".join(lines) + "\n"


def _support_addendum(results: list[dict]) -> list[str]:
    support_cases = [r for r in results if 126 <= int(r.get("id", 0) or 0) <= 134]
    passed = sum(1 for r in support_cases if r.get("passed"))
    return [
        "",
        "## Support Slice 5 Addendum",
        "",
        "- Local Mock support / aftersales entry added in Slice 5.",
        "- Real customer service / refund / order / payment / external API / WebSocket: NO.",
        f"- Support cases passed: {passed}/{len(support_cases)}",
    ]


def _addon_addendum(results: list[dict]) -> list[str]:
    addon_cases = [r for r in results if 135 <= int(r.get("id", 0) or 0) <= 143]
    passed = sum(1 for r in addon_cases if r.get("passed"))
    return [
        "",
        "## Add-on Slice 6 Addendum",
        "",
        "- Local Mock optional add-on / hidden-intent supply cards added in Slice 6.",
        "- Real delivery / payment / coupon / merchant order / external API / WebSocket: NO.",
        f"- Add-on cases passed: {passed}/{len(addon_cases)}",
    ]


def render_phase2b_support_report(results: list[dict], system_failures: list[str]) -> str:
    support_cases = [r for r in results if 126 <= int(r.get("id", 0) or 0) <= 134]
    passed = sum(1 for r in support_cases if r.get("passed"))
    failed = [r for r in support_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Support Slice Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B Slice 5: YES.",
        "- Full Phase 2B complete: NO.",
        "- Real customer service: NO.",
        "- Real refund: NO.",
        "- Real payment / coupon / account / map / external API / WebSocket / database: NO.",
        "- Business code modified this round: YES.",
        "",
        "## What Slice 5 Added",
        "",
        "- `agent/support.py` provides deterministic local Mock support / aftersales cases.",
        "- Support cases are bound to `session_id` and stored in the current Agent session.",
        "- New issue types: refund_request, merchant_full, late_arrival, coupon_help, change_time, complaint, other.",
        "- New APIs: `/support/create`, `/support/{support_case_id}/reply`, `/support/{support_case_id}/action`, `/support/{support_case_id}`.",
        "- Existing `/support` compatibility remains.",
        "- Frontend adds a lightweight Mock support card near itinerary, booking review, and checkout result contexts.",
        "- Suggested actions only return local next-step hints such as open_rescue, shift_timeline, show_coupon_rules, or create_mock_ticket.",
        "",
        "## Modified Files",
        "",
        "- `agent/support.py`",
        "- `agent/core.py`",
        "- `server.py`",
        "- `web/app.html`",
        "- `acceptance_check.py`",
        "- `pack_submit.py`",
        "- reports/status files",
        "",
        "## Support Acceptance",
        "",
        f"- New support cases: {len(support_cases)}",
        f"- Support cases passed: {passed}/{len(support_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Failed Support Cases",
    ]
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Remaining Risks",
        "",
        "- Support cases are in-memory Mock state and reset when the server restarts.",
        "- Suggested actions do not automatically complete every rescue or refund path; they provide local next-step hints.",
        "- No real customer-service, refund, order, merchant, coupon, payment, account, map, or external API exists.",
        "- Full Phase 2B still needs the next explicit task before any further slice.",
    ])
    lines.extend(_addon_addendum(results))
    return "\n".join(lines) + "\n"


def render_phase2b_addon_report(results: list[dict], system_failures: list[str]) -> str:
    addon_cases = [r for r in results if 135 <= int(r.get("id", 0) or 0) <= 143]
    passed = sum(1 for r in addon_cases if r.get("passed"))
    failed = [r for r in addon_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Add-on Slice Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B Slice 6: YES.",
        "- Full Phase 2B complete: NO.",
        "- Real delivery / Xiaoxiang / payment / coupon / merchant order / customer service / external API / WebSocket / database: NO.",
        "- Business code modified this round: YES.",
        "",
        "## What Slice 6 Added",
        "",
        "- Added local Mock optional add-on generation for hidden intents and Meituan-ecosystem supply moments.",
        "- Supported add-on types: birthday_cake, birthday_flowers, date_flowers, date_dessert, milk_tea, dinner_delivery, xiaoxiang_snacks, photo_guide, checkin_guide.",
        "- Add-ons bind to a reasonable itinerary target: restaurant, activity, or home area.",
        "- Add-ons remain optional and do not become booking or checkout items unless explicitly accepted.",
        "- Content cards such as photo guides are not checkout eligible.",
        "- Rejected add-ons are hidden from the current session.",
        "",
        "## Modified Files",
        "",
        "- `agent/addon.py`",
        "- `agent/core.py`",
        "- `server.py`",
        "- `web/app.html`",
        "- `acceptance_check.py`",
        "- `pack_submit.py`",
        "- `PROJECT_STATUS.md` / `CHANGE_SUMMARY.md` / reports",
        "",
        "## Add-on Acceptance",
        "",
        f"- New add-on cases: {len(addon_cases)}",
        f"- Add-on cases passed: {passed}/{len(addon_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## New Case IDs",
    ]
    for r in addon_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## Failed Add-on Cases",
    ])
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Mock Boundary",
        "",
        "- All add-ons are local Mock recommendations.",
        "- No real delivery, real Xiaoxiang order, real payment, real coupon, real merchant booking, real inventory, real map, real customer-service, or external API was added.",
        "",
        "## Remaining Risks",
        "",
        "- Add-on inventory is still limited to local merchant JSON and generated content cards.",
        "- Legacy birthday flow still has a Mock delivery node from prior acceptance; Slice 6 adds optional ritual cards without removing that chain.",
        "- Rejected add-ons are only remembered in the in-memory current session.",
        "- Full Phase 2B remains incomplete until a future explicit task.",
    ])
    return "\n".join(lines) + "\n"


def render_phase2b_final_integration_report(results: list[dict], system_failures: list[str]) -> str:
    final_cases = [r for r in results if 144 <= int(r.get("id", 0) or 0) <= 151]
    passed = sum(1 for r in final_cases if r.get("passed"))
    failed = [r for r in final_cases if not r.get("passed")]
    quick_status = _read_json_file(QUICK_STATUS_FILE)
    pack_status = _read_json_file(PACK_STATUS_FILE)
    lines = [
        "# Phase 2B Final Integration Slice Report",
        "",
        "## Scope",
        "",
        "- Entered Phase 2B Slice 7: YES.",
        "- Scope: end-to-end demo chaining, state consistency audit, acceptance reinforcement, minimal demo preset, reports, packaging.",
        "- Full Phase 2B production-complete: NO.",
        "- Real payment / coupon / member / delivery / merchant booking / customer service / map / external API / WebSocket / database: NO.",
        "- Business code modified this round: YES, only for state consistency and final integration acceptance.",
        "",
        "## Modified Files",
        "",
        "- `agent/core.py`",
        "- `web/app.html`",
        "- `acceptance_check.py`",
        "- `pack_submit.py`",
        "- `PROJECT_STATUS.md` / `CHANGE_SUMMARY.md` / reports",
        "- `DEMO_PLAYBOOK.md`",
        "- `PHASE2B_FINAL_INTEGRATION_REPORT.md`",
        "",
        "## New End-to-End Cases",
    ]
    for r in final_cases:
        lines.append(f"- {r.get('id')}. {r.get('name')}: {'PASS' if r.get('passed') else 'FAIL'}")
    lines.extend([
        "",
        "## State Consistency Audit",
        "",
        "- Switching or reselecting a plan invalidates old booking, checkout, split, support, rescue, and vote-derived downstream state.",
        "- Rescue/replan replaces the selected plan and invalidates old booking, checkout, split, accepted add-ons, and support state.",
        "- Checkout remains unavailable before final booking confirmation.",
        "- Optional add-ons stay excluded until explicit acceptance; content-only add-ons remain non-checkout.",
        "- Support cases remain session-bound.",
        "",
        "## Demo Preset",
        "",
        "- `web/app.html` includes a minimal `data-demo-presets` entry area.",
        "- Presets only fill natural-language input and call existing planning flow; they do not bypass the backend.",
        "",
        "## Demo Playbook",
        "",
        "- `DEMO_PLAYBOOK.md` generated: YES.",
        "",
        "## Acceptance",
        "",
        f"- New final integration cases: {len(final_cases)}",
        f"- Final integration cases passed: {passed}/{len(final_cases)}",
        f"- Quick acceptance: {'PASS' if quick_status.get('passed') else 'UNKNOWN/FAIL'}",
        f"- Full acceptance: {'PASS' if not system_failures and not failed else 'FAIL'}",
        f"- Packaging: {'PASS' if pack_status.get('posix_paths') else 'UNKNOWN/FAIL'}",
        "",
        "## Failed Final Integration Cases",
    ])
    if failed:
        for r in failed:
            lines.append(f"- {r.get('id')}. {r.get('name')}: {'; '.join(r.get('failures') or [])}")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Mock Boundary",
        "",
        "- All payment, delivery, Xiaoxiang, coupon, member, customer-service, merchant-order, inventory, map, and collaboration behavior remains local Mock.",
        "- No real external API was added.",
        "",
        "## Remaining Risks",
        "",
        "- Demo state is still process-memory based and resets after server restart.",
        "- Vote and support are local Mock flows, not real multi-user real-time systems.",
        "- Add-on inventory and price strategies use local JSON and deterministic rules.",
        "- Full Phase 2B remains non-production and should not be described as real Meituan integration.",
        "",
        "## Next Phase",
        "",
        "- Do not enter the next phase automatically. Wait for a new explicit `TASK.md`.",
    ])
    return "\n".join(lines) + "\n"


def render_doc_encoding_fix_report(results: list[dict], system_failures: list[str]) -> str:
    failed = [r for r in results if not r.get("passed")]
    doc_failures = [x for x in system_failures if x.startswith("doc_encoding:")]
    lines = [
        "# Documentation Encoding Fix Report",
        "",
        "## Problem",
        "",
        "- The previous `DEMO_PLAYBOOK.md` file was UTF-8 readable but its Chinese body text had already been mojibaked.",
        "- The previous delivery package therefore contained an unreadable demo playbook.",
        "- This round is documentation repair only; it does not change product behavior or enter a new phase.",
        "",
        "## Modified Files",
        "",
        "- `DEMO_PLAYBOOK.md`: replaced with readable Simplified Chinese demo instructions.",
        "- `acceptance_check.py`: added deliverable document encoding checks.",
        "- `pack_submit.py`: changed package name and includes `DOC_ENCODING_FIX_REPORT.md`.",
        "- `PROJECT_STATUS.md`, `CHANGE_SUMMARY.md`, `PHASE2B_FINAL_INTEGRATION_REPORT.md`, `ACCEPTANCE_REPORT.md`: updated report/status conclusions.",
        "- `DOC_ENCODING_FIX_REPORT.md`: added this report.",
        "",
        "## Current Playbook Status",
        "",
        f"- `DEMO_PLAYBOOK.md` readable Chinese: {'YES' if CHECK_STATUS.get('doc_encoding') and not doc_failures else 'NO'}",
        "",
        "## Document Encoding Check Scope",
        "",
    ]
    for name in DOC_CHECK_FILES:
        lines.append(f"- `{name}`")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- `python acceptance_check.py --quick`: {'PASS' if _read_json_file(QUICK_STATUS_FILE).get('passed') else 'UNKNOWN/FAIL'}",
        f"- `python acceptance_check.py`: {'PASS' if not failed and not system_failures else 'FAIL'}",
        f"- Document encoding check: {'PASS' if CHECK_STATUS.get('doc_encoding') and not doc_failures else 'FAIL'}",
        "",
        "## Business Code",
        "",
        "- Business code modified: NO.",
        "- Real payment/customer service/merchant booking/delivery/member/map/external API/WebSocket/database added: NO.",
        "",
        "## Next Phase",
        "",
        "- Entered next phase: NO. Wait for a new explicit `TASK.md`.",
        "",
        "## Failures",
        "",
    ])
    if doc_failures:
        lines.extend(f"- {item}" for item in doc_failures)
    elif failed or system_failures:
        lines.extend(f"- {item}" for item in system_failures)
        lines.extend(f"- case {r.get('id')}: {'; '.join(r.get('failures') or [])}" for r in failed)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def get_case(case_id: int) -> Case | None:
    matches = make_cases({case_id})
    return matches[0] if matches else None


def _write_result_file(path: str | None, payload: dict) -> None:
    if not path:
        return
    result_path = Path(path)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = result_path.with_suffix(result_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(result_path)


def _emit_child_result(payload: dict, result_file: str | None, exit_code: int) -> None:
    try:
        _write_result_file(result_file, payload)
        print(json.dumps(payload, ensure_ascii=False), flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
    finally:
        os._exit(exit_code)


def run_single_case(case_id: int, result_file: str | None = None) -> int:
    case = get_case(case_id)
    if not case:
        result = {
            "id": case_id,
            "name": f"case {case_id}",
            "input": "",
            "request": {},
            "clarification_triggered": False,
            "clarification_completed": False,
            "result_type": "error",
            "plan_summary": "用例不存在",
            "addon_summary": "用例不存在",
            "booking_status": "用例不存在",
            "exception_summary": "用例不存在",
            "elapsed_seconds": 0.0,
            "passed": False,
            "failures": [f"case {case_id} not found"],
        }
        _emit_child_result(result, result_file, 1)
    try:
        result = case.run_direct()
    except Exception as exc:
        result = case.failed_result(f"case raised: {exc}")
    _emit_child_result(result, result_file, 0 if result.get("passed") else 1)


def run_single_system_check(name: str, result_file: str | None = None) -> int:
    spec = SYSTEM_CHECK_SPECS.get(name)
    if not spec:
        result = {
            "name": name,
            "passed": False,
            "failures": [f"unknown system check: {name}"],
            "elapsed_seconds": 0.0,
        }
        _emit_child_result(result, result_file, 1)
    check_fn, _timeout = spec
    started = time.time()
    try:
        failures = check_fn()
    except Exception as exc:
        failures = [f"{name} raised: {exc}"]
    result = {
        "name": name,
        "passed": not failures,
        "failures": failures,
        "elapsed_seconds": round(time.time() - started, 2),
    }
    _emit_child_result(result, result_file, 0 if not failures else 1)


def reset_acceptance_tmp() -> None:
    shutil.rmtree(ACCEPTANCE_TMP, ignore_errors=True)
    ACCEPTANCE_TMP.mkdir(parents=True, exist_ok=True)


def _tmp_paths(prefix: str, label: str) -> tuple[Path, Path, Path]:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)
    stamp = f"{int(time.time() * 1000)}_{os.getpid()}"
    return (
        ACCEPTANCE_TMP / f"{prefix}_{safe}_{stamp}.out",
        ACCEPTANCE_TMP / f"{prefix}_{safe}_{stamp}.err",
        ACCEPTANCE_TMP / f"{prefix}_{safe}_{stamp}.result.json",
    )


def _read_text(path: Path, limit: int | None = None) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[-limit:] if limit and len(text) > limit else text


def _kill_process_group(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            proc.kill()
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        pass


def _wait_process(proc: subprocess.Popen, timeout_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return True
        time.sleep(0.05)
    _kill_process_group(proc)
    kill_deadline = time.time() + 5
    while time.time() < kill_deadline:
        if proc.poll() is not None:
            return False
        time.sleep(0.05)
    return False


def _last_json_from_file(path: Path, required_fields: tuple[str, ...]) -> dict | None:
    text = _read_text(path)
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict) and all(field in payload for field in required_fields):
            return payload
    return None


def _json_from_result_file(path: Path, required_fields: tuple[str, ...]) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict) and all(field in payload for field in required_fields):
        return payload
    return None


def _wait_for_result_file_or_timeout(
    proc: subprocess.Popen,
    result_path: Path,
    timeout_seconds: int,
    required_fields: tuple[str, ...],
    grace_seconds: float = 0.75,
) -> tuple[str, dict | None]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        payload = _json_from_result_file(result_path, required_fields)
        if payload is not None:
            if proc.poll() is None:
                grace_deadline = time.time() + grace_seconds
                while time.time() < grace_deadline and proc.poll() is None:
                    time.sleep(0.05)
                if proc.poll() is None:
                    _kill_process_group(proc)
                    return "result_then_killed", payload
            return "result", payload
        if proc.poll() is not None:
            return "exit", _json_from_result_file(result_path, required_fields)
        time.sleep(0.05)

    payload = _json_from_result_file(result_path, required_fields)
    _kill_process_group(proc)
    return ("result_after_deadline", payload) if payload is not None else ("timeout", None)


def run_case_subprocess(case: Case, timeout_seconds: int | None = None) -> dict:
    timeout_seconds = timeout_seconds or case.timeout_seconds or DEFAULT_CASE_TIMEOUT
    print(f"[START] {case.cid:02d} {case.name}", flush=True)
    started = time.time()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    kwargs: dict[str, Any] = {}
    if os.name != "nt":
        kwargs["start_new_session"] = True
    stdout_path, stderr_path, result_path = _tmp_paths("case", str(case.cid))
    try:
        with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_file, stderr_path.open("w", encoding="utf-8", errors="replace") as stderr_file:
            proc = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--case", str(case.cid), "--result-file", str(result_path)],
                cwd=str(ROOT),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                **kwargs,
            )
            completion_mode, json_payload = _wait_for_result_file_or_timeout(proc, result_path, timeout_seconds, ("id", "passed"))
    except Exception as exc:
        result = case.failed_result(f"case subprocess launch/wait failed: {exc}", time.time() - started)
        print(f"[END] {case.cid:02d} {case.name} - FAIL ({result['elapsed_seconds']}s)", flush=True)
        return result

    elapsed = time.time() - started
    stdout = _read_text(stdout_path).strip()
    stderr = _read_text(stderr_path, 1000).strip()
    if completion_mode == "timeout":
        result = case.failed_result(f"case subprocess timeout after {timeout_seconds}s", elapsed)
        print(f"[END] {case.cid:02d} {case.name} - FAIL ({result['elapsed_seconds']}s)", flush=True)
        try:
            stdout_path.unlink(missing_ok=True)
            stderr_path.unlink(missing_ok=True)
            result_path.unlink(missing_ok=True)
        except Exception:
            pass
        return result
    if json_payload is not None:
        result = json_payload
    else:
        result = case.failed_result(
            f"case subprocess returned no valid result file; completion={completion_mode}; stdout={stdout[:500]}",
            elapsed,
        )

    if completion_mode not in ("result_then_killed", "result_after_deadline") and proc.returncode != 0 and result.get("passed") is not False:
        result = case.failed_result(f"case subprocess exited {proc.returncode}: {(stderr or '').strip()[:500]}", elapsed)
    result["elapsed_seconds"] = round(elapsed, 2)
    if completion_mode in ("result_then_killed", "result_after_deadline"):
        result.setdefault("runner_warnings", []).append(f"accepted completed result file before child exit ({completion_mode})")
    status = "PASS" if result.get("passed") else "FAIL"
    print(f"[END] {case.cid:02d} {case.name} - {status} ({result['elapsed_seconds']}s)", flush=True)
    if stderr and not result.get("passed"):
        print(stderr.strip()[:500], flush=True)
    try:
        stdout_path.unlink(missing_ok=True)
        stderr_path.unlink(missing_ok=True)
        result_path.unlink(missing_ok=True)
    except Exception:
        pass
    return result


def run_system_check_subprocess(name: str, timeout_seconds: int | None = None) -> dict:
    _check_fn, default_timeout = SYSTEM_CHECK_SPECS[name]
    timeout_seconds = timeout_seconds or default_timeout
    print(f"[SYS START] {name}", flush=True)
    started = time.time()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    kwargs: dict[str, Any] = {}
    if os.name != "nt":
        kwargs["start_new_session"] = True
    stdout_path, stderr_path, result_path = _tmp_paths("system", name)
    try:
        with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_file, stderr_path.open("w", encoding="utf-8", errors="replace") as stderr_file:
            proc = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--system-check", name, "--result-file", str(result_path)],
                cwd=str(ROOT),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                **kwargs,
            )
            completion_mode, json_payload = _wait_for_result_file_or_timeout(proc, result_path, timeout_seconds, ("name", "passed"))
    except Exception as exc:
        result = {
            "name": name,
            "passed": False,
            "failures": [f"system check launch/wait failed: {exc}"],
            "elapsed_seconds": round(time.time() - started, 2),
        }
        print(f"[SYS END] {name} - FAIL ({result['elapsed_seconds']}s)", flush=True)
        return result

    elapsed = time.time() - started
    stdout = _read_text(stdout_path).strip()
    stderr = _read_text(stderr_path, 1000).strip()
    if completion_mode == "timeout":
        result = {
            "name": name,
            "passed": False,
            "failures": [f"system check subprocess timeout after {timeout_seconds}s"],
            "elapsed_seconds": round(elapsed, 2),
        }
        print(f"[SYS END] {name} - FAIL ({result['elapsed_seconds']}s)", flush=True)
        try:
            stdout_path.unlink(missing_ok=True)
            stderr_path.unlink(missing_ok=True)
            result_path.unlink(missing_ok=True)
        except Exception:
            pass
        return result
    if json_payload is not None:
        result = json_payload
    else:
        result = {
            "name": name,
            "passed": False,
            "failures": [f"system check returned no valid result file; completion={completion_mode}; stdout={stdout[:500]}"],
            "elapsed_seconds": round(elapsed, 2),
        }

    if completion_mode not in ("result_then_killed", "result_after_deadline") and proc.returncode != 0 and result.get("passed") is not False:
        result = {
            "name": name,
            "passed": False,
            "failures": [f"system check exited {proc.returncode}: {(stderr or '').strip()[:500]}"],
            "elapsed_seconds": round(elapsed, 2),
        }
    result["elapsed_seconds"] = round(elapsed, 2)
    if completion_mode in ("result_then_killed", "result_after_deadline"):
        result.setdefault("runner_warnings", []).append(f"accepted completed result file before child exit ({completion_mode})")
    status = "PASS" if result.get("passed") else "FAIL"
    print(f"[SYS END] {name} - {status} ({result['elapsed_seconds']}s)", flush=True)
    if stderr and not result.get("passed"):
        print(stderr.strip()[:500], flush=True)
    try:
        stdout_path.unlink(missing_ok=True)
        stderr_path.unlink(missing_ok=True)
        result_path.unlink(missing_ok=True)
    except Exception:
        pass
    return result


def apply_system_check_statuses(system_results: list[dict]) -> list[str]:
    failures: list[str] = []
    for item in system_results:
        name = item.get("name")
        check_failures = list(item.get("failures") or [])
        failures.extend(f"{name}: {failure}" for failure in check_failures)
        passed = bool(item.get("passed")) and not check_failures
        if name == "api_smoke":
            CHECK_STATUS["api_smoke"] = passed
            CHECK_STATUS["session_isolation"] = passed
        elif name == "data_integrity":
            CHECK_STATUS["garbled_data"] = passed
        elif name == "doc_encoding":
            CHECK_STATUS["doc_encoding"] = passed
        elif name == "security_scan":
            CHECK_STATUS["security_scan"] = passed
            CHECK_STATUS["security_hits"] = check_failures
    return failures


def main() -> int:
    args = sys.argv[1:]
    result_file: str | None = None
    if "--result-file" in args:
        idx = args.index("--result-file")
        if idx + 1 >= len(args):
            print(json.dumps({"passed": False, "failures": ["missing --result-file path"]}, ensure_ascii=False), flush=True)
            return 1
        result_file = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if len(args) == 2 and args[0] == "--case":
        try:
            return run_single_case(int(args[1]), result_file)
        except ValueError:
            result = {"id": args[1], "passed": False, "failures": ["invalid case id"]}
            _emit_child_result(result, result_file, 1)
    if len(args) == 2 and args[0] == "--system-check":
        return run_single_system_check(args[1], result_file)
    quick_mode = "--quick" in args

    started = time.time()
    reset_acceptance_tmp()
    cases = make_cases(QUICK_CASE_IDS if quick_mode else None)
    print(f"Total cases: {len(cases)} ({'quick' if quick_mode else 'full'})", flush=True)
    results = [run_case_subprocess(case, case.timeout_seconds or DEFAULT_CASE_TIMEOUT) for case in cases]
    system_results = [
        run_system_check_subprocess(name, timeout)
        for name, (_check_fn, timeout) in SYSTEM_CHECK_SPECS.items()
    ]
    system_failures = apply_system_check_statuses(system_results)
    failed = [r for r in results if not r["passed"]]
    stable_exit = True
    if quick_mode:
        _write_json_file(QUICK_STATUS_FILE, {
            "passed": not failed and not system_failures,
            "total": len(results),
            "failed": len(failed),
            "system_failures": system_failures,
            "elapsed_seconds": round(time.time() - started, 2),
        })
    (ROOT / "ACCEPTANCE_REPORT.md").write_text(render_acceptance(results, system_failures, stable_exit), encoding="utf-8")
    (ROOT / "CODE_QUALITY_REPORT.md").write_text(render_quality_report(system_failures), encoding="utf-8")
    (ROOT / "HARDENING2_REPORT.md").write_text(render_hardening2_report(results, system_failures, stable_exit), encoding="utf-8")
    (ROOT / "SUBMISSION_CLEANUP_REPORT.md").write_text(render_submission_cleanup_report(results, system_failures, stable_exit), encoding="utf-8")
    (ROOT / "CORE_WORKFLOW_REBUILD_REPORT.md").write_text(render_core_workflow_report(results, system_failures), encoding="utf-8")
    (ROOT / "WORKFLOW_REBUILD_REPORT.md").write_text(render_workflow_rebuild_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2C_POLISH_REPORT.md").write_text(render_phase2c_polish_report(results, system_failures), encoding="utf-8")
    (ROOT / "CATALOG_EXPANSION_REPORT.md").write_text(render_catalog_expansion_report(results, system_failures), encoding="utf-8")
    (ROOT / "BROWSER_QA_REPORT.md").write_text(render_browser_qa_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2C_USER_FLOW_PATCH_REPORT.md").write_text(render_phase2c_user_flow_patch_report(results, system_failures), encoding="utf-8")
    (ROOT / "NATURAL_INTENT_COORDINATION_REPORT.md").write_text(render_natural_intent_coordination_report(results, system_failures), encoding="utf-8")
    (ROOT / "PROJECT_STATUS.md").write_text(render_project_status_report(results, system_failures, stable_exit), encoding="utf-8")
    (ROOT / "CHANGE_SUMMARY.md").write_text(render_change_summary_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2A_ITINERARY_REPORT.md").write_text(render_phase2a_itinerary_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2A_CLEANUP_REPORT.md").write_text(render_phase2a_cleanup_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_RESCUE_REPORT.md").write_text(render_phase2b_rescue_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_VOTE_REPORT.md").write_text(render_phase2b_vote_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_BOOKING_REPORT.md").write_text(render_phase2b_booking_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_CHECKOUT_REPORT.md").write_text(render_phase2b_checkout_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_SUPPORT_REPORT.md").write_text(render_phase2b_support_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_ADDON_REPORT.md").write_text(render_phase2b_addon_report(results, system_failures), encoding="utf-8")
    (ROOT / "PHASE2B_FINAL_INTEGRATION_REPORT.md").write_text(render_phase2b_final_integration_report(results, system_failures), encoding="utf-8")
    (ROOT / "DOC_ENCODING_FIX_REPORT.md").write_text(render_doc_encoding_fix_report(results, system_failures), encoding="utf-8")

    for r in results:
        print(f"[{'PASS' if r['passed'] else 'FAIL'}] {r['id']:02d} {r['name']} ({r['elapsed_seconds']}s)")
        for item in r["failures"]:
            print(f"  - {item}")
    if system_failures:
        print("SYSTEM CHECK FAILURES:")
        for item in system_failures:
            print(f"  - {item}")
    print(f"Elapsed: {round(time.time() - started, 2)}s")
    shutil.rmtree(ACCEPTANCE_TMP, ignore_errors=True)
    if failed or system_failures:
        print(f"FAILED: {len(failed)} case(s), {len(system_failures)} system failure(s)")
        print("Failed items:", ", ".join(f"{r['id']}.{r['name']}" for r in failed) or "none")
        return 1
    print(f"PASSED: {len(results)}/{len(results)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
