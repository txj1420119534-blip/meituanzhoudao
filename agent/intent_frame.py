"""Intent truth layer.

This module separates what the user actually said from defaults that the
planner may use internally. The UI should read confirmed_fields/field_sources
instead of treating parser fallback values as confirmed user intent.
"""
from __future__ import annotations

import re
from typing import Any


AREA_RE = r"新街口|老门东|河西|马鞍山|夫子庙|鼓楼|玄武湖|江宁|仙林|百家湖|奥体"
AREA_OPTIONS = ["新街口", "老门东", "河西", "夫子庙", "鼓楼", "玄武湖", "江宁", "仙林", "百家湖", "奥体", "马鞍山"]
TIME_RE = r"(\d{1,2}[:：]\d{2})|今天|今晚|晚上|下午|中午|周末|明天"
BUDGET_RE = r"(人均|预算|每人|一个人|一人).{0,6}\d+|\d+\s*(块|元|/人)"
PARTY_RE = r"(\d+|一|两|二|三|四|五|六|七|八|九|十)\s*(个)?\s*(人|朋友|同学|同事)"
EAT_RE = r"吃饭|吃个饭|聚餐|找个地方吃|餐厅|晚饭|午饭|正餐|火锅|海鲜|烧烤|江浙菜|炒菜|好吃|吃点"
HOME_DELIVERY_RE = r"在家吃|宅家吃|不想出门吃|不出门吃|外卖|点外卖|送到家|小象|闪购|零食"
STAYIN_RE = r"在家|宅家|不想出门|不出门"
CUISINE_ANY_RE = r"菜系都可以|菜系不限|吃什么都行|随便吃点|随便吃|不挑|都可以"
MEAL_BRIDGE_RE = r"顺便吃点|中间吃点|补给|垫一下|吃点东西"


def _has(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text or "", re.I))


def _is_home_delivery_text(text: str) -> bool:
    return _has(HOME_DELIVERY_RE, text) or (_has(STAYIN_RE, text) and _has(r"吃|外卖|零食|小象|闪购|饮料|奶茶", text))


def _has_eat_in_intent(text: str) -> bool:
    return _has(EAT_RE, text) and not _is_home_delivery_text(text)


def _cuisine_preference(text: str, main_role: str = "UNKNOWN", sequence: list[dict[str, Any]] | None = None, negatives: set[str] | None = None) -> tuple[str | None, str]:
    if negatives and "no_meal" in negatives:
        return None, "unknown"
    has_eat_context = main_role == "EAT" or any(item.get("role") == "EAT" for item in (sequence or []))
    if _has(CUISINE_ANY_RE, text):
        return ("any", "explicit_text") if has_eat_context else (None, "unknown")
    if "火锅" in text:
        return "火锅", "explicit_text"
    if "海鲜" in text:
        return "海鲜", "explicit_text"
    if "烧烤" in text or "烤串" in text:
        return "烧烤", "explicit_text"
    if "江浙菜" in text or "炒菜" in text or "家常菜" in text:
        return "江浙菜", "explicit_text"
    if has_eat_context and _has_eat_in_intent(text):
        return "any", "planning_default"
    return None, "unknown"


def _dine_mode(text: str, main_role: str, sequence: list[dict[str, Any]], negatives: set[str] | None = None) -> tuple[str, str, dict[str, Any]]:
    if negatives and "no_meal" in negatives:
        return "unknown", "unknown", {}
    if _is_home_delivery_text(text):
        return "delivery", "explicit_text", {"modifiable": True}
    if _has(r"到店|店里吃|堂食", text):
        return "eat_in", "explicit_text", {"modifiable": True}
    has_eat = main_role == "EAT" or any(item.get("role") == "EAT" for item in sequence)
    if has_eat:
        return "eat_in", "planning_default", {"modifiable": True}
    return "unknown", "unknown", {}


