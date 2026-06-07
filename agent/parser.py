"""
parser.py —— 一句话 → 结构化需求 request。
三层兜底永不崩：① LLM ② 关键词规则 ③ samples.json 第一条。
还会做两件事：
  - 抽取「明确品类」（如 剧本杀 / 火锅）→ planner 用它锁定槽位
  - 检测「需要追问」（如 没说人数/预算）→ core 走追问中转，不直接出方案
"""
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.semantic import analyze_semantics, has_intent
from agent.category_schema import (
    extract_domain_signals,
    first_area,
    has_budget,
    has_exact_start_time,
    has_party_size,
    parse_budget,
    parse_coarse_start_time,
    parse_party_size,
)
from agent.clarify import decide_clarifications
from agent.intent_frame import build_intent_frame, clarification_questions

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

VALID_SCENES = {"friends_out", "play_only", "family_out", "stay_in", "couple", "food_only", "addon_only"}
STAY_IN_RE = r"宅家|在家|不想出门|不想出去|不出门|待着|呆着|躺着"
FOOD_INTENT_RE = (
    r"吃饭|吃点|吃个|聚餐|餐厅|晚饭|午饭|正餐|美食|外卖|夜宵|"
    r"海鲜|火锅|烧烤|烤串|炒菜|家常菜|江浙菜|简餐|西餐|面馆|吃面|甜品|蛋糕|奶茶|咖啡"
)
NO_MEAL_RE = r"不想吃饭|不吃饭|不要吃饭|不安排吃饭|不吃餐|不要餐厅|别安排吃的|不想吃东西"
NO_OUTDOOR_RE = r"不想出门|不出门|不想出去|在家|宅家"
NO_ICE_RE = r"不能喝冰|不能冰|不要冰|不加冰|去冰|别冰|喝热的|热饮|温热"
NOT_TOO_SWEET_RE = r"不要太甜|别太甜|不太甜|少糖|低糖|半糖|三分糖|无糖"
BODY_UNCOMFORTABLE_RE = r"生理期|姨妈|来例假|肚子不舒服|胃不舒服|身体不舒服|感冒|不舒服"
NO_ALCOHOL_RE = r"别有酒|不要酒|不喝酒|不能喝酒|不要喝酒|无酒精|别推荐酒|不含酒"
CAFFEINE_FREE_RE = r"不要咖啡因|不含咖啡因|不能有咖啡因|无咖啡因|低咖啡因"
HOME_DELIVERY_RE = r"在家吃|宅家吃|不想出门吃|不出门吃|外卖|点外卖|送到家|小象|闪购|零食"
CUISINE_ANY_RE = r"菜系都可以|菜系不限|吃什么都行|随便吃点|随便吃|不挑|都可以"


