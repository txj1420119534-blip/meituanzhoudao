"""
catalog.py —— 按槽位从 merchants.json 检索 + 排序候选。
排序分 = 匹配分 + 广告权重；硬约束（预算/营业/距离）永远先于广告权重过滤。
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
UNLIMITED = {"不限", "都可以", "随便", "无所谓", "没有偏好", "any"}


def _load_merchants() -> list[dict]:
    path = os.path.join(DATA_DIR, "merchants.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _load_travel() -> dict:
    path = os.path.join(DATA_DIR, "travel.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _travel_between(from_area: str, to_area: str) -> dict:
    travel = _load_travel()
    key = f"{from_area}->{to_area}"
    if key in travel:
        return travel[key]
    key2 = f"{to_area}->{from_area}"
    if key2 in travel:
        return travel[key2]
    return {"walk": 60, "taxi": 22, "metro": 30}


def _is_open(merchant: dict, start_time: str) -> bool:
    if isinstance(start_time, (int, float)):
        start_time = f"{int(start_time):02d}:00"
    elif not isinstance(start_time, str):
        start_time = "14:00"
    elif ":" not in start_time and start_time.isdigit():
        start_time = f"{int(start_time):02d}:00"
    open_t = merchant.get("open", "00:00")
    close_t = merchant.get("close", "23:59")
    return open_t <= start_time <= close_t


def search_merchants(
    slot_role: str,
    request: dict,
    logbook=None,
    want: "str | list[str] | None" = None,
    exclude_ids: "set[str] | list[str] | None" = None,
) -> list[dict]:
    """
    按槽位 + 约束检索商户，返回排序后的候选列表（每条带 _match_score/_ad_weight/_final_score/is_promoted）。

    步骤：
      1) slot_role 过滤 → 2) want（细分品类）过滤 → 3) hard_limits（预算/营业/距离/孩子）过滤
      4) exclude_ids 排除 → 5) 计算匹配分 → 6) 加广告权重 → 7) 按 final_score 降序
    """
    merchants = _load_merchants()
    exclude_ids = set(exclude_ids or [])
    budget = int(request.get("budget_per_person", 999) or 999)
    home_area = request.get("home_area", "新街口")
    prefs = request.get("preferences", [])
    hard_limits = request.get("hard_limits", [])
    has_kid = request.get("has_kid", False)
    start_time = request.get("start_time", "14:00")
    cuisine = request.get("cuisine_preference")
    diet_limits = request.get("diet_limits", []) or []
    if isinstance(diet_limits, str):
        diet_limits = [] if diet_limits == "none" else [diet_limits]
    safety_flags = request.get("safety_flags", []) or []
    if isinstance(safety_flags, str):
        safety_flags = [safety_flags]
    drink_preferences = request.get("drink_preferences", {}) or {}
    distance_tolerance = request.get("distance_tolerance")
    script_style = request.get("script_style")
    party_size = int(request.get("party_size", 2) or 2)
    origin_mode = request.get("origin_mode")
    target_area_locked = bool(request.get("target_area_locked") and home_area and home_area != "线上")

    if logbook:
        logbook.add("商户检索", "running",
                    f"正在筛选 {slot_role} 类目候选商户…")

    candidates: list[dict] = []
    for m_raw in merchants:
        m = dict(m_raw)  # 拷贝一份，避免污染原数据
        if m.get("disabled_for_recommendation"):
            continue
        if m["slot_role"] != slot_role:
            continue
        if m["id"] in exclude_ids:
            continue
        # want 限定品类
        if want:
            want_list = [want] if isinstance(want, str) else list(want)
            if m["category"] not in want_list:
                continue
        if slot_role == "EAT" and cuisine and cuisine not in UNLIMITED and m.get("category") != cuisine:
            continue
        if slot_role == "PLAY" and m.get("category") == "剧本杀":
            styles = m.get("script_styles", [])
            if script_style and script_style not in UNLIMITED and styles and script_style not in styles:
                continue
            counts = m.get("player_counts", [])
            if counts and party_size > max(counts):
                continue
            if script_style == "恐怖本" and request.get("newbie"):
                horror_level = str(m.get("horror_level", "低"))
                if not m.get("newbie_friendly", False) or horror_level in ("中", "高"):
                    continue
        # 硬约束：预算（线上 STAYIN 不强卡预算线）
        if m.get("price", 0) > budget and slot_role != "STAYIN":
            continue
        # 硬约束：营业（线上不卡）
        if m.get("area") != "线上" and not _is_open(m, start_time):
            continue
        if target_area_locked and m.get("area") not in (home_area, "线上"):
            continue
        # 硬约束：stay_near（线上不卡）
        if "stay_near" in hard_limits and m.get("area") != "线上":
            tv = _travel_between(home_area, m["area"])
            if tv["taxi"] > 30:
                continue
        if distance_tolerance in ("nearby", "same_area") and m.get("area") != "线上":
            tv = _travel_between(home_area, m["area"])
            if distance_tolerance == "nearby" and tv["taxi"] > 15:
                continue
            if distance_tolerance == "same_area" and tv["taxi"] > 25:
                continue
        # 硬约束：亲子安全
        flags = m.get("flags", {})
        if isinstance(flags, list):
            flags = {str(item): True for item in flags}
        elif not isinstance(flags, dict):
            flags = {}
        if has_kid and not flags.get("kid_friendly", False):
            continue
        tags_text = " ".join(m.get("review_tags", []) or []) + " " + m.get("category", "") + " " + " ".join(m.get("recommended_dishes", []) or [])
        if ("no_alcohol" in diet_limits or "no_alcohol" in safety_flags or "drive_safe" in safety_flags) and (
            flags.get("alcohol", False) or "啤酒" in tags_text or "有酒" in tags_text or m.get("category") == "酒吧"
        ):
            continue
        if "no_spicy" in diet_limits or "no_spicy" in safety_flags:
            support = set(m.get("diet_support", []) or [])
            spicy_raw = m.get("spicy_level", 0)
            if isinstance(spicy_raw, str) and spicy_raw.lower() in {"none", "no", "non_spicy", "不辣"}:
                spicy_level = 0
            else:
                try:
                    spicy_level = int(spicy_raw or 0)
                except (TypeError, ValueError):
                    spicy_level = 0
            if m.get("category") == "火锅":
                if not ({"no_spicy", "不辣", "番茄锅", "鸳鸯锅"} & support):
                    continue
            elif flags.get("spicy", False) or spicy_level >= 2 or any(k in tags_text for k in ["麻辣", "重辣", "川味"]):
                continue
        if slot_role == "ADDON" and m.get("category") in ("奶茶", "咖啡"):
            drink_options = m.get("drink_options", {}) or {}
            body_suitability = m.get("body_suitability", {}) or {}
            if isinstance(body_suitability, list):
                body_suitability = {str(item): True for item in body_suitability}
            elif not isinstance(body_suitability, dict):
                body_suitability = {}
            if drink_preferences.get("hot_required") and not drink_options.get("hot_available", False):
                continue
            if "cannot_ice" in safety_flags and not body_suitability.get("cannot_ice", False):
                continue
            if "not_too_sweet" in safety_flags and not body_suitability.get("not_too_sweet", False):
                continue
            if "body_uncomfortable" in safety_flags and not body_suitability.get("body_uncomfortable", False):
                continue
            if "caffeine_free" in safety_flags and drink_options.get("caffeine") not in ("none", "free", "caffeine_free"):
                continue

        candidates.append(m)

    # ===== 评分 =====
    for m in candidates:
        score = 0.0
        score += m.get("rating", 4.0) * 5

        tags_text = " ".join(m.get("review_tags", []) or []) + " " + m.get("category", "")
        if "photo" in prefs and ("出片" in tags_text or "拍照" in tags_text or "网红" in tags_text):
            score += 10
        if "good_food" in prefs and m.get("rating", 0) >= 4.5:
            score += 8
        if "easy_pace" in prefs and ("低强度" in tags_text or "室内" in tags_text or "轻松" in tags_text or "安静" in tags_text):
            score += 6
        if "culture" in prefs and "文艺" in tags_text:
            score += 6
        if "light_food" in prefs and ("清淡" in tags_text or "轻食" in tags_text):
            score += 8
        if slot_role == "ADDON" and m.get("category") in ("奶茶", "咖啡"):
            drink_options = m.get("drink_options", {}) or {}
            sugar_levels = drink_options.get("sugar_levels", []) or []
            ice_levels = drink_options.get("ice_levels", []) or []
            if drink_preferences.get("hot_required") and drink_options.get("hot_available", False):
                score += 10
            if drink_preferences.get("sugar_level") in sugar_levels:
                score += 5
            if drink_preferences.get("ice_level") in ice_levels:
                score += 5
            if "caffeine_free" in safety_flags and drink_options.get("caffeine") in ("none", "free", "caffeine_free"):
                score += 8
        if "relax" in prefs and ("轻松" in tags_text or "安静" in tags_text):
            score += 4
        if slot_role == "PLAY" and m.get("category") == "剧本杀":
            table_score = _score_script_table(m, request)
            score += table_score
            if script_style and script_style not in UNLIMITED and script_style in (m.get("script_styles") or []):
                score += 8
        if origin_mode == "separate" and m.get("area") == "新街口":
            score += 4

        # 距离
        if m.get("area") != "线上":
            tv = _travel_between(home_area, m["area"])
            if tv["taxi"] <= 15:
                score += 5
            elif tv["taxi"] <= 25:
                score += 2
            if distance_tolerance == "food_first" and slot_role == "EAT" and m.get("rating", 0) >= 4.6:
                score += 5

        # 排队
        queue = m.get("queue_minutes", 0)
        if queue <= 5:
            score += 5
        elif queue <= 15:
            score += 2

        # 广告权重（铁律：上限 15，永远不能凌驾硬约束）
        ad_bid = m.get("ad_bid", 0) or 0
        ad_weight = min(15.0, ad_bid / 8000.0) if ad_bid > 0 else 0.0

        m["_match_score"] = round(score, 2)
        m["_ad_weight"] = round(ad_weight, 2)
        m["_final_score"] = round(score + ad_weight, 2)
        # 推广标：广告权重对最终排名有实质贡献时才打
        m["is_promoted"] = ad_weight >= 3

    candidates.sort(key=lambda x: x["_final_score"], reverse=True)

    if logbook:
        logbook.add("商户检索", "success",
                    f"在 {slot_role} 类目下找到 {len(candidates)} 个候选商户")
    return candidates


def _score_script_table(merchant: dict, request: dict) -> float:
    style = request.get("script_style")
    party_size = int(request.get("party_size", 2) or 2)
    tables = merchant.get("open_tables", []) or []
    best = 0.0
    for table in tables:
        if style and style not in UNLIMITED and table.get("style") != style:
            continue
        required = int(table.get("required_players", 0) or 0)
        current = int(table.get("current_players", 0) or 0)
        if required and party_size > required:
            continue
        if required and current + party_size >= required:
            best = max(best, 12.0)
        elif table.get("status") == "assembling":
            best = max(best, 5.0)
    return best


if __name__ == "__main__":
    from agent.logbook import LogBook
    log = LogBook()

    req = {
        "scene": "friends_out",
        "party_size": 4,
        "has_kid": False,
        "budget_per_person": 150,
        "home_area": "新街口",
        "preferences": ["photo", "good_food", "easy_pace"],
        "hard_limits": ["stay_near"],
        "start_time": "14:00",
    }
    results = search_merchants("PLAY", req, log)
    print(f"\nPLAY 候选 Top 5：")
    for m in results[:5]:
        tag = " [推广]" if m["is_promoted"] else ""
        print(f"  {m['name']:<16} ¥{m['price']:<4} 评分{m['rating']} 分数{m['_final_score']}{tag}")

    print(f"\nEAT 候选 Top 5：")
    results2 = search_merchants("EAT", req, log)
    for m in results2[:5]:
        tag = " [推广]" if m["is_promoted"] else ""
        print(f"  {m['name']:<16} ¥{m['price']:<4} 评分{m['rating']} 分数{m['_final_score']}{tag}")

    log.print_all()