def _stayin_sequence(text: str) -> list[dict[str, Any]]:
    if not _is_home_delivery_text(text):
        return []
    out: list[dict[str, Any]] = []
    if _has(r"外卖|点外卖|在家吃|宅家吃|吃点|正餐|晚饭|午饭", text):
        out.append({"role": "STAYIN", "category": "外卖", "source": "explicit_text"})
    if _has(r"零食|小象|闪购|饮料", text):
        out.append({"role": "STAYIN", "category": "闪购零食", "source": "explicit_text"})
    return out or [{"role": "STAYIN", "category": "外卖", "source": "explicit_text"}]


def _ordered_sequence(text: str, sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keyword_map = {
        "剧本杀": ["剧本杀", "打本", "打个本", "盒装本", "剧本"],
        "电影院": ["电影院", "影院", "电影"],
        "KTV": ["KTV", "唱歌", "唱K"],
        "台球": ["台球", "桌球"],
        "密室": ["密室"],
        "按摩": ["按摩", "足疗", "SPA"],
        "酒店": ["酒店"],
        "展览": ["看展", "展览"],
        "citywalk": ["citywalk", "马鞍山", "逛街", "散步"],
        "火锅": ["火锅"],
        "海鲜": ["海鲜"],
        "烧烤": ["烧烤", "烤串"],
        "江浙菜": ["江浙菜", "炒菜", "家常菜"],
        None: ["吃饭", "吃个饭", "吃点", "聚餐", "正餐", "好吃"],
        "奶茶": ["奶茶"],
        "咖啡": ["咖啡"],
    }

    def pos(item: dict[str, Any]) -> int:
        title = item.get("script_title")
        if title and text.find(title) >= 0:
            return text.find(title)
        keys = keyword_map.get(item.get("category"), keyword_map.get(None, []))
        hits = [text.find(k) for k in keys if k and text.find(k) >= 0]
        return min(hits) if hits else 9999

    return sorted(sequence, key=pos)


def _first_area(text: str) -> str | None:
    m = re.search(AREA_RE, text or "")
    return m.group(0) if m else None


def _parse_party(text: str) -> int | None:
    joint = re.search(r"(?:我和|我跟|我带|加我|和|跟|带)\s*(\d+|一|两|二|三|四|五|六|七|八|九|十)\s*(个)?\s*(朋友|同学|同事|人)", text or "")
    if joint:
        raw = joint.group(1)
        cn = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        base = int(raw) if raw.isdigit() else cn.get(raw)
        return base + 1 if base is not None else None
    m = re.search(PARTY_RE, text or "")
    if not m:
        return None
    raw = m.group(1)
    cn = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    return int(raw) if raw.isdigit() else cn.get(raw)


def _parse_budget(text: str) -> int | None:
    patterns = [
        r"(?:人均|预算|每人|一个人|一人)[^\d]{0,6}(\d+)",
        r"(\d+)\s*(?:块|元|/人)",
    ]
    for p in patterns:
        m = re.search(p, text or "")
        if m:
            return int(m.group(1))
    return None


def _parse_start_time(text: str) -> str | None:
    text = text or ""
    m = re.search(r"(\d{1,2})[:：](\d{2})", text)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"
    m = re.search(r"(\d{1,2})\s*点", text)
    if m:
        hour = int(m.group(1))
        if "下午" in text or "晚上" in text or "今晚" in text:
            if hour < 12:
                hour += 12
        return f"{hour:02d}:00"
    if "今晚" in text or "晚上" in text:
        return "19:00"
    if "下午" in text:
        return "14:00"
    if "中午" in text:
        return "12:00"
    return None


def _duration_minutes(text: str) -> int | None:
    m = re.search(r"(\d+)\s*(?:个)?小时", text or "")
    return int(m.group(1)) * 60 if m else None


def _transport(text: str) -> str:
    if _has(r"自驾|开车", text):
        return "self_drive"
    if _has(r"地铁|公交|公共交通|打车|步行", text):
        return "public"
    return "unknown"


def _diet_limits(text: str) -> list[str]:
    out: list[str] = []
    if _has(r"不吃辣|不能吃辣|不要辣|怕辣", text):
        out.append("no_spicy")
    if _has(r"不喝酒|不要酒|别有酒|不含酒|无酒", text):
        out.append("no_alcohol")
    if _has(r"清淡|轻食|胃不舒服", text):
        out.append("light_food")
    return out


def _negatives(text: str) -> list[str]:
    out: list[str] = []
    if _has(r"不想吃饭|不吃饭|不要吃饭|不安排吃饭", text):
        out.append("no_meal")
    if _has(r"不想出门|不出门|宅家|在家", text):
        out.append("no_outdoor")
    if _has(r"不冰|不能喝冰|不要冰|去冰|热的|热饮", text):
        out.append("no_ice")
    if _has(r"不要太甜|别太甜|少糖|低糖|无糖", text):
        out.append("not_too_sweet")
    if _has(r"不要咖啡因|不含咖啡因|无咖啡因", text):
        out.append("caffeine_free")
    if _has(r"不喝酒|不要酒|别有酒|不含酒|无酒", text):
        out.append("no_alcohol")
    return out


def _safety(text: str) -> list[str]:
    out = set(_diet_limits(text))
    if _has(r"孕妇|怀孕|生理期|姨妈|胃不舒服|身体不舒服", text):
        out.update({"body_uncomfortable", "cannot_ice", "not_too_sweet"})
    if _has(r"不冰|不能喝冰|不要冰|去冰|热的|热饮", text):
        out.add("cannot_ice")
    if _has(r"不要太甜|别太甜|少糖|低糖|无糖", text):
        out.add("not_too_sweet")
    if _has(r"孩子|小孩|亲子|宝宝", text):
        out.add("kid_safe")
    if _has(r"自驾|开车", text):
        out.add("no_alcohol")
    if _has(r"不要咖啡因|不含咖啡因|无咖啡因", text):
        out.add("caffeine_free")
    return sorted(out)


def _intent(text: str, parsed: dict[str, Any]) -> tuple[str, str, str, list[dict[str, Any]], str]:
    text = text or ""
    sequence: list[dict[str, Any]] = []
    negative = set(_negatives(text))
    if _is_home_delivery_text(text):
        sequence.extend(_stayin_sequence(text))
        return "clear", "stay_in", "STAYIN", sequence, "build_plan" if sequence else "ask_clarification"
    script_title_match = re.search(r"《([^》]{1,40})》", text)
    if script_title_match and _has(r"玩|剧本|本|打本|盒装|顺便", text):
        sequence.append({
            "role": "PLAY",
            "category": "剧本杀",
            "source": "explicit_text",
            "script_title": script_title_match.group(1).strip(),
        })

    if _has(r"睡会|睡觉|休息|躺会|什么都不想干|好累|好困", text) and not _has(r"酒店|按摩|足疗|SPA", text):
        return "rest_first", "rest", "REST", sequence, "rest_support"

    if _has(r"打本|打个本|剧本杀|剧本|盒装本|本子", text) and not any(x.get("category") == "剧本杀" for x in sequence):
        sequence.append({"role": "PLAY", "category": "剧本杀", "source": "explicit_text"})
    if _has(r"电影|影院", text):
        sequence.append({"role": "PLAY", "category": "电影院", "source": "explicit_text"})
    if _has(r"KTV|唱歌", text):
        sequence.append({"role": "PLAY", "category": "KTV", "source": "explicit_text"})
    if _has(r"台球|桌球", text):
        sequence.append({"role": "PLAY", "category": "台球", "source": "explicit_text"})
    if _has(r"密室", text):
        sequence.append({"role": "PLAY", "category": "密室", "source": "explicit_text"})
    if _has(r"按摩|足疗|SPA", text):
        sequence.append({"role": "PLAY", "category": "按摩", "source": "explicit_text"})
    if _has(r"酒店|订个酒店|休息一下", text):
        sequence.append({"role": "PLAY", "category": "酒店", "source": "explicit_text"})
    if _has(r"看展|展览", text):
        sequence.append({"role": "PLAY", "category": "展览", "source": "explicit_text"})
    if _has(r"citywalk|马鞍山|散步|逛街", text):
        sequence.append({"role": "PLAY", "category": "景区", "source": "explicit_text"})
    if _has(EAT_RE, text) and "no_meal" not in negative and not _is_home_delivery_text(text):
        cat = "火锅" if "火锅" in text else "海鲜" if "海鲜" in text else None
        if "烧烤" in text or "烤串" in text:
            cat = "烧烤"
        elif "江浙菜" in text or "炒菜" in text or "家常菜" in text:
            cat = "江浙菜"
        item = {"role": "EAT", "category": cat, "source": "explicit_text"}
        if _has(MEAL_BRIDGE_RE, text):
            item["meal_bridge_preference"] = True
        sequence.append(item)
    if _has(r"奶茶|咖啡(?!因)|喝点|饮品", text):
        cat = "咖啡" if re.search(r"咖啡(?!因)", text) else "奶茶"
        sequence.append({"role": "ADDON", "category": cat, "source": "explicit_text"})

    if _has(STAYIN_RE, text):
        sequence = _ordered_sequence(text, sequence)
        return "clear", "stay_in", "STAYIN", sequence, "build_plan" if sequence else "ask_clarification"
    if _has(r"约会|女朋友|男朋友|对象|浪漫", text):
        return "broad", "date", "PLAY", sequence, "ask_clarification"
    if _has(r"生日", text):
        return "clear", "birthday", "PLAY", sequence, "build_plan"
    if sequence:
        sequence = _ordered_sequence(text, sequence)
        first = sequence[0]
        if len(sequence) == 1 and first["role"] == "EAT" and first["category"] is None:
            return "broad", "food_discovery", "EAT", sequence, "ask_clarification"
        if len(sequence) == 1 and first["role"] == "PLAY" and first["category"] is None:
            return "broad", "outing", "PLAY", sequence, "show_category_choices"
        intent = {
            "剧本杀": "script_game",
            "电影院": "movie",
            "KTV": "outing",
            "台球": "billiards",
            "密室": "outing",
            "按摩": "massage",
            "展览": "outing",
            "citywalk": "景区",
            "酒店": "hotel",
            "火锅": "hotpot",
            "海鲜": "seafood",
            "奶茶": "milk_tea",
            "咖啡": "coffee",
        }.get(first.get("category"), "outing")
        return "clear", intent, first["role"], sequence, "build_plan"
    if _has(r"出去玩|出门玩|聚会|同学|朋友|同事", text):
        return "broad", "outing", "PLAY", sequence, "show_category_choices"
    if _has(r"吃点什么|随便吃点|今晚吃饭|附近.*好吃", text):
        return "broad", "food_discovery", "EAT", sequence, "ask_clarification"
    return "ambiguous", "unknown", "UNKNOWN", sequence, "ask_clarification"


def build_intent_frame(raw_text: str, parsed: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = parsed or {}
    raw_text = raw_text or ""
    status, primary, role, sequence, action = _intent(raw_text, parsed)

    party = _parse_party(raw_text)
    start = _parse_start_time(raw_text)
    duration = _duration_minutes(raw_text)
    area = _first_area(raw_text)
    budget = _parse_budget(raw_text)
    transport = _transport(raw_text)
    occasion = "约会" if primary == "date" else "生日" if primary == "birthday" else None
    negatives = set(_negatives(raw_text))
    cuisine, cuisine_source = _cuisine_preference(raw_text, role, sequence, negatives)
    dine_mode, dine_source, dine_assumption = _dine_mode(raw_text, role, sequence, negatives)
    home_area_source = "explicit_text" if area is not None else "unknown"
    if primary == "stay_in" and area is None:
        area = "线上"
        home_area_source = "planning_default"

    confirmed = {
        "party_size": party,
        "start_time": start,
        "end_time": None,
        "duration_minutes": duration,
        "home_area": area,
        "friend_areas": [],
        "budget_per_person": budget,
        "transport": transport,
        "dine_mode": dine_mode,
        "cuisine_preference": cuisine,
        "diet_limits": _diet_limits(raw_text),
        "occasion": occasion,
    }
    sources = {
        "party_size": "explicit_text" if party is not None else "unknown",
        "start_time": "explicit_text" if start is not None else "unknown",
        "home_area": home_area_source,
        "budget_per_person": "explicit_text" if budget is not None else "unknown",
        "transport": "explicit_text" if transport != "unknown" else "unknown",
        "dine_mode": dine_source,
        "cuisine_preference": cuisine_source,
    }

    unknown = [k for k, v in confirmed.items() if v in (None, [], "unknown") and k in {
        "party_size", "start_time", "duration_minutes", "home_area", "budget_per_person", "transport"
    }]
    if primary == "stay_in":
        unknown = [k for k in unknown if k not in ("home_area", "transport")]
    if cuisine not in (None, "", "unknown"):
        unknown = [k for k in unknown if k != "cuisine_preference"]
    if dine_mode not in (None, "", "unknown"):
        unknown = [k for k in unknown if k != "dine_mode"]
    if primary == "food_discovery":
        required_food_fields = {"party_size", "start_time", "home_area", "budget_per_person"}
        action = "ask_clarification" if required_food_fields & set(unknown) else "build_plan"
    elif primary == "date" and action == "build_plan":
        action = "ask_clarification"
    if primary == "date" and all(k not in unknown for k in ("start_time", "home_area", "budget_per_person")) and _has(r"看电影|电影|拍照|出片|散步|citywalk|展览|看展|吃饭|甜品|不想太累|别太累", raw_text):
        action = "build_plan"
    if primary == "outing" and status == "broad":
        action = "show_category_choices"
    if status == "rest_first":
        action = "rest_support"

    return {
        "raw_text": raw_text,
        "intent_status": status,
        "primary_intent": primary,
        "main_role": role,
        "sequence": sequence,
        "confirmed_fields": confirmed,
        "field_sources": sources,
        "unknown_fields": unknown,
        "assumptions": {"dine_mode": dine_assumption} if dine_assumption else {},
        "negative_intents": list(negatives),
        "safety_flags": _safety(raw_text),
        "confidence": 0.9 if status == "clear" else 0.62 if status == "broad" else 0.35,
        "next_action": action,
        "goal_summary": make_goal_summary(primary, sequence, confirmed),
    }


def make_goal_summary(primary: str, sequence: list[dict[str, Any]], confirmed: dict[str, Any]) -> str:
    if primary == "stay_in":
        return "宅家休息和外卖补给"
    if primary == "birthday":
        return "朋友生日仪式感安排"
    elif primary == "food_discovery":
        return "想找点吃的"
    if primary == "rest":
        return "想先休息一下"
    if primary == "outing":
        return "想出门玩，但还没确定活动类型"
    if primary == "date":
        return "想安排一次约会"
    if primary == "drink":
        return f"想喝{sequence[0]['category'] if sequence else '饮品'}"
    if sequence:
        labels = [x["category"] or ("吃饭" if x["role"] == "EAT" else "活动") for x in sequence]
        return "，再".join(labels)
    return "还需要确认目标"


def clarification_questions(frame: dict[str, Any]) -> list[dict[str, Any]]:
    primary = frame.get("primary_intent")
    unknown = set(frame.get("unknown_fields") or [])
    raw_text = frame.get("raw_text") or ""
    questions: list[dict[str, Any]] = []

    def add(key: str, question: str, options: list[dict[str, Any]], multi: bool = False):
        question_payload = {"key": key, "field": key, "question": question, "type": "chip", "options": options}
        if multi:
            question_payload["multi"] = True
        questions.append(question_payload)

    if frame.get("next_action") == "show_category_choices":
        add("activity_choice", "先选一个或多个活动方向？", [
            {"label": "剧本杀", "value": "剧本杀"},
            {"label": "KTV", "value": "KTV"},
            {"label": "台球", "value": "台球"},
            {"label": "密室", "value": "密室"},
            {"label": "电影", "value": "电影院"},
            {"label": "桌游", "value": "桌游"},
            {"label": "其他", "value": "其他"},
        ], multi=True)
        return questions
    if frame.get("next_action") == "rest_support":
        add("at_home_or_outside", "你现在更想怎么休息？", [
            {"label": "在家睡会", "value": "home_rest"},
            {"label": "在外面找地方歇歇", "value": "outside_rest"},
            {"label": "打车回家", "value": "taxi_home"},
            {"label": "按摩放松", "value": "massage"},
        ])
        return questions

    if primary == "stay_in":
        for key, question in [
            ("start_time", "\u5927\u6982\u4ec0\u4e48\u65f6\u5019\u5f00\u59cb\uff1f"),
            ("duration_minutes", "\u5927\u6982\u653e\u677e\u591a\u4e45\uff1f"),
            ("budget_per_person", "\u5927\u6982\u9884\u7b97\uff1f"),
        ]:
            if key in unknown:
                add(key, question, _default_options(key))
        if not frame.get("sequence"):
            add("stayin_mode", "\u5b85\u5bb6\u60f3\u600e\u4e48\u6d88\u78e8\uff1f", [
                {"label": "\u7535\u5f71 + \u5916\u5356", "value": "movie_takeaway"},
                {"label": "\u8ffd\u5267 + \u96f6\u98df", "value": "movie_snacks"},
                {"label": "\u53ea\u60f3\u70b9\u5403\u7684", "value": "takeaway_only"},
            ])
    elif primary == "food_discovery":
        sources = frame.get("field_sources") or {}
        confirmed = frame.get("confirmed_fields") or {}
        if confirmed.get("dine_mode") in (None, "", "unknown"):
            add("dine_mode", "想怎么吃？", [
                {"label": "到店吃", "value": "eat_in"},
                {"label": "点外卖", "value": "delivery"},
                {"label": "都可以", "value": "either"},
            ])
        if "home_area" in unknown:
            add("home_area", "在哪附近？", [{"label": x, "value": x} for x in ["新街口", "老门东", "河西"]])
        if "start_time" in unknown:
            add("start_time", "大概几点？", _default_options("start_time"))
        if "budget_per_person" in unknown:
            add("budget_per_person", "人均预算？", _default_options("budget_per_person"))
        if confirmed.get("cuisine_preference") in (None, "", "unknown"):
            add("cuisine_preference", "更想吃哪类？", [{"label": x, "value": x} for x in ["火锅", "江浙菜", "烧烤", "海鲜", "简餐", "都可以"]], multi=True)
    elif primary == "date":
        for key, question in [("start_time", "什么时候开始？"), ("home_area", "优先哪个区域？"), ("budget_per_person", "人均预算？")]:
            if key in unknown:
                add(key, question, _default_options(key))
        add("date_preferences", "这次约会更想包含什么？", [
            {"label": "看电影", "value": "看电影"},
            {"label": "拍照", "value": "拍照"},
            {"label": "散步", "value": "散步"},
            {"label": "吃饭", "value": "吃饭"},
            {"label": "甜品", "value": "甜品"},
            {"label": "轻松聊天", "value": "轻松聊天"},
            {"label": "不太累", "value": "不太累"},
        ], multi=True)
        if not _has(r"浪漫|安静|出片|轻松|惊喜|不想太累|别太累", raw_text):
            add("style", "约会风格？", [{"label": x, "value": x} for x in ["浪漫", "安静", "出片", "轻松", "惊喜"]], multi=True)
    else:
        for key in ["party_size", "start_time", "duration_minutes", "home_area", "budget_per_person"]:
            if key in unknown:
                add(key, _default_question(key), _default_options(key))
    return questions[:5]


def _default_question(key: str) -> str:
    return {
        "party_size": "一共几个人？",
        "start_time": "大概几点开始？",
        "duration_minutes": "大概玩多久？",
        "home_area": "优先哪个区域？",
        "budget_per_person": "人均预算？",
    }.get(key, key)


def _default_options(key: str) -> list[dict[str, Any]]:
    return {
        "party_size": [{"label": x, "value": v} for x, v in [("2人", 2), ("4人", 4), ("6人", 6)]],
        "start_time": [{"label": x, "value": v} for x, v in [("今天14:00", "14:00"), ("今天18:00", "18:00"), ("今晚19:30", "19:30")]],
        "duration_minutes": [{"label": x, "value": v} for x, v in [("2小时", 120), ("4小时", 240), ("6小时", 360)]],
        "home_area": [{"label": x, "value": x} for x in ["新街口", "老门东", "河西"]],
        "budget_per_person": [{"label": x, "value": v} for x, v in [("100以内", 100), ("150", 150), ("300", 300)]],
    }.get(key, [])