# ─────────────────────────────────────────────────────────────────────
# 明确品类 关键词 → (槽位 role, 商户库 category)
# 用户原话提到这些词，agent 必须把对应槽位锁定到该品类
# ─────────────────────────────────────────────────────────────────────
EXPLICIT_KEYWORDS = [
    # PLAY
    ("剧本杀",   "PLAY",   "剧本杀"),
    ("恐怖本",   "PLAY",   "剧本杀"),
    ("欢乐本",   "PLAY",   "剧本杀"),
    ("盒装本",   "PLAY",   "剧本杀"),
    ("欢乐盒装本", "PLAY", "剧本杀"),
    ("打个本",   "PLAY",   "剧本杀"),
    ("打本",     "PLAY",   "剧本杀"),
    ("约本",     "PLAY",   "剧本杀"),
    ("推本",     "PLAY",   "剧本杀"),
    ("本子",     "PLAY",   "剧本杀"),
    ("剧本",     "PLAY",   "剧本杀"),
    ("密室",     "PLAY",   "密室"),
    ("电影院",   "PLAY",   "电影院"),
    ("看电影",   "PLAY",   "电影院"),
    ("电影",     "PLAY",   "电影院"),
    ("KTV",      "PLAY",   "KTV"),
    ("ktv",      "PLAY",   "KTV"),
    ("唱歌",     "PLAY",   "KTV"),
    ("唱K",      "PLAY",   "KTV"),
    ("台球",     "PLAY",   "台球"),
    ("桌球",     "PLAY",   "台球"),
    ("按摩",     "PLAY",   "按摩"),
    ("足疗",     "PLAY",   "按摩"),
    ("SPA",      "PLAY",   "按摩"),
    ("spa",      "PLAY",   "按摩"),
    ("马鞍山",   "PLAY",   "景区"),
    ("citywalk", "PLAY",  "景区"),
    ("Citywalk", "PLAY",  "景区"),
    ("酒店",     "PLAY",   "酒店"),
    ("订个酒店", "PLAY",   "酒店"),
    ("桌游",     "PLAY",   "桌游"),
    ("看展",     "PLAY",   "展览"),
    ("展览",     "PLAY",   "展览"),
    ("手作",     "PLAY",   "手作"),
    ("陶艺",     "PLAY",   "手作"),
    ("市集",     "PLAY",   "市集"),
    ("滑冰",     "PLAY",   "运动"),
    ("骑行",     "PLAY",   "户外运动"),
    ("亲子乐园", "PLAY",   "亲子乐园"),
    # EAT
    ("火锅",     "EAT",    "火锅"),
    ("烧烤",     "EAT",    "烧烤"),
    ("烤串",     "EAT",    "烧烤"),
    ("撸串",     "EAT",    "烧烤"),
    ("西餐",     "EAT",    "西餐"),
    ("牛排",     "EAT",    "西餐"),
    ("意面",     "EAT",    "西餐"),
    ("海鲜",     "EAT",    "海鲜"),
    ("河鲜",     "EAT",    "海鲜"),
    ("江浙菜",   "EAT",    "江浙菜"),
    ("炒菜",     "EAT",    "江浙菜"),
    ("家常菜",   "EAT",    "江浙菜"),
    ("面馆",     "EAT",    "本地面食"),
    ("吃面",     "EAT",    "本地面食"),
    ("简餐",     "EAT",    "简餐"),
    ("沙拉",     "EAT",    "简餐"),
    ("融合菜",   "EAT",    "融合菜"),
    # STAYIN
    ("在线电影", "STAYIN", "在线电影"),
    ("追剧",     "STAYIN", "在线电影"),
    ("在家看",   "STAYIN", "在线电影"),
    ("看剧",     "STAYIN", "在线电影"),
    ("点外卖",   "STAYIN", "外卖"),
    ("外卖",     "STAYIN", "外卖"),
    ("闪购",     "STAYIN", "闪购零食"),
    # ADDON
    ("奶茶",     "ADDON",  "奶茶"),
    ("咖啡",     "ADDON",  "咖啡"),
    ("蛋糕鲜花", "ADDON",  "蛋糕鲜花"),
    ("蛋糕",     "ADDON",  "蛋糕鲜花"),
    ("鲜花",     "ADDON",  "蛋糕鲜花"),
    ("甜品",     "ADDON",  "甜品"),
    ("酒吧",     "ADDON",  "酒吧"),
    ("精酿",     "ADDON",  "酒吧"),
    ("冰淇淋",   "ADDON",  "冰淇淋"),
]

# 同一商户库 category 在多个关键词上都能命中时，去重保留首次出现的（按 EXPLICIT_KEYWORDS 顺序）


def _merge_unique(values: list[str]) -> list[str]:
    out = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


