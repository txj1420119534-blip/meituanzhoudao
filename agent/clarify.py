"""
clarify.py —— 根据场景/品类决定“该让用户补什么”。

原则：
- LLM/关键词只负责把用户一句话打标。
- Python 用可解释的产品规则生成问题，最多 5 个，保证一屏内完成。
- 只问“规划必须知道”的信息；饭后奶茶、散场小吃这类商业推荐直接放进方案里。
"""
from __future__ import annotations

import re

from agent.category_schema import (
    has_area,
    has_budget,
    has_duration,
    has_exact_start_time,
    has_party_size,
    UNLIMITED,
)


AREA_OPTIONS = ["新街口", "老门东", "河西", "夫子庙", "鼓楼", "玄武湖", "江宁", "仙林", "百家湖", "奥体", "马鞍山"]


QUESTION_BANK = {
    "party_size": {
        "question": "一共几个人？",
        "type": "chip",
        "options": [
            {"label": "2 人", "value": 2},
            {"label": "3 人", "value": 3},
            {"label": "4 人", "value": 4},
            {"label": "5 人", "value": 5},
            {"label": "6 人", "value": 6},
            {"label": "7 人+", "value": 7},
        ],
    },
    "script_party_size": {
        "question": "剧本杀几个人上车？",
        "type": "chip",
        "options": [
            {"label": "4 人", "value": 4},
            {"label": "5 人", "value": 5},
            {"label": "6 人", "value": 6},
            {"label": "7 人", "value": 7},
        ],
    },
    "budget_per_person": {
        "question": "人均预算？",
        "type": "chip",
        "options": [
            {"label": "¥80 以内", "value": 80},
            {"label": "¥120", "value": 120},
            {"label": "¥150", "value": 150},
            {"label": "¥200", "value": 200},
            {"label": "¥300+", "value": 300},
        ],
    },
    "start_time": {
        "question": "大概几点开始？",
        "type": "chip",
        "options": [
            {"label": "今天 14:00", "value": "14:00"},
            {"label": "今天 15:00", "value": "15:00"},
            {"label": "今天 18:00", "value": "18:00"},
            {"label": "今晚 19:30", "value": "19:30"},
        ],
    },
    "window_hours": {
        "question": "这局大概留多久？",
        "type": "chip",
        "options": [
            {"label": "2 小时", "value": 2},
            {"label": "3 小时", "value": 3},
            {"label": "4 小时", "value": 4},
            {"label": "5 小时+", "value": 6},
        ],
    },
    "script_style": {
        "question": "想玩什么类型的本？",
        "type": "chip",
        "multi": True,
        "options": [
            {"label": "欢乐本", "value": "欢乐本"},
            {"label": "推理本", "value": "推理本"},
            {"label": "机制本", "value": "机制本"},
            {"label": "情感本", "value": "情感本"},
            {"label": "恐怖本", "value": "恐怖本"},
            {"label": "都可以", "value": "不限"},
        ],
    },
    "home_area": {
        "question": "优先从哪片区域开始？",
        "type": "chip",
        "options": [{"label": area, "value": area} for area in AREA_OPTIONS],
    },
    "origin_mode": {
        "question": "大家从哪出发？",
        "type": "chip",
        "options": [
            {"label": "都在一起", "value": "together"},
            {"label": "各自过去", "value": "separate"},
            {"label": "按我位置", "value": "organizer_area"},
        ],
    },
    "distance_tolerance": {
        "question": "距离怎么控制？",
        "type": "chip",
        "options": [
            {"label": "附近就好", "value": "nearby"},
            {"label": "同商圈优先", "value": "same_area"},
            {"label": "好店可跑远", "value": "food_first"},
            {"label": "都可以", "value": "flexible"},
        ],
    },
    "cuisine_preference": {
        "question": "更想吃哪类？",
        "type": "chip",
        "options": [
            {"label": "海鲜", "value": "海鲜"},
            {"label": "江浙菜/炒菜", "value": "江浙菜"},
            {"label": "火锅", "value": "火锅"},
            {"label": "烧烤", "value": "烧烤"},
            {"label": "简餐轻食", "value": "简餐"},
            {"label": "都可以", "value": "不限"},
        ],
    },
    "diet_limits": {
        "question": "有忌口吗？",
        "type": "chip",
        "options": [
            {"label": "无明显忌口", "value": "none"},
            {"label": "不吃辣", "value": "no_spicy"},
            {"label": "不喝酒", "value": "no_alcohol"},
            {"label": "清淡一点", "value": "light_food"},
        ],
    },
    "stayin_mode": {
        "question": "宅家想怎么消磨？",
        "type": "chip",
        "options": [
            {"label": "电影 + 外卖", "value": "movie_takeaway"},
            {"label": "追剧 + 零食", "value": "movie_snacks"},
            {"label": "只想囤零食", "value": "snacks_only"},
            {"label": "都可以", "value": "relax_any"},
        ],
    },
    "date_meal": {
        "question": "这次要不要顺便安排吃饭？",
        "type": "chip",
        "options": [
            {"label": "安排吃饭", "value": "yes"},
            {"label": "先不安排", "value": "no"},
            {"label": "只放可选推荐", "value": "optional"},
        ],
    },
    "experience_mode": {
        "question": "你更想哪种方式？",
        "type": "chip",
        "options": [
            {"label": "宅家在线看", "value": "stay_in_online"},
            {"label": "出门去影院", "value": "cinema_out"},
        ],
    },
}


