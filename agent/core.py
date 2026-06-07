"""
core.py —— Agent 编排者。按 Python 顺序驱动整条流程。
对外只有 Agent 类的 6 个方法：run / choose / confirm_and_execute / inject_exception /
                              reject_merchant / replace_step。
"""
import sys
import os
import json
import re
import copy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.logbook import LogBook
from agent.parser import parse_request
from agent.planner import build_itinerary, replan, score_plan
from agent.tools import check_availability, book_item, compose_share_card
from agent.addon import suggest_addon, suggest_addons
from agent.checkout import (
    apply_checkout_strategy,
    build_checkout_preview,
    pay_mock_checkout,
    split_mock_checkout,
)
from agent.constraint_engine import build_constraints
from agent.group_decision import build_group_decision
from agent.price_optimizer import optimize_price
from agent.itinerary_model import (
    attach_closed_itineraries,
    build_booking_review,
    mark_booking_review_confirmed,
    shift_plan_for_booking_review,
)
from agent.support import (
    apply_support_action,
    create_support_case,
    get_support_case,
    reply_support_case,
)


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_profile() -> dict:
    try:
        path = os.path.join(DATA_DIR, "user_profile.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _coerce_int(value, default: int) -> int:
    out = default
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        out = value
    elif isinstance(value, float):
        out = int(value)
    elif isinstance(value, str):
        m = re.search(r"\d+", value)
        if m:
            out = int(m.group(0))
    return out if out > 0 else default


def _coerce_time(value, default: str = "14:00") -> str:
    if isinstance(value, int):
        return f"{value:02d}:00"
    if isinstance(value, float):
        return f"{int(value):02d}:00"
    if isinstance(value, str):
        s = value.strip()
        m = re.search(r"(\d{1,2})\s*[:：]\s*(\d{1,2})", s)
        if m:
            return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"
        if s.isdigit():
            return f"{int(s):02d}:00"
    return default


def _normalize_request_types(request: dict) -> dict:
    request = dict(request or {})
    if request.get("party_size") is not None:
        request["party_size"] = _coerce_int(request.get("party_size"), 1 if request.get("scene") == "stay_in" else 4)
    if request.get("budget_per_person") is not None:
        request["budget_per_person"] = _coerce_int(request.get("budget_per_person"), 150)
    if request.get("window_hours") is not None:
        request["window_hours"] = _coerce_int(request.get("window_hours"), 5)
    if request.get("start_time") is not None:
        request["start_time"] = _coerce_time(request.get("start_time"), "14:00")
    diet = request.get("diet_limits", [])
    if diet == "none":
        diet = []
    elif isinstance(diet, str):
        diet = [diet]
    request["diet_limits"] = diet
    return request


def _planning_request(request: dict) -> dict:
    """Use local fallback values for tools without writing them back to request."""
    out = dict(request or {})
    frame = (request or {}).get("intent_frame") or {}
    sources = frame.get("field_sources") or {}
    trusted_home_area = sources.get("home_area") in {"explicit_text", "user_answer", "profile_memory"}
    if request.get("origin_area"):
        out["origin_area"] = request.get("origin_area")
    elif not trusted_home_area and out.get("scene") != "stay_in":
        out.pop("home_area", None)
    if trusted_home_area and out.get("home_area") and out.get("scene") != "stay_in":
        out["target_area_locked"] = True
    out["party_size"] = _coerce_int(out.get("party_size"), 1 if out.get("scene") == "stay_in" else 4)
    out["budget_per_person"] = _coerce_int(out.get("budget_per_person"), 150)
    out["window_hours"] = _coerce_int(out.get("window_hours"), 5)
    out["start_time"] = _coerce_time(out.get("start_time"), "14:00")
    return out


def _sync_intent_frame_from_answers(request: dict, answers: dict) -> dict:
    """Mark clarified fields as user-provided in intent_frame."""
    request = dict(request or {})
    frame = dict(request.get("intent_frame") or {})
    confirmed = dict(frame.get("confirmed_fields") or {})
    sources = dict(frame.get("field_sources") or {})
    unknown = list(frame.get("unknown_fields") or [])
    answer_map = {
        "party_size": "party_size",
        "start_time": "start_time",
        "end_time": "end_time",
        "duration_minutes": "duration_minutes",
        "home_area": "home_area",
        "friend_areas": "friend_areas",
        "budget_per_person": "budget_per_person",
        "transport": "transport",
        "dine_mode": "dine_mode",
        "cuisine_preference": "cuisine_preference",
        "diet_limits": "diet_limits",
        "occasion": "occasion",
        "date_preferences": "date_preferences",
        "style": "style",
        "activity_choice": "activity_choice",
        "script_style": "script_style",
    }
    if "window_hours" in answers and answers.get("window_hours") not in (None, ""):
        try:
            confirmed["duration_minutes"] = int(answers["window_hours"]) * 60
            sources["duration_minutes"] = "user_answer"
            unknown = [x for x in unknown if x not in ("duration_minutes", "window_hours")]
        except Exception:
            pass
    for answer_key, field in answer_map.items():
        if answer_key not in answers or answers.get(answer_key) in (None, ""):
            continue
        value = request.get(answer_key, answers.get(answer_key))
        if field == "duration_minutes" and value is not None:
            try:
                value = int(value)
            except Exception:
                pass
        confirmed[field] = value
        sources[field] = "user_answer"
        unknown = [x for x in unknown if x != field]
    frame["confirmed_fields"] = confirmed
    frame["field_sources"] = sources
    frame["unknown_fields"] = unknown
    request["intent_frame"] = frame
    return request


def _apply_planning_context(request: dict, context: dict | None) -> dict:
    """Apply explicit UI context before planning without treating parser defaults as user text."""
    context = dict(context or {})
    answers: dict = {}
    for key in ("home_area", "start_time", "transport"):
        value = context.get(key)
        if value not in (None, "", "unknown"):
            answers[key] = value
    if not answers:
        return request

    request = dict(request or {})
    frame = request.get("intent_frame") or {}
    sources = frame.get("field_sources") or {}

    chosen_area = answers.get("home_area")
    if chosen_area:
        parsed_area = request.get("home_area")
        parsed_source = sources.get("home_area")
        request["origin_area"] = chosen_area
        request["origin_area_source"] = "user_answer"
        if parsed_source not in {"explicit_text", "user_answer", "profile_memory"}:
            request["home_area"] = chosen_area
            request["target_area_locked"] = True
        elif parsed_area == chosen_area:
            request["home_area"] = chosen_area
            request["target_area_locked"] = True
        elif parsed_source in {"explicit_text", "user_answer", "profile_memory"}:
            request["target_area_locked"] = True

    if answers.get("start_time"):
        request["start_time"] = answers["start_time"]
    if answers.get("transport"):
        request["transport"] = answers["transport"]

    sync_answers = {k: v for k, v in answers.items() if k != "home_area"}
    if chosen_area and (sources.get("home_area") not in {"explicit_text", "profile_memory"} or request.get("home_area") == chosen_area):
        sync_answers["home_area"] = chosen_area
    request = _sync_intent_frame_from_answers(request, sync_answers)

    need = []
    answered_keys = set(sync_answers)
    if chosen_area:
        answered_keys.add("home_area")
    for q in request.get("clarifications_needed", []) or []:
        if q.get("key") not in answered_keys:
            need.append(q)
    request["clarifications_needed"] = need
    request["missing_fields"] = [q.get("key") for q in need if q.get("key")]
    if not need and request.get("next_action") == "ask_clarification":
        request["next_action"] = "build_plan"
    return request


def _as_list(value) -> list:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [x for x in value if x not in (None, "")]
    return [value]


def _detect_feedback_intent(text: str) -> dict | None:
    text = text or ""
    if re.search(r"朋友.*晚|晚半小时|晚到|迟到|顺一下|顺延", text):
        return {"type": "time_conflict", "feedback_intent": "friend_late"}
    if re.search(r"满座|排队太久|排队久|到.*门口.*排队|换一家", text):
        return {
            "type": "restaurant_full",
            "feedback_intent": "queue_or_full",
            "context": {"location_state": "near_current_merchant"},
        }
    if re.search(r"太恐怖|换轻松一点|轻松一点|别太吓人", text):
        return {"type": "ticket_soldout", "feedback_intent": "too_horror", "script_style": "欢乐本"}
    if re.search(r"太贵|预算超|超预算|换便宜点|便宜点", text):
        return {"type": "budget_conflict", "feedback_intent": "too_expensive"}
    if re.search(r"换近一点|近一点|太远|别太远", text):
        return {
            "type": "restaurant_full",
            "feedback_intent": "nearer",
            "context": {"location_state": "near_current_merchant"},
        }
    return None


class Agent:
    """本地生活执行助手的核心编排者。流程由 Python 代码顺序驱动，不由大模型决定。"""

    def __init__(self):
        self.logbook = LogBook()
        self.memory_rejected_ids: list[str] = []
        self.session: dict = self._fresh_session()

    def _fresh_session(self) -> dict:
        return {
            "request": None,
            "profile": _load_profile(),
            "plans": [],
            "chosen": None,
            "executed": False,
            "rejected_ids": list(self.memory_rejected_ids),   # 用户拒绝过的商户 id 列表（catalog 排序前剔除）
            "addon": None,
            "rejected_addon_ids": [],
            "accepted_addons": [],
            "share_card": "",
            "bookings": [],
            "booking_review": None,
            "booking_result": None,
            "checkout_preview": None,
            "checkout_result": None,
            "checkout_split": None,
            "checkout_error": None,
            "logs": [],
            "exception_result": None,
            # 追问中转：当 parse 出来发现关键信息缺失时，先停下来让用户补
            "mode": "ready",                    # ready / needs_clarification / planned / executed
            "clarifications_needed": [],
            "explicit_categories": [],
            "intent_frame": None,
            "constraints": {},
            "group_decision": {},
            "vote_decision": None,
            "price_optimization": {},
            "support_case": None,
            "support_cases": {},
            "support_error": None,
        }

    def _snapshot(self) -> dict:
        """Return a caller-facing snapshot so later refinement does not mutate prior results."""
        return copy.deepcopy(self.session)

    def _clear_mock_fulfillment_state(
        self,
        *,
        clear_booking_review: bool = False,
        clear_vote: bool = False,
        clear_support: bool = False,
        clear_exception: bool = False,
    ) -> None:
        """Invalidate downstream Mock state after the selected plan changes."""
        self.session["executed"] = False
        self.session["bookings"] = []
        self.session["share_card"] = ""
        if clear_booking_review:
            self.session["booking_review"] = None
        self.session["booking_result"] = None
        self.session["accepted_addons"] = []
        self.session["addon"] = None
        self.session["checkout_preview"] = None
        self.session["checkout_result"] = None
        self.session["checkout_split"] = None
        self.session["checkout_error"] = None
        if clear_vote:
            self.session["vote_room"] = None
            self.session["vote_decision"] = None
        if clear_support:
            self.session["support_case"] = None
            self.session["support_cases"] = {}
            self.session["support_error"] = None
        if clear_exception:
            self.session["exception_result"] = None

    # ─────────────────────────────────────────────────────────────────
    # 主流程
    # ─────────────────────────────────────────────────────────────────
    def run(self, text: str, context: dict | None = None) -> dict:
        """
        一句话 → 解析 → (若信息够 → 排方案 → 查余位)；
        若信息缺失 → 立即返回追问，让用户先补全再走 refine()。
        """
        feedback = _detect_feedback_intent(text)
        if feedback and self.session.get("chosen"):
            self.logbook.clear()
            request = self.session.get("request") or {}
            request["feedback_intent"] = feedback.get("feedback_intent")
            if feedback.get("script_style"):
                request["script_style"] = feedback["script_style"]
                prefs = set(request.get("preferences", []) or [])
                prefs.add("easy_pace")
                prefs.add("newbie_friendly")
                request["preferences"] = list(prefs)
            context = dict(feedback.get("context") or {})
            if context.get("location_state") == "near_current_merchant":
                for step in self.session.get("chosen", {}).get("steps", []):
                    if step.get("kind") in ("restaurant", "activity"):
                        context.setdefault("current_area", step.get("area"))
                        context.setdefault("current_merchant_id", step.get("id"))
                        break
            self.logbook.add("用户反馈", "warning", f"识别为 {feedback.get('feedback_intent')}，进入局部重排")
            return self.inject_exception(feedback["type"], context)

        self.logbook.clear()
        self.session = self._fresh_session()

        # 1) 解析
        request = parse_request(text, self.logbook)
        request = _apply_planning_context(request, context)
        request["_rejected_ids"] = set(self.session["rejected_ids"])
        self.session["request"] = request
        self.session["explicit_categories"] = request.get("explicit_categories", [])
        self.session["clarifications_needed"] = request.get("clarifications_needed", [])
        self.session["intent_frame"] = request.get("intent_frame")
        self.session["constraints"] = build_constraints(request, request.get("intent_frame"))
        self.session["group_decision"] = build_group_decision(text, request.get("intent_frame"))

        # 2) 信息严重缺失 → 进入追问模式，不出方案
        if request.get("next_action") != "build_plan" or self.session["clarifications_needed"]:
            self.session["mode"] = "needs_clarification"
            if request.get("next_action") == "rest_support":
                self.session["mode"] = "rest_support"
            elif request.get("next_action") == "show_category_choices":
                self.session["mode"] = "category_choices"
            self.logbook.add("请用户补充", "warning",
                             "信息不全，已暂停规划，等待用户补充关键信息后再继续")
            self.session["logs"] = self.logbook.to_list()
            return self._snapshot()

        # 3) 信息齐了 → 排方案 + 查余位
        return self._build_and_check(request)

    def refine(self, answers: dict) -> dict:
        """
        用户回答了追问的字段后，把答案合并进 request，重新走规划。
        answers 形如 {"party_size": 4, "budget_per_person": 150}。
        """
        request = self.session.get("request") or {}
        if not request:
            self.logbook.add("补充信息", "error", "没有正在追问的会话")
            self.session["logs"] = self.logbook.to_list()
            return self.session

        # 合并答案
        applied = []
        for k, v in (answers or {}).items():
            if v is None or v == "":
                continue
            try:
                # 数字字段强转
                if k in ("party_size", "budget_per_person", "window_hours"):
                    v = int(v)
            except Exception:
                continue
            if k == "diet_limits":
                if v == "none":
                    v = []
                elif isinstance(v, str):
                    v = [v]
            if k == "experience_mode":
                if v == "stay_in_online":
                    request["scene"] = "stay_in"
                    request["main_role"] = "STAYIN"
                    request["primary_intent"] = "stay_in"
                    request["requested_categories"] = ["在线电影"]
                    request["explicit_categories"] = [{"role": "STAYIN", "category": "在线电影", "keyword": "在线看"}]
                    request["home_area"] = "线上"
                elif v == "cinema_out":
                    request["scene"] = "play_only"
                    request["main_role"] = "PLAY"
                    request["primary_intent"] = "movie"
                    request["requested_categories"] = ["电影院"]
                    request["explicit_categories"] = [{"role": "PLAY", "category": "电影院", "keyword": "影院"}]
                    neg = set(request.get("negative_intents", []) or [])
                    neg.discard("no_outdoor")
                    request["negative_intents"] = list(neg)
                request.pop("intent_conflict", None)
                request["confidence"] = 0.86
                applied.append(f"{k}={v}")
                continue
            if k == "date_preferences":
                choices = _as_list(v)
                request["date_preferences"] = choices
                prefs = set(request.get("preferences") or [])
                explicit = list(request.get("explicit_categories") or [])
                play_cats: list[str] = []
                if "看电影" in choices:
                    play_cats.append("电影院")
                if "拍照" in choices:
                    prefs.add("photo_friendly")
                    play_cats.extend(["展览", "景区"])
                if "散步" in choices:
                    prefs.add("easy_pace")
                    play_cats.append("景区")
                if "甜品" in choices:
                    prefs.add("dessert")
                if "轻松聊天" in choices:
                    prefs.add("quiet")
                if "不太累" in choices:
                    prefs.add("easy_pace")
                for cat in play_cats:
                    if not any(x.get("role") == "PLAY" and x.get("category") == cat for x in explicit):
                        explicit.append({"role": "PLAY", "category": cat, "keyword": "约会偏好"})
                request["date_wants_food"] = "吃饭" in choices
                request["preferences"] = sorted(prefs)
                request["explicit_categories"] = explicit
                request["scene"] = "couple"
                request["primary_intent"] = "date"
                request["main_role"] = "PLAY"
                request["confidence"] = max(float(request.get("confidence") or 0), 0.86)
                applied.append(f"{k}={choices}")
                continue
            if k == "script_style":
                choices = _as_list(v)
                request["script_style_choices"] = choices
                chosen = next((x for x in choices if x and x != "不限"), None)
                if chosen:
                    request["script_style"] = chosen
                applied.append(f"{k}={choices}")
                continue
            if k == "cuisine_preference":
                choices = _as_list(v)
                request["cuisine_preferences"] = choices
                chosen = next((x for x in choices if x and x != "都可以"), None)
                request["cuisine_preference"] = chosen or "都可以"
                if chosen:
                    explicit = [x for x in (request.get("explicit_categories") or []) if x.get("role") != "EAT"]
                    explicit.extend({"role": "EAT", "category": x, "keyword": "菜系偏好"} for x in choices if x and x != "都可以")
                    request["explicit_categories"] = explicit
                    request["requested_categories"] = list(dict.fromkeys((request.get("requested_categories") or []) + [x for x in choices if x != "都可以"]))
                applied.append(f"{k}={choices}")
                continue
            if k == "style":
                choices = _as_list(v)
                prefs = set(request.get("preferences") or [])
                for item in choices:
                    if item in ("出片", "浪漫"):
                        prefs.add("photo_friendly")
                    if item in ("安静", "轻松"):
                        prefs.add("quiet")
                    if item == "惊喜":
                        prefs.add("ritual")
                request["date_styles"] = choices
                request["preferences"] = sorted(prefs)
                applied.append(f"{k}={choices}")
                continue
            if k == "activity_choice":
                choices = _as_list(v)
                mapping = {
                    "剧本杀": ("script_game", "PLAY", "剧本杀"),
                    "KTV": ("outing", "PLAY", "KTV"),
                    "台球": ("outing", "PLAY", "台球"),
                    "密室": ("outing", "PLAY", "密室"),
                    "电影": ("movie", "PLAY", "电影院"),
                    "电影院": ("movie", "PLAY", "电影院"),
                    "桌游": ("outing", "PLAY", "桌游"),
                }
                selected = [mapping[x] for x in choices if x in mapping]
                if selected:
                    primary, role, cat = selected[0]
                    request["primary_intent"] = primary
                    request["main_role"] = role
                    request["requested_categories"] = list(dict.fromkeys(x[2] for x in selected))
                    request["activity_choices"] = choices
                    request["explicit_categories"] = [
                        {"role": item_role, "category": item_cat, "keyword": str(choice)}
                        for choice, (_primary, item_role, item_cat) in zip([x for x in choices if x in mapping], selected)
                    ]
                    request["scene"] = "play_only"
                applied.append(f"{k}={choices}")
                continue
            request[k] = v
            applied.append(f"{k}={v}")
        request["next_action"] = "build_plan"
        request = _normalize_request_types(request)
        request = _sync_intent_frame_from_answers(request, answers or {})
        request["constraints"] = build_constraints(request, request.get("intent_frame"))
        # 清空"待追问"
        request["clarifications_needed"] = []
        request["missing_fields"] = []
        self.session["clarifications_needed"] = []
        request["_rejected_ids"] = set(self.session["rejected_ids"])
        self.session["request"] = request
        self.session["constraints"] = request["constraints"]

        self.logbook.add("补充信息", "success",
                         f"已收到补充：{'、'.join(applied) if applied else '无'}")

        return self._build_and_check(request)

    def _build_and_check(self, request: dict) -> dict:
        """共用：排方案 + 查余位 + 更新画像评分。"""
        request = _normalize_request_types(request)
        self.session["request"] = request
        self.session["constraints"] = build_constraints(request, request.get("intent_frame"))
        planning_request = _planning_request(request)
        plans = build_itinerary(planning_request, self.logbook)
        for p in plans:
            optional = suggest_addons(
                p,
                planning_request,
                self.logbook,
                rejected_ids=set(self.session.get("rejected_addon_ids") or []),
            )
            p["commercial_recommendations"] = optional
            p["optional_addons"] = optional
            p["score"] = score_plan(p, planning_request, profile=self.session.get("profile"))
            p["price_optimization"] = optimize_price(p, planning_request)
        plans = attach_closed_itineraries(plans, request)
        self.session["plans"] = plans
        self.session["price_optimization"] = plans[0].get("price_optimization") if plans else {}

        # 查余位（每个方案的每个商户节点）
        for p in plans:
            for step in p.get("steps", []):
                if step.get("kind") in ("activity", "restaurant", "stayin", "delivery"):
                    res = check_availability(
                        step["id"], step.get("start", "14:00"),
                        planning_request.get("party_size", 2),
                        self.logbook,
                    )
                    step["_available"] = (res.get("data") or {}).get("available", False if not res.get("ok") else True)

        self.session["mode"] = "planned"
        self.session["logs"] = self.logbook.to_list()
        return self.session

    # ─────────────────────────────────────────────────────────────────
    def choose(self, plan_index: int) -> dict:
        plans = self.session.get("plans", [])
        if 0 <= plan_index < len(plans):
            self._clear_mock_fulfillment_state(
                clear_booking_review=True,
                clear_vote=True,
                clear_support=True,
                clear_exception=True,
            )
            self.session["chosen"] = plans[plan_index]
            if self.session["chosen"].get("itinerary"):
                self.session["chosen"]["itinerary"]["status"] = "selected"
                for seg in self.session["chosen"]["itinerary"].get("segments", []):
                    seg["status"] = "selected"
            self.session["booking_review"] = build_booking_review(
                self.session["chosen"],
                self.session.get("request") or {},
            )
            self.session["booking_result"] = None
            self.session["accepted_addons"] = []
            self.session["addon"] = None
            self.session["checkout_preview"] = None
            self.session["checkout_result"] = None
            self.session["checkout_split"] = None
            self.session["checkout_error"] = None
            self.session["mode"] = "selected"
            self.logbook.add("选择方案", "success",
                             f"你选择了「{plans[plan_index]['title']}」")
        else:
            self.logbook.add("选择方案", "error", f"方案下标 {plan_index} 越界")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def choose_segments(self, selected_segments: list[dict] | None = None) -> dict:
        """Choose one merchant per itinerary segment and build a local Mock mixed plan."""
        plans = self.session.get("plans", [])
        if not plans:
            self.logbook.add("分段选择", "error", "尚未生成候选方案")
            self.session["logs"] = self.logbook.to_list()
            return self.session

        selected_segments = selected_segments or []
        if not selected_segments:
            return self.choose(0)

        business_kinds = {"activity", "restaurant", "stayin", "delivery", "addon"}
        base = copy.deepcopy(plans[0])
        base_steps = list(base.get("steps") or [])
        business_positions = [i for i, s in enumerate(base_steps) if s.get("kind") in business_kinds]
        if not business_positions:
            return self.choose(0)

        choice_summary: list[dict] = []
        for item in selected_segments:
            try:
                seg_idx = int(item.get("segment_index", 0))
            except Exception:
                seg_idx = 0
            if seg_idx < 0 or seg_idx >= len(business_positions):
                continue
            step = item.get("step")
            if not isinstance(step, dict):
                try:
                    plan_idx = int(item.get("plan_index", 0))
                except Exception:
                    plan_idx = 0
                source_steps = [
                    s for s in (plans[plan_idx].get("steps") if 0 <= plan_idx < len(plans) else []) or []
                    if s.get("kind") in business_kinds
                ]
                step = copy.deepcopy(source_steps[seg_idx]) if seg_idx < len(source_steps) else None
            if not isinstance(step, dict):
                continue
            base_steps[business_positions[seg_idx]] = copy.deepcopy(step)
            try:
                plan_idx_for_label = int(item.get("plan_index", 0) or 0)
            except Exception:
                plan_idx_for_label = 0
            choice_summary.append({
                "segment_index": seg_idx,
                "plan_label": item.get("plan_label") or ("Plan B" if plan_idx_for_label == 1 else "Plan A"),
                "merchant_id": step.get("id"),
                "merchant_name": step.get("name"),
                "category": step.get("category"),
            })

        if not choice_summary:
            return self.choose(0)

        self._clear_mock_fulfillment_state(
            clear_booking_review=True,
            clear_vote=True,
            clear_support=True,
            clear_exception=True,
        )
        base["steps"] = base_steps
        business_steps = [s for s in base_steps if s.get("kind") in business_kinds]
        base["title"] = " + ".join(s.get("name") or s.get("category") or "行程" for s in business_steps[:3]) or base.get("title")
        base["segment_choices"] = choice_summary
        base["total_cost_per_person"] = sum(int(s.get("cost") or 0) for s in base_steps if s.get("kind") in business_kinds | {"travel"})
        base = attach_closed_itineraries([base], _planning_request(self.session.get("request") or {}))[0]
        self.session["chosen"] = base
        if self.session["chosen"].get("itinerary"):
            self.session["chosen"]["itinerary"]["status"] = "selected"
            for seg in self.session["chosen"]["itinerary"].get("segments", []):
                seg["status"] = "selected"
        self.session["segment_choices"] = choice_summary
        self.session["booking_review"] = build_booking_review(
            self.session["chosen"],
            self.session.get("request") or {},
        )
        self.session["mode"] = "selected"
        self.logbook.add("分段选择", "success", f"已确认 {len(choice_summary)} 段行程，进入预约核对")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    # ─────────────────────────────────────────────────────────────────
    def prepare_booking_review(self) -> dict:
        """Generate or refresh the per-segment Mock booking review."""
        chosen = self.session.get("chosen")
        if not chosen and self.session.get("plans"):
            self.choose(0)
            chosen = self.session.get("chosen")
        if not chosen:
            self.logbook.add("预约核对", "error", "尚未选择方案")
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self._clear_mock_fulfillment_state(clear_booking_review=False)
        self.session["booking_review"] = build_booking_review(chosen, self.session.get("request") or {})
        self.session["mode"] = "booking_review"
        self.logbook.add("预约核对", "running", "已生成逐段预约核对信息，等待发起人确认")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def update_booking_review(self, segment_index: int = 0, fields: dict | None = None) -> dict:
        """Edit local booking review fields and shift later itinerary times if needed."""
        chosen = self.session.get("chosen")
        if not chosen:
            self.logbook.add("预约核对", "error", "尚未选择方案，无法调整预约信息")
            self.session["logs"] = self.logbook.to_list()
            return self.session
        fields = fields or {}
        new_start = fields.get("scheduled_start") or fields.get("start_time")
        delta = fields.get("delta_minutes")
        try:
            segment_index = int(segment_index)
        except Exception:
            segment_index = 0
        try:
            delta_int = int(delta) if delta not in (None, "") else None
        except Exception:
            delta_int = None
        new_plan, review, warnings = shift_plan_for_booking_review(
            chosen,
            self.session.get("request") or {},
            segment_index,
            new_start=new_start,
            delta_minutes=delta_int,
        )
        self._clear_mock_fulfillment_state(clear_booking_review=False, clear_exception=True)
        self.session["chosen"] = new_plan
        self.session["booking_review"] = review
        self.session["mode"] = "booking_review"
        msg = "已更新预约核对时间，并顺延后续行程" if warnings else "预约核对信息已刷新"
        self.logbook.add("预约核对", "success", msg)
        self.session["logs"] = self.logbook.to_list()
        return self.session

    # ─────────────────────────────────────────────────────────────────
    def confirm_and_execute(self) -> dict:
        chosen = self.session.get("chosen")
        if not chosen:
            self.logbook.add("执行", "error", "尚未选择方案")
            self.session["logs"] = self.logbook.to_list()
            return self.session

        request = self.session.get("request", {})
        planning_request = _planning_request(request)
        party_size = planning_request.get("party_size", 2)
        bookings = []

        review = self.session.get("booking_review") or build_booking_review(chosen, request)
        bookable_segments = [
            s for s in review.get("segments", [])
            if s.get("bookable") and s.get("merchant_id")
        ]
        if not bookable_segments:
            self.logbook.add("执行", "warning", "没有可模拟预约的主行程段")
        for segment in bookable_segments:
            r = book_item(
                segment.get("merchant_id"),
                segment.get("scheduled_start") or segment.get("prefilled_fields", {}).get("scheduled_start") or "14:00",
                int(segment.get("party_size") or party_size or 1),
                self.logbook,
            )
            if r.get("ok"):
                bookings.append(r["data"])
        self.session["bookings"] = bookings
        self.session["booking_review"] = mark_booking_review_confirmed(review, bookings)
        self.session["booking_result"] = {
            "status": "mock_booked",
            "bookings": bookings,
            "mock_only": True,
            "real_payment": False,
            "real_booking": False,
        }
        if chosen.get("itinerary"):
            chosen["itinerary"]["status"] = "booked"
            for seg in chosen["itinerary"].get("segments", []):
                seg["status"] = "booked"

        optional = suggest_addons(
            chosen,
            planning_request,
            self.logbook,
            rejected_ids=set(self.session.get("rejected_addon_ids") or []),
        )
        chosen["commercial_recommendations"] = optional
        chosen["optional_addons"] = optional
        if chosen.get("itinerary"):
            chosen["itinerary"]["optional_addons"] = optional

        # 增值推荐：只暴露第一张可结算卡作为旧字段，完整列表在 optional_addons。
        addon = next((x for x in optional if x.get("checkout_eligible", True)), None)
        self.session["addon"] = addon
        self.session["checkout_preview"] = build_checkout_preview(
            chosen,
            self.session.get("booking_review"),
            self.session.get("booking_result"),
            self.session.get("accepted_addons") or [],
        )
        self.session["checkout_result"] = None
        self.session["checkout_split"] = None
        self.session["checkout_error"] = None

        # 分享卡
        share = compose_share_card(chosen, self.logbook)
        share = compose_share_card(chosen, self.logbook)
        self.session["share_card"] = share.get("data", {}).get("text", "")

        self.session["executed"] = True
        self.session["mode"] = "executed"
        self.session["logs"] = self.logbook.to_list()
        return self.session

    # ─────────────────────────────────────────────────────────────────
    def _refresh_checkout_preview(self) -> dict | None:
        """Refresh local Mock checkout preview after booking confirmation."""
        if not self.session.get("booking_result"):
            self.session["checkout_error"] = {
                "ok": False,
                "message": "请先完成最终预约，再查看 Mock 结算。",
                "code": "booking_required",
            }
            return None
        self.session["checkout_preview"] = build_checkout_preview(
            self.session.get("chosen"),
            self.session.get("booking_review"),
            self.session.get("booking_result"),
            self.session.get("accepted_addons") or [],
        )
        self.session["checkout_error"] = None
        return self.session["checkout_preview"]

    def accept_addon(self, addon_id: str | None = None) -> dict:
        """Explicitly accept an optional add-on so it can enter the Mock bill."""
        chosen = self.session.get("chosen") or {}
        optional = (
            chosen.get("optional_addons")
            or (chosen.get("itinerary") or {}).get("optional_addons")
            or chosen.get("commercial_recommendations")
            or []
        )
        addon = None
        if addon_id:
            wanted = str(addon_id)
            addon = next(
                (
                    x for x in optional
                    if str(x.get("addon_id") or x.get("id") or x.get("merchant_id") or "") == wanted
                    or str(x.get("merchant_id") or "") == wanted
                ),
                None,
            )
        if addon is None:
            addon = self.session.get("addon")
        if addon is None and optional:
            addon = next((x for x in optional if x.get("checkout_eligible", True)), None)
        if not addon:
            self.session["checkout_error"] = {
                "ok": False,
                "message": "当前没有可加入账单的可选加购。",
                "code": "no_addon",
            }
            self.session["logs"] = self.logbook.to_list()
            return self.session
        if not addon.get("checkout_eligible", True):
            self.session["checkout_error"] = {
                "ok": False,
                "message": "这张是内容攻略卡，不进入 Mock 账单。",
                "code": "addon_not_checkout_eligible",
            }
            self.session["logs"] = self.logbook.to_list()
            return self.session
        wanted = str(addon_id or addon.get("id") or addon.get("merchant_id") or "")
        addon_key = str(addon.get("addon_id") or addon.get("id") or addon.get("merchant_id") or "")
        merchant_key = str(addon.get("merchant_id") or "")
        if wanted and addon_key and wanted != addon_key:
            if merchant_key and wanted == merchant_key:
                pass
            else:
                self.session["checkout_error"] = {
                    "ok": False,
                    "message": "没有找到这个可选加购。",
                    "code": "addon_not_found",
                }
                self.session["logs"] = self.logbook.to_list()
                return self.session
        accepted = list(self.session.get("accepted_addons") or [])
        keys = {str(x.get("addon_id") or x.get("id") or x.get("merchant_id") or "") for x in accepted}
        if addon_key not in keys:
            accepted.append({**addon, "status": "accepted"})
        self.session["addon"] = addon
        self.session["accepted_addons"] = accepted
        self._refresh_checkout_preview()
        self.logbook.add("Mock 结算", "success", "可选加购已加入 Mock 账单")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def remove_addon(self, addon_id: str | None = None) -> dict:
        """Remove accepted add-ons from the Mock bill."""
        accepted = list(self.session.get("accepted_addons") or [])
        rejected = set(self.session.get("rejected_addon_ids") or [])
        if addon_id:
            wanted = str(addon_id)
            accepted = [
                x for x in accepted
                if str(x.get("addon_id") or x.get("id") or x.get("merchant_id") or "") != wanted
                and str(x.get("merchant_id") or "") != wanted
            ]
            rejected.add(wanted)
        else:
            addon = self.session.get("addon") or {}
            for key in (addon.get("addon_id"), addon.get("id"), addon.get("merchant_id")):
                if key:
                    rejected.add(str(key))
            accepted = []
        self.session["accepted_addons"] = accepted
        self.session["rejected_addon_ids"] = sorted(rejected)
        chosen = self.session.get("chosen") or {}
        optional = [
            x for x in (chosen.get("optional_addons") or [])
            if str(x.get("addon_id") or x.get("id") or x.get("merchant_id") or "") not in rejected
            and str(x.get("merchant_id") or "") not in rejected
        ]
        if chosen:
            chosen["optional_addons"] = optional
            chosen["commercial_recommendations"] = optional
            if chosen.get("itinerary"):
                chosen["itinerary"]["optional_addons"] = optional
        self.session["addon"] = next((x for x in optional if x.get("checkout_eligible", True)), None)
        self._refresh_checkout_preview()
        self.logbook.add("Mock 结算", "success", "可选加购未进入 Mock 账单")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def preview_checkout(self) -> dict:
        """Build local Mock checkout preview after booking confirmation."""
        self._refresh_checkout_preview()
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def apply_checkout(self, strategy_id: str | None = None) -> dict:
        """Select a local Mock checkout strategy without paying."""
        preview = self.session.get("checkout_preview") or self._refresh_checkout_preview()
        if not preview:
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self.session["checkout_preview"] = apply_checkout_strategy(preview, strategy_id)
        self.session["checkout_result"] = None
        self.logbook.add("Mock 结算", "success", "已切换优惠比较方案")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def pay_checkout(self, strategy_id: str | None = None) -> dict:
        """Create a local Mock payment result. No real payment is performed."""
        preview = self.session.get("checkout_preview") or self._refresh_checkout_preview()
        if not preview:
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self.session["checkout_result"] = pay_mock_checkout(preview, strategy_id)
        self.session["checkout_preview"] = apply_checkout_strategy(
            preview,
            self.session["checkout_result"].get("strategy_id"),
        )
        self.logbook.add("Mock 结算", "success", "已生成本地 Mock 支付结果")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def split_checkout(
        self,
        mode: str = "aa",
        members: list[str] | None = None,
        host: str = "发起人",
        exempted_members: list[str] | None = None,
    ) -> dict:
        """Create local Mock split-bill data. No real collection link is created."""
        preview = self.session.get("checkout_preview") or self._refresh_checkout_preview()
        if not preview:
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self.session["checkout_split"] = split_mock_checkout(
            preview,
            mode=mode,
            members=members,
            host=host,
            exempted_members=exempted_members,
        )
        self.logbook.add("Mock 分账", "success", "已生成本地 Mock 分账结果")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def inject_exception(self, exception_type: str, context: dict | None = None) -> dict:
        """注入异常，局部重排，更新 chosen 和分享卡。"""
        # 把已拒绝列表带进 session，replan 内部会读
        if self.session.get("request"):
            self.session["request"]["_rejected_ids"] = set(self.session["rejected_ids"])

        result = replan(self.session, exception_type, context or {}, self.logbook)
        self.session["exception_result"] = result

        new_plan = result.get("new_plan")
        if new_plan:
            new_plan = attach_closed_itineraries([new_plan], self.session.get("request") or {})[0]
            if new_plan.get("itinerary"):
                new_plan["itinerary"]["status"] = "changed"
            result["new_plan"] = new_plan
            self._clear_mock_fulfillment_state(
                clear_booking_review=True,
                clear_support=True,
            )
            self.session["chosen"] = new_plan
            self.session["booking_review"] = build_booking_review(new_plan, self.session.get("request") or {})
            self.session["mode"] = "selected"

            # 把被换掉的节点记入 rejected_ids
            before = result.get("before")
            if isinstance(before, dict) and before.get("id"):
                if before["id"] not in self.session["rejected_ids"]:
                    self.session["rejected_ids"].append(before["id"])

            # 重新生成分享卡
            share = compose_share_card(new_plan, self.logbook)
            self.session["share_card"] = share.get("data", {}).get("text", "")

        self.session["logs"] = self.logbook.to_list()
        return self.session

    # ─────────────────────────────────────────────────────────────────
    def create_support_case(
        self,
        session_id: str = "default",
        issue_type: str = "other",
        segment_id: str | None = None,
        target_segment_index: int | None = None,
        source: str | None = None,
        user_message: str | None = None,
    ) -> dict:
        """Create a local Mock support / aftersales case in the current session."""
        case = create_support_case(
            self.session,
            session_id=session_id,
            issue_type=issue_type,
            segment_id=segment_id,
            target_segment_index=target_segment_index,
            source=source,
            user_message=user_message,
        )
        self.session["support_error"] = None
        self.logbook.add("Mock support", "running", f"case={case.get('support_case_id')}, issue={case.get('issue_type')}")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def support_issue(self, segment_id: str, issue_type: str) -> dict:
        """Backward-compatible local Mock support entry for one itinerary segment."""
        return self.create_support_case(
            session_id="default",
            issue_type=issue_type,
            segment_id=segment_id,
            source="selected_itinerary",
        )

    def reply_support_case(self, support_case_id: str, message: str) -> dict:
        case = get_support_case(self.session, support_case_id)
        if not case:
            self.session["support_error"] = {
                "ok": False,
                "message": "Mock support case not found in this session.",
                "code": "support_case_not_found",
            }
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self.session["support_case"] = reply_support_case(case, message)
        self.session["support_error"] = None
        self.logbook.add("Mock support", "success", f"reply case={support_case_id}")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def apply_support_action(self, support_case_id: str, action_id: str) -> dict:
        case = get_support_case(self.session, support_case_id)
        if not case:
            self.session["support_error"] = {
                "ok": False,
                "message": "Mock support case not found in this session.",
                "code": "support_case_not_found",
            }
            self.session["logs"] = self.logbook.to_list()
            return self.session
        self.session["support_case"] = apply_support_action(case, action_id, self.session)
        self.session["support_error"] = None
        self.logbook.add("Mock support", "success", f"action={action_id}, case={support_case_id}")
        self.session["logs"] = self.logbook.to_list()
        return self.session

    def get_support_case(self, support_case_id: str) -> dict | None:
        return get_support_case(self.session, support_case_id)

    def reject_merchant(self, merchant_id: str) -> dict:
        """用户主动拒绝一个商户，下次检索前剔除。"""
        if merchant_id not in self.session["rejected_ids"]:
            self.session["rejected_ids"].append(merchant_id)
            if merchant_id not in self.memory_rejected_ids:
                self.memory_rejected_ids.append(merchant_id)
            self.logbook.add("用户反馈", "warning",
                             f"已记住「{merchant_id}」被拒绝，下次不再推荐")
        self.session["logs"] = self.logbook.to_list()
        return self.session


if __name__ == "__main__":
    agent = Agent()
    print("=== 测试 Agent 完整主流程 ===")
    session = agent.run("今天下午和朋友4个人出去玩，想拍照吃饭不要太累，人均150，晚上别排队")
    print(f"\n解析：scene={session['request']['scene']}, "
          f"{session['request']['party_size']}人, "
          f"¥{session['request']['budget_per_person']}/人")
    print(f"生成方案数：{len(session['plans'])}")
    for i, p in enumerate(session['plans']):
        print(f"  方案 {chr(65 + i)}: {p['title']} (评分 {p['score']['total']})")

    agent.choose(0)
    agent.confirm_and_execute()
    session = agent.session
    print(f"\n分享卡：\n{session.get('share_card', '')}")

    if session.get("addon"):
        print(f"\n增值推荐：{session['addon']['name']} ¥{session['addon']['price']}")

    print("\n--- 触发异常：餐厅满座 ---")
    agent.inject_exception("restaurant_full")
    session = agent.session
    exc = session.get("exception_result") or {}
    print(f"调整原因：{exc.get('reason', '')}")
    print(f"已记住的拒绝商户：{session.get('rejected_ids')}")