def _dedupe_categories(values: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for item in values:
        key = (item["role"], item["category"])
        if key in seen:
            continue
        out.append(item)
        seen.add(key)
    return out


def _remove_negated_categories(text: str, categories: list[dict]) -> list[dict]:
    """Do not let phrases like "不想吃饭" become a positive EAT category."""
    if not re.search(NO_MEAL_RE, text or ""):
        return categories
    return [item for item in categories if item.get("role") != "EAT"]


def _extract_script_title(text: str) -> str | None:
    m = re.search(r"《([^》]{1,40})》", text or "")
    if m and re.search(r"玩|剧本|本|打本|盒装", text or ""):
        return m.group(1).strip()
    return None


def _extract_explicit_categories(text: str, semantic: dict | None = None) -> list[dict]:
    """从原话扫描，返回 [{"role":"PLAY","category":"剧本杀","keyword":"剧本杀"}, ...]。"""
    found: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for kw, role, cat in EXPLICIT_KEYWORDS:
        if kw not in text:
            continue
        real_role, real_cat = role, cat
        if kw in ("看电影", "电影") and _has_stay_in_intent(text):
            real_role, real_cat = "STAYIN", "在线电影"
        if (real_role, real_cat) not in seen:
            # "看电影"在出门局是电影院；在宅家/不出门语境里应锁到在线电影。
            found.append({"role": real_role, "category": real_cat, "keyword": kw})
            seen.add((real_role, real_cat))
    if semantic:
        found.extend(semantic.get("explicit_categories", []) or [])
    return _dedupe_categories(found)


def _has_stay_in_intent(text: str) -> bool:
    return bool(re.search(STAY_IN_RE, text) or
                has_intent(text, "stay_home") or
                (has_intent(text, "low_energy") and has_intent(text, "casual_play")))


def _has_party_size(text: str) -> bool:
    return has_party_size(text)


def _has_budget(text: str) -> bool:
    return has_budget(text)


def _has_start_time(text: str) -> bool:
    return has_exact_start_time(text)


def _has_food_intent(text: str, explicit_cats: list[dict] | None = None) -> bool:
    """只有用户真的提到餐饮/外卖/饮品时，才把“吃喝”当作需求。"""
    if re.search(FOOD_INTENT_RE, text or ""):
        return True
    for item in explicit_cats or []:
        if item.get("role") in ("EAT", "ADDON"):
            return True
        if item.get("role") == "STAYIN" and item.get("category") in ("外卖", "闪购零食"):
            return True
    return False


def _role_bucket(explicit_cats: list[dict]) -> dict[str, list[str]]:
    bucket = {"PLAY": [], "EAT": [], "STAYIN": [], "ADDON": []}
    for item in explicit_cats or []:
        role = item.get("role")
        cat = item.get("category")
        if role in bucket and cat and cat not in bucket[role]:
            bucket[role].append(cat)
    return bucket


def _derive_primary_intent(text: str, result: dict, explicit_cats: list[dict], semantic: dict) -> tuple[str, str]:
    cats = _role_bucket(explicit_cats)
    tags = set(semantic.get("intent_tags", []) or [])
    if cats["ADDON"] and not cats["PLAY"] and not cats["EAT"] and result.get("scene") != "stay_in":
        cat = cats["ADDON"][0]
        if cat == "奶茶":
            return "milk_tea", "ADDON"
        if cat == "咖啡":
            return "coffee", "ADDON"
        return "addon_single", "ADDON"
    if "生日" in text or "birthday" in tags:
        return "birthday", "PLAY"
    if cats["EAT"]:
        cat = cats["EAT"][0]
        return {
            "火锅": "hotpot",
            "海鲜": "seafood",
            "烧烤": "bbq",
            "江浙菜": "jiangzhe_food",
            "简餐": "light_meal",
        }.get(cat, "food"), "EAT"
    if cats["PLAY"]:
        cat = cats["PLAY"][0]
        return {
            "剧本杀": "script_game",
            "电影院": "movie",
            "密室": "escape_room",
            "桌游": "board_game",
            "KTV": "ktv",
            "台球": "billiards",
            "按摩": "massage",
            "citywalk": "景区",
            "酒店": "hotel",
        }.get(cat, "play"), "PLAY"
    if result.get("scene") == "stay_in":
        return "stay_in", "STAYIN"
    if result.get("scene") == "food_only":
        return "food", "EAT"
    return "weekend_plan", "PLAY"


def _derive_negative_intents(text: str) -> list[str]:
    out: list[str] = []
    if re.search(NO_MEAL_RE, text):
        out.append("no_meal")
    if re.search(NO_OUTDOOR_RE, text):
        out.append("no_outdoor")
    if re.search(NO_ICE_RE, text):
        out.append("no_ice")
    if re.search(NOT_TOO_SWEET_RE, text):
        out.append("not_too_sweet")
    if re.search(NO_ALCOHOL_RE, text):
        out.append("no_alcohol")
    if re.search(CAFFEINE_FREE_RE, text):
        out.append("caffeine_free")
    return out


def _derive_safety_flags(text: str, result: dict) -> list[str]:
    flags = set(result.get("diet_limits", []) or [])
    if re.search(NO_ICE_RE, text):
        flags.add("cannot_ice")
    if re.search(NOT_TOO_SWEET_RE, text):
        flags.add("not_too_sweet")
    if re.search(BODY_UNCOMFORTABLE_RE, text):
        flags.add("body_uncomfortable")
        flags.add("cannot_ice")
    if re.search(NO_ALCOHOL_RE, text):
        flags.add("no_alcohol")
    if re.search(CAFFEINE_FREE_RE, text):
        flags.add("caffeine_free")
    if result.get("has_kid"):
        flags.add("kid_safe")
    if result.get("transport") == "self_drive":
        flags.add("drive_safe")
        if re.search(r"喝点|喝酒|小酒|酒吧|精酿|啤酒", text or ""):
            flags.add("no_alcohol")
    return _merge_unique(list(flags))


def _derive_drink_preferences(text: str, safety_flags: list[str]) -> dict:
    sugar = None
    if "无糖" in text:
        sugar = "zero"
    elif re.search(r"三分糖|少糖|低糖|半糖|不要太甜|别太甜|不太甜", text):
        sugar = "low"
    ice = None
    if re.search(r"热饮|喝热的|热的|温热|生理期|姨妈|来例假", text):
        ice = "hot"
    elif re.search(r"常温", text):
        ice = "room"
    elif re.search(r"去冰|不加冰|不能喝冰|不能冰|不要冰|别冰", text):
        ice = "no_ice"
    return {
        "sugar_level": sugar,
        "ice_level": ice,
        "hot_required": bool(ice == "hot" or "body_uncomfortable" in safety_flags or "cannot_ice" in safety_flags),
    }


def _apply_intent_fields(text: str, result: dict, explicit_cats: list[dict], semantic: dict) -> None:
    if re.search(HOME_DELIVERY_RE, text or ""):
        if not any(c.get("role") == "STAYIN" and c.get("category") == "外卖" for c in explicit_cats) and re.search(r"外卖|在家吃|宅家吃|吃点|正餐|晚饭|午饭", text or ""):
            explicit_cats.append({"role": "STAYIN", "category": "外卖", "keyword": "宅家配送"})
        if not any(c.get("role") == "STAYIN" and c.get("category") == "闪购零食" for c in explicit_cats) and re.search(r"零食|小象|闪购|饮料", text or ""):
            explicit_cats.append({"role": "STAYIN", "category": "闪购零食", "keyword": "宅家配送"})
    buckets = _role_bucket(explicit_cats)
    result["requested_categories"] = _merge_unique([c.get("category") for c in explicit_cats if c.get("category")])
    negative = _derive_negative_intents(text)
    result["negative_intents"] = negative
    result["safety_flags"] = _derive_safety_flags(text, result)
    result["drink_preferences"] = _derive_drink_preferences(text, result["safety_flags"])
    primary, main_role = _derive_primary_intent(text, result, explicit_cats, semantic)
    result["primary_intent"] = primary
    result["main_role"] = main_role

    if main_role == "ADDON" and buckets["ADDON"] and not buckets["PLAY"] and not buckets["EAT"] and result.get("scene") != "stay_in":
        result["scene"] = "addon_only"
        result["party_size"] = 1
        result["preferences"] = [p for p in (result.get("preferences") or []) if p not in ("good_food", "easy_pace")]
    if buckets["STAYIN"] or re.search(HOME_DELIVERY_RE, text or ""):
        result["scene"] = "stay_in"
        result["primary_intent"] = "stay_in"
        result["main_role"] = "STAYIN"
        result["home_area"] = "线上"
        result["dine_mode"] = "delivery"
    if buckets["EAT"] and not buckets["PLAY"] and "no_meal" not in negative:
        result["scene"] = "food_only"
    if re.search(CUISINE_ANY_RE, text or "") and (buckets["EAT"] or result.get("scene") == "food_only" or re.search(r"吃|餐|菜系|美食", text or "")):
        result["cuisine_preference"] = "any"
    if buckets["PLAY"] and not buckets["EAT"] and "no_meal" in negative:
        result["scene"] = "play_only"

    if primary in ("milk_tea", "coffee"):
        result["window_hours"] = min(int(result.get("window_hours", 1) or 1), 1)

    tags = set(semantic.get("intent_tags", []) or [])
    if "newbie" in tags:
        result["newbie"] = True
    if result.get("transport") == "self_drive" and "no_alcohol" in result.get("safety_flags", []):
        diet = set(result.get("diet_limits", []) or [])
        diet.add("no_alcohol")
        result["diet_limits"] = _merge_unique(list(diet))
    if re.search(NO_OUTDOOR_RE, text or "") and re.search(r"影院|电影院|去.*电影", text or ""):
        result["intent_conflict"] = "stay_in_vs_cinema"
        result["confidence"] = 0.35
        result["clarification_hint"] = "你是想宅家在线看，还是出门去影院？"
        return

    confidence = 0.92 if explicit_cats else 0.72
    if result.get("_parse_method") == "llm":
        confidence += 0.03
    if negative:
        confidence += 0.02
    if not text or not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", text):
        confidence = 0.25
    elif not explicit_cats and not semantic.get("intent_tags"):
        confidence = 0.4
    result["confidence"] = min(0.98, confidence)


def _sanitize_preferences_by_scene(text: str, result: dict, explicit_cats: list[dict]) -> None:
    """
    LLM 和默认规则容易把“朋友出门”泛化成“吃好喝好”。
    但电影/看展/手作这类单活动场景，只有原话出现餐饮意图时才保留餐饮偏好。
    """
    prefs = list(result.get("preferences", []) or [])
    if not prefs:
        return

    food_needed = (
        result.get("scene") in ("food_only", "stay_in")
        or _has_food_intent(text, explicit_cats)
        or any(c.get("role") == "EAT" for c in explicit_cats)
    )
    if not food_needed:
        prefs = [p for p in prefs if p not in ("good_food", "light_food")]

    result["preferences"] = _merge_unique(prefs)


def _normalize_request_by_text(text: str, result: dict, rule: dict, semantic: dict) -> dict:
    """
    LLM 可以帮忙理解自然语言，但强业务意图必须由规则兜住。
    这里处理两类高价值纠偏：场景强意图、以及原文里明确写出的数字。
    """
    result = dict(result or {})

    if result.get("scene") not in VALID_SCENES:
        result["scene"] = rule.get("scene", "friends_out")

    if semantic.get("scene"):
        result["scene"] = semantic["scene"]
    if re.search(HOME_DELIVERY_RE, text or ""):
        result["scene"] = "stay_in"
    if semantic.get("home_area"):
        result["home_area"] = semantic["home_area"]
    if semantic.get("transport"):
        result["transport"] = semantic["transport"]

    if result.get("scene") == "stay_in":
        result["has_kid"] = False

    if re.search(r"打本|约本|推本|本子|剧本杀|剧本", text):
        result["scene"] = "friends_out"

    if _has_party_size(text):
        result["party_size"] = rule.get("party_size", result.get("party_size", 4))
    if _has_budget(text):
        result["budget_per_person"] = rule.get("budget_per_person", result.get("budget_per_person", 150))
    if _has_start_time(text):
        result["start_time"] = rule.get("start_time", result.get("start_time", "14:00"))
    else:
        # 只是临时占位；_detect_clarifications 会要求用户补全，不会直接拿默认值排方案。
        result["start_time"] = rule.get("start_time", "14:00")

    if result.get("scene") == "stay_in" and not _has_party_size(text):
        result["party_size"] = 1
    if re.search(r"我和(女朋友|男朋友|对象|老婆|老公)|情侣|约会|二人世界", text or "") and not _has_party_size(text):
        result["party_size"] = 2

    result["preferences"] = _merge_unique(
        list(result.get("preferences", []) or []) + list(semantic.get("preferences", []) or [])
    )
    result["hard_limits"] = _merge_unique(
        list(result.get("hard_limits", []) or []) + list(semantic.get("hard_limits", []) or [])
    )
    result["intent_tags"] = semantic.get("intent_tags", []) or []

    domain = extract_domain_signals(text)
    for key in ("script_style", "cuisine_preference", "distance_tolerance", "origin_mode", "stayin_mode"):
        if domain.get(key):
            result[key] = domain[key]
    if re.search(CUISINE_ANY_RE, text or "") and re.search(r"吃|餐|菜系|美食|火锅|海鲜|烧烤|江浙菜", text or ""):
        result["cuisine_preference"] = "any"
    result["diet_limits"] = _merge_unique(
        list(result.get("diet_limits", []) or []) + list(domain.get("diet_limits", []) or [])
    )

    # 用户说“附近/别太远”本质是距离硬约束；“好吃可跑远”则让 catalog 放宽距离。
    if result.get("distance_tolerance") in ("nearby", "same_area") and "stay_near" not in result["hard_limits"]:
        result["hard_limits"].append("stay_near")

    return result


def _detect_clarifications(text: str, request: dict, explicit_cats: list[dict]) -> list[dict]:
    """
    判断是否信息严重缺失，需要追问。
    具体规则在 clarify.py 中维护，parser 只做入口转发。
    """
    return decide_clarifications(text, request, explicit_cats)


def _load_samples() -> list[dict]:
    """读 samples.json，最后一层兜底用。"""
    path = os.path.join(DATA_DIR, "samples.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def parse_request(text: str, logbook=None) -> dict:
    """
    把一句话转结构化需求。永远返回有效 dict（5.3 节定义）。
    额外字段：
      - explicit_categories: 用户原话点名的品类（planner 锁槽用）
      - clarifications_needed: 信息严重缺失时的追问列表（core 路由用）

    被 Agent.run() 调用。
    """
    text = (text or "").strip()
    if logbook:
        logbook.add("理解需求", "running", "正在解析这句话里的人群、预算、时间和偏好…")

    semantic = analyze_semantics(text)

    # ===== 第一层：LongCat 解析（无 key 时自动走本地规则兜底） =====
    result = _try_llm_parse(text)
    rule = _keyword_parse(text)
    if result:
        # 把规则解析的结果做个并集，补齐 LLM 偶尔漏字段的情况
        for k, v in rule.items():
            if k not in result or result[k] in (None, "", [], {}):
                result[k] = v
        result["raw_text"] = text
        result["_parse_method"] = "llm"
    else:
        # ===== 第二层：关键词规则 =====
        result = rule
        result["_parse_method"] = "rule"

    result = _normalize_request_by_text(text, result, rule, semantic)

    # ===== 不论哪一层，都做明确品类抽取 + 主意图归一 + 追问检测 =====
    explicit_cats = _remove_negated_categories(text, _extract_explicit_categories(text, semantic))
    script_title = _extract_script_title(text)
    if script_title and not any(c.get("category") == "剧本杀" for c in explicit_cats):
        explicit_cats.append({"role": "PLAY", "category": "剧本杀", "keyword": script_title})
    if script_title:
        result["script_title"] = script_title
    result["explicit_categories"] = explicit_cats
    _apply_intent_fields(text, result, explicit_cats, semantic)

    # 如果用户点了 PLAY 品类，把场景固定为活动局（除非已是 stay_in / couple / family_out / addon_only）。
    # EAT-only / ADDON-only 不做这个覆盖，避免“只想吃海鲜/只想喝奶茶”被硬塞成玩+吃两段。
    if any(c.get("role") == "PLAY" for c in explicit_cats) and result.get("scene") not in ("stay_in", "couple", "family_out", "addon_only"):
        has_eat_intent = _has_food_intent(text, explicit_cats)
        result["scene"] = "friends_out" if has_eat_intent or any(c.get("role") == "EAT" for c in explicit_cats) else "play_only"
        if "no_meal" in result.get("negative_intents", []):
            result["scene"] = "play_only"

    _sanitize_preferences_by_scene(text, result, explicit_cats)
    frame = build_intent_frame(text, result)
    result["intent_frame"] = frame
    result["intent_status"] = frame["intent_status"]
    result["next_action"] = frame["next_action"]
    result["confidence"] = min(result.get("confidence", 0.0) or 0.0, frame.get("confidence", 0.0) or 0.0) if frame["intent_status"] in ("broad", "ambiguous", "rest_first") else result.get("confidence", frame.get("confidence", 0.0))
    result["primary_intent"] = frame["primary_intent"] if frame["primary_intent"] != "unknown" else result.get("primary_intent")
    result["main_role"] = frame["main_role"] if frame["main_role"] != "UNKNOWN" else result.get("main_role")
    result["sequence"] = frame["sequence"]
    for item in frame.get("sequence") or []:
        role = item.get("role")
        category = item.get("category")
        if role in ("PLAY", "EAT", "STAYIN", "ADDON") and category:
            if not any(c.get("role") == role and c.get("category") == category for c in result.get("explicit_categories", [])):
                result.setdefault("explicit_categories", []).append({"role": role, "category": category, "keyword": "intent_frame"})
    result["requested_categories"] = _merge_unique(
        list(result.get("requested_categories") or []) +
        [item.get("category") for item in frame.get("sequence") or [] if item.get("category")]
    )
    if result.get("primary_intent") == "food_discovery" and not any(c.get("role") == "PLAY" for c in explicit_cats):
        result["scene"] = "food_only"
    result["negative_intents"] = _merge_unique(list(result.get("negative_intents") or []) + list(frame.get("negative_intents") or []))
    result["safety_flags"] = _merge_unique(list(result.get("safety_flags") or []) + list(frame.get("safety_flags") or []))

    # 用户没说过的字段不能显示成已确认。保留旧字段给 planner 的内部试排，
    # 但 broad/rest/ambiguous 阶段会在 core 被拦截，不会直接进入 build_itinerary。
    for key, source in (frame.get("field_sources") or {}).items():
        if source == "unknown":
            if key == "transport":
                result[key] = "unknown"
            else:
                result[key] = None
        else:
            result[key] = frame["confirmed_fields"].get(key)

    if frame["next_action"] != "build_plan":
        result["clarifications_needed"] = clarification_questions(frame)
    elif frame.get("primary_intent") == "date":
        result["clarifications_needed"] = []
    else:
        result["clarifications_needed"] = _detect_clarifications(text, result, explicit_cats)
    result["missing_fields"] = [c.get("key") for c in result["clarifications_needed"] if c.get("key")]
    if not result["clarifications_needed"] and result.get("next_action") not in ("build_plan", "show_category_choices", "rest_support"):
        result["next_action"] = "build_plan"
        if result.get("intent_frame"):
            result["intent_frame"]["next_action"] = "build_plan"
    result["goal_summary"] = frame.get("goal_summary") or _make_goal_summary(result)

    # 日志
    if logbook:
        cat_str = "、".join(c["category"] for c in explicit_cats) or "无"
        need = result["clarifications_needed"]
        if need:
            need_keys = "、".join(c["key"] for c in need)
            logbook.add("理解需求", "warning",
                        f"识别为「{_scene_label(result['scene'])}」，点名品类：{cat_str}；"
                        f"还缺：{need_keys}，需要追问")
        else:
            logbook.add("理解需求", "success",
                        f"识别为「{_scene_label(result['scene'])}」，"
                        f"{result.get('party_size', '?')}人，"
                        f"预算 ¥{result.get('budget_per_person', '?')}/人")
    return result


def _scene_label(scene: str) -> str:
    return {
        "friends_out": "朋友出门安排",
        "play_only":   "活动优先安排",
        "family_out":  "家庭亲子安排",
        "stay_in":     "宅家安排",
        "couple":      "情侣约会",
        "food_only":   "美食安排",
        "addon_only":  "轻量单点",
    }.get(scene, "周末安排")


def _make_goal_summary(request: dict) -> str:
    cats = request.get("requested_categories") or []
    primary = request.get("primary_intent", "")
    party = request.get("party_size")
    budget = request.get("budget_per_person")
    bits = []
    if primary in ("milk_tea", "coffee", "addon_single"):
        bits.append(f"想要一份{cats[0] if cats else '饮品'}")
    elif primary == "movie":
        bits.append("想看电影")
    elif primary == "script_game":
        bits.append(f"{party or '?'} 人想玩剧本杀")
    elif primary == "hotpot":
        bits.append(f"{party or '?'} 人想吃火锅")
    elif primary == "birthday":
        bits.append(f"{party or '?'} 人生日仪式感安排")
    elif request.get("scene") == "stay_in":
        bits.append("想宅家放松")
    elif cats:
        bits.append("想要 " + "、".join(cats))
    else:
        bits.append("想把周末安排落地")
    if budget:
        bits.append(f"人均约 ¥{budget}")
    if request.get("transport") == "public":
        bits.append("公共交通")
    elif request.get("transport") == "self_drive":
        bits.append("自驾")
    return "，".join(bits)


def _try_llm_parse(text: str) -> dict | None:
    """第一层：让 LongCat 返回纯 JSON。失败返回 None。"""
    if not text:
        return None
    try:
        from agent.llm import ask_llm
        system = (
            "你是一个需求解析器。把用户的一句话转成 JSON，"
            "只返回纯 JSON 对象，不要 markdown 代码块，不要任何前后说明文字。\n"
            "字段约定：\n"
            "scene: friends_out / play_only / family_out / stay_in / couple / food_only 之一\n"
            "party_size: 数字\n"
            "has_kid: bool\n"
            "transport: public / self_drive / unknown\n"
            "start_time: HH:MM\n"
            "window_hours: 数字\n"
            "home_area: 新街口 / 老门东 / 河西 / 线上 之一\n"
            "budget_per_person: 数字\n"
            "preferences: 字符串数组，候选值 photo/good_food/easy_pace/culture/kid_friendly/light_food/relax\n"
            "hard_limits: 字符串数组，候选值 no_evening_queue/stay_near/kid_safe\n"
            "script_style: 剧本杀子类，候选值 欢乐本/推理本/机制本/情感本/恐怖本/不限\n"
            "cuisine_preference: 餐饮菜系，候选值 火锅/烧烤/海鲜/江浙菜/本地面食/简餐/西餐/融合菜/不限\n"
            "diet_limits: 字符串数组，候选值 no_spicy/no_alcohol/light_food/no_cilantro\n"
            "distance_tolerance: nearby/same_area/food_first/flexible\n"
            "origin_mode: together/separate/organizer_area/unknown"
        )
        raw = ask_llm(text, system=system, timeout=8)
        if not raw:
            return None
        # 清理可能的 ```json ``` 包裹
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception:
        return None


def _keyword_parse(text: str) -> dict:
    """第二层：关键词规则。"""
    # 1. 场景
    scene = "friends_out"
    if _has_stay_in_intent(text):
        scene = "stay_in"
    elif re.search(r"孩子|娃|宝宝|亲子|老婆孩子|儿子|女儿", text):
        scene = "family_out"
    elif re.search(r"情侣|对象|约会|男朋友|女朋友", text):
        scene = "couple"
    elif re.search(r"吃饭|聚餐|餐厅|晚饭|午饭|海鲜|火锅|烧烤|江浙菜|炒菜|家常菜|西餐|简餐", text) and not re.search(
        r"剧本杀|打本|约本|密室|桌游|狼人杀|KTV|唱歌|看电影|电影院|看展|展览|手作|陶艺|市集|逛街|citywalk|Citywalk|散步",
        text
    ):
        scene = "food_only"

    has_kid = scene == "family_out" or bool(re.search(r"孩子|娃|宝宝", text))

    # 2. 人数
    party_size = 1 if scene == "stay_in" else (3 if has_kid else (2 if scene == "couple" else 4))
    party_size = parse_party_size(text, party_size)

    # 3. 预算
    budget = parse_budget(text, 150)

    # 4. 开始时间
    start_time = parse_coarse_start_time(text, "14:00")

    # 5. 时长
    window_hours = 5
    m = re.search(r"(\d+)\s*个?小时", text)
    if m:
        window_hours = int(m.group(1))

    # 6. 区域
    home_area = first_area(text, "新街口")
    if scene == "stay_in":
        home_area = "线上"

    # 7. 交通
    transport = "public"
    if re.search(r"自驾|开车", text):
        transport = "self_drive"

    # 8. 偏好（软）
    prefs: list[str] = []
    if re.search(r"拍照|出片|打卡", text):
        prefs.append("photo")
    if re.search(r"吃|餐|美食", text):
        prefs.append("good_food")
    if re.search(r"不累|不想太累|轻松|歇|休息|躺", text):
        prefs.append("easy_pace")
    if re.search(r"文艺|展|安静", text):
        prefs.append("culture")
    if has_kid:
        prefs.append("kid_friendly")
        if "easy_pace" not in prefs:
            prefs.append("easy_pace")
    if re.search(r"减肥|清淡|低脂|轻食", text):
        prefs.append("light_food")
    if scene == "stay_in":
        prefs.append("relax")
    if re.search(r"打本|约本|推本|本子|剧本杀|剧本|密室|桌游", text):
        prefs.append("relax")
    if not prefs:
        if scene == "food_only" or re.search(FOOD_INTENT_RE, text):
            prefs = ["good_food"]
        elif scene == "stay_in":
            prefs = ["relax"]
        else:
            prefs = []

    # 9. 硬约束
    hard_limits: list[str] = []
    if re.search(r"排队", text):
        hard_limits.append("no_evening_queue")
    if re.search(r"别离家太远|不要太远|近一?点|别太远", text):
        hard_limits.append("stay_near")
    if has_kid:
        hard_limits.append("kid_safe")

    return {
        "scene": scene,
        "party_size": party_size,
        "has_kid": has_kid,
        "transport": transport,
        "start_time": start_time,
        "window_hours": window_hours,
        "home_area": home_area,
        "budget_per_person": budget,
        "preferences": prefs,
        "hard_limits": hard_limits,
        "raw_text": text,
    }


if __name__ == "__main__":
    from agent.logbook import LogBook

    tests = [
        "今天下午和朋友4个人出去玩，想拍照吃饭不要太累，人均150，晚上别排队",
        "今天下午想带5岁的孩子和老婆出去玩几个小时，老婆在减肥要清淡点，别离家太远",
        "周末不想出门，想在家看个电影点个外卖，轻松一点",
        "和对象周末下午想约会，文艺一点的，人均120",
        # 信息不全：应触发追问 + 锁定剧本杀品类
        "下午想和朋友去打剧本杀",
        # 信息不全：应触发追问 + 锁定火锅品类
        "晚上想吃火锅",
    ]
    for t in tests:
        log = LogBook()
        print(f"\n输入：{t}")
        r = parse_request(t, log)
        print(f"  scene={r['scene']}  party={r['party_size']}人  预算¥{r['budget_per_person']}")
        print(f"  preferences={r['preferences']}")
        print(f"  hard_limits={r['hard_limits']}")
        print(f"  解析方式：{r.get('_parse_method')}")
        print(f"  明确品类：{r.get('explicit_categories')}")
        need = r.get('clarifications_needed', [])
        if need:
            print(f"  需追问：{[c['key'] for c in need]}")