def decide_clarifications(text: str, request: dict, explicit_cats: list[dict], max_questions: int = 5) -> list[dict]:
    text = text or ""
    scene = request.get("scene", "friends_out")
    main_role = request.get("main_role")
    primary_intent = request.get("primary_intent")
    roles = {c.get("role") for c in explicit_cats}
    cats = {c.get("category") for c in explicit_cats}
    intent_tags = set(request.get("intent_tags", []) or [])

    if request.get("intent_conflict"):
        return _materialize(["experience_mode"])

    is_script = "剧本杀" in cats or "script_game" in intent_tags
    is_heavy_play = is_script or any(c in cats for c in ("密室", "KTV"))
    is_food_only = scene == "food_only"
    is_dinner = is_food_only or "dinner" in intent_tags or "EAT" in roles
    is_stayin = scene == "stay_in"
    romantic = bool(re.search(r"约会|女朋友|男朋友|对象|情侣|纪念日|生日|仪式感", text))
    no_meal = "no_meal" in (request.get("negative_intents") or [])

    ordered_keys: list[str] = []

    def want(key: str, condition: bool = True):
        if condition and key not in ordered_keys:
            ordered_keys.append(key)

    if main_role == "ADDON" or primary_intent in ("milk_tea", "coffee", "addon_single") or scene == "addon_only":
        want("start_time", not has_exact_start_time(text))
        want("home_area", not has_area(text))
        return _materialize(ordered_keys[:2])

    if primary_intent == "movie" and "no_meal" in (request.get("negative_intents") or []):
        want("start_time", not has_exact_start_time(text))
        want("home_area", not has_area(text))
        return _materialize(ordered_keys[:2])

    if is_stayin:
        want("start_time", not (has_exact_start_time(text) or request.get("start_time")))
        want("budget_per_person", not has_budget(text))
        want("stayin_mode", not request.get("stayin_mode") and not any(c.get("role") == "STAYIN" for c in explicit_cats))
        return _materialize(ordered_keys[:max_questions])

    if is_script:
        want("script_party_size", not has_party_size(text))
        want("start_time", not has_exact_start_time(text))
        want("budget_per_person", not has_budget(text))
        want("script_style", _is_blank(request.get("script_style")))
        want("window_hours", not has_duration(text))
        want("home_area", not has_area(text))
        return _materialize(ordered_keys[:max(max_questions, 6)])

    if is_dinner:
        want("party_size", not has_party_size(text))
        want("start_time", not has_exact_start_time(text))
        want("budget_per_person", not has_budget(text))
        want("home_area", not has_area(text))
        want("distance_tolerance", not has_area(text) and _is_blank(request.get("distance_tolerance")))
        want("cuisine_preference", _is_blank(request.get("cuisine_preference")))
        # 忌口不是所有饭局必问；如果用户没给菜系，先问菜系。如果菜系已明确，再补忌口。
        specific_cuisine = request.get("cuisine_preference") not in (None, "", "any", "都可以", "不限", "随便")
        want("diet_limits", specific_cuisine and not request.get("diet_limits") and not _has_no_diet_text(text))
        return _materialize(ordered_keys[:max_questions])

    # 泛娱乐场景：不要问商业增值项，只补规划必须知道的核心字段。
    want("date_meal", romantic and not is_dinner and not no_meal)
    want("party_size", not has_party_size(text))
    want("start_time", not has_exact_start_time(text))
    want("budget_per_person", not has_budget(text))
    want("home_area", not has_area(text))
    want("distance_tolerance", _is_blank(request.get("distance_tolerance")))
    want("window_hours", is_heavy_play and not has_duration(text))
    return _materialize(ordered_keys[:max_questions])


def _materialize(keys: list[str]) -> list[dict]:
    out = []
    for key in keys:
        q = dict(QUESTION_BANK[key])
        real_key = "party_size" if key == "script_party_size" else key
        q["key"] = real_key
        q["field"] = real_key
        out.append(q)
    return out


def _is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set)):
        return len(value) == 0
    return False


def _has_no_diet_text(text: str) -> bool:
    return bool(re.search(r"无忌口|没有忌口|没忌口|都能吃|不挑食", text or ""))
