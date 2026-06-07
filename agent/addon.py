"""
addon.py —— 本地 Mock optional add-on 推荐。

Slice 6 规则：
- add-on 只作为可选小卡片，不污染主行程；
- 用户显式加入后才进入 Mock checkout；
- 所有履约、配送、攻略、优惠都只是本地 Mock。
"""
import sys
import os
import json
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

MEAL_CATEGORIES = {"外卖", "江浙菜", "火锅", "海鲜", "烧烤", "简餐", "西餐", "融合菜", "本地面食"}
LIGHT_DRINK_CATEGORIES = {"奶茶", "咖啡", "甜品", "冰淇淋"}
RITUAL_CATEGORIES = {"蛋糕鲜花"}
STAYIN_CATEGORIES = {"外卖", "闪购零食"}


def _load_merchants() -> list[dict]:
    path = os.path.join(DATA_DIR, "merchants.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _raw_text(request: dict) -> str:
    return request.get("raw_text") or request.get("text") or ""


def _flag_set(request: dict) -> set[str]:
    return set(request.get("negative_intents") or []) | set(request.get("safety_flags") or []) | set(request.get("diet_limits") or [])


def _merchant_flags(merchant: dict) -> dict:
    flags = merchant.get("flags") or {}
    if isinstance(flags, list):
        return {str(item): True for item in flags}
    return flags if isinstance(flags, dict) else {}


def _body_suitability(merchant: dict) -> dict:
    body = merchant.get("body_suitability") or {}
    if isinstance(body, list):
        return {str(item): True for item in body}
    return body if isinstance(body, dict) else {}


def _is_birthday(request: dict) -> bool:
    confirmed = ((request.get("intent_frame") or {}).get("confirmed_fields") or {})
    raw = _raw_text(request)
    return confirmed.get("occasion") == "生日" or any(k in raw for k in ("生日", "庆生", "过生日", "寿星"))


def _is_date(request: dict) -> bool:
    raw = _raw_text(request)
    return request.get("scene") == "couple" or request.get("primary_intent") == "date" or any(k in raw for k in ("约会", "女朋友", "男朋友", "情侣", "对象", "浪漫"))


def _duration_minutes(plan: dict, request: dict) -> int:
    for value in (
        request.get("duration_minutes"),
        ((request.get("intent_frame") or {}).get("confirmed_fields") or {}).get("duration_minutes"),
    ):
        try:
            if value:
                return int(value)
        except Exception:
            pass
    try:
        return int(request.get("window_hours") or 0) * 60
    except Exception:
        return int(plan.get("total_minutes") or 0)


def _business_steps(plan: dict) -> list[dict]:
    return [s for s in plan.get("steps", []) or [] if s.get("kind") != "travel"]


def _anchor_for(plan: dict, request: dict, prefer: tuple[str, ...] = ()) -> dict:
    steps = _business_steps(plan)
    for kind in prefer:
        for idx, step in enumerate(steps):
            if step.get("kind") == kind or step.get("slot_role") == kind:
                return {**step, "_segment_index": idx}
    for idx, step in enumerate(reversed(steps)):
        if step.get("area") and step.get("area") != "线上":
            out = {**step, "_segment_index": len(steps) - idx - 1}
            return out
    return {
        "name": "宅家地址" if request.get("scene") == "stay_in" else "当前目的地",
        "area": request.get("home_area") or "新街口",
        "kind": "stayin" if request.get("scene") == "stay_in" else "activity",
        "_segment_index": None,
    }


def _merchant_ok(merchant: dict, request: dict, *, target_area: str | None = None, categories: set[str] | None = None) -> bool:
    if merchant.get("disabled_for_recommendation"):
        return False
    if categories and merchant.get("category") not in categories:
        return False
    if target_area and merchant.get("area") not in (target_area, "线上"):
        return False
    flags = _flag_set(request)
    raw = _raw_text(request)
    merchant_flags = _merchant_flags(merchant)
    if "no_alcohol" in flags and merchant_flags.get("alcohol"):
        return False
    if ("no_meal" in flags or "不吃饭" in raw or "不想吃饭" in raw) and merchant.get("category") in MEAL_CATEGORIES:
        return False
    if any(k in raw for k in ("不要奶茶", "不喝奶茶")) and merchant.get("category") == "奶茶":
        return False
    if any(k in raw for k in ("不要花", "不要鲜花", "不要蛋糕")) and merchant.get("category") in RITUAL_CATEGORIES:
        return False
    if "cannot_ice" in flags or (request.get("drink_preferences") or {}).get("hot_required"):
        if merchant.get("category") in {"奶茶", "咖啡"}:
            opts = merchant.get("drink_options") or {}
            body = _body_suitability(merchant)
            if not (opts.get("hot_available") or body.get("cannot_ice")):
                return False
    if "not_too_sweet" in flags and merchant.get("category") in {"奶茶", "甜品"}:
        body = _body_suitability(merchant)
        if merchant.get("category") == "奶茶" and not body.get("not_too_sweet"):
            return False
    if "caffeine_free" in flags and merchant.get("category") in {"奶茶", "咖啡"}:
        opts = merchant.get("drink_options") or {}
        if opts.get("caffeine") not in ("none", "optional", "low", None):
            return False
    return True


def _pick_merchant(
    merchants: list[dict],
    request: dict,
    *,
    categories: set[str],
    target_area: str | None = None,
    exclude_ids: set[str] | None = None,
) -> dict | None:
    exclude_ids = set(exclude_ids or set())
    pool = [
        m for m in merchants
        if m.get("slot_role") in {"ADDON", "STAYIN"} and str(m.get("id")) not in exclude_ids
        and _merchant_ok(m, request, target_area=target_area, categories=categories)
    ]
    if not pool and target_area:
        pool = [
            m for m in merchants
            if m.get("slot_role") in {"ADDON", "STAYIN"} and str(m.get("id")) not in exclude_ids
            and _merchant_ok(m, request, categories=categories)
        ]
    if not pool:
        return None
    pool.sort(key=lambda m: (m.get("rating", 0), -int(m.get("price", 999) or 999)), reverse=True)
    return deepcopy(pool[0])


def _addon_from_merchant(
    addon_type: str,
    merchant: dict,
    *,
    title: str,
    reason: str,
    trigger_scene: str,
    target_segment: dict,
    fulfillment_type: str,
    checkout_eligible: bool = True,
    constraints: list[str] | None = None,
    category_override: str | None = None,
) -> dict:
    target_index = target_segment.get("_segment_index")
    target_area = target_segment.get("area") or merchant.get("area")
    addon_id = f"{addon_type}:{merchant.get('id')}:{target_index if target_index is not None else 'home'}"
    display_area = target_area if fulfillment_type in {"mock_delivery", "mock_home_delivery", "mock_pickup_or_delivery"} else merchant.get("area")
    return {
        "addon_id": addon_id,
        "id": addon_id,
        "merchant_id": merchant.get("id"),
        "name": merchant.get("name"),
        "title": title,
        "category": category_override or merchant.get("category"),
        "merchant_category": merchant.get("category"),
        "type": addon_type,
        "trigger_scene": trigger_scene,
        "target_segment_role": target_segment.get("slot_role") or target_segment.get("kind"),
        "target_segment_index": target_index,
        "target_segment_id": target_segment.get("id") or target_segment.get("segment_id"),
        "target_name": target_segment.get("name") or target_segment.get("target_name") or "宅家地址",
        "target_area": target_area,
        "area": display_area,
        "merchant_area": merchant.get("area"),
        "price": merchant.get("price", 0),
        "rating": merchant.get("rating", 0),
        "image": merchant.get("image", ""),
        "tags": merchant.get("review_tags", []),
        "review_count": merchant.get("review_count", 0),
        "reason": reason,
        "mock_only": True,
        "real_delivery": False,
        "real_payment": False,
        "real_order": False,
        "fulfillment_type": fulfillment_type,
        "constraints": constraints or ["same_area", "optional_only", "mock_only"],
        "checkout_eligible": bool(checkout_eligible),
        "duration_minutes": merchant.get("duration_minutes", 0),
        "delivery_minutes": 25 if fulfillment_type in {"mock_delivery", "mock_home_delivery"} else 0,
        "status": "optional",
        "source": "hidden_intent_optional_addon",
    }


def _content_addon(addon_type: str, *, title: str, reason: str, target_segment: dict, trigger_scene: str) -> dict:
    target_index = target_segment.get("_segment_index")
    addon_id = f"{addon_type}:content:{target_index if target_index is not None else 'home'}"
    return {
        "addon_id": addon_id,
        "id": addon_id,
        "name": title,
        "title": title,
        "category": "内容攻略",
        "type": addon_type,
        "trigger_scene": trigger_scene,
        "target_segment_role": target_segment.get("slot_role") or target_segment.get("kind"),
        "target_segment_index": target_index,
        "target_segment_id": target_segment.get("id") or target_segment.get("segment_id"),
        "target_name": target_segment.get("name") or "当前目的地",
        "target_area": target_segment.get("area") or "新街口",
        "area": target_segment.get("area") or "新街口",
        "price": 0,
        "rating": 0,
        "image": "📸",
        "reason": reason,
        "mock_only": True,
        "real_delivery": False,
        "real_payment": False,
        "real_order": False,
        "fulfillment_type": "content_card",
        "constraints": ["content_only", "not_bookable", "not_checkout"],
        "checkout_eligible": False,
        "duration_minutes": 0,
        "delivery_minutes": 0,
        "status": "optional",
        "source": "hidden_intent_content_card",
    }


def suggest_addons(plan: dict, request: dict, logbook=None, rejected_ids: set[str] | None = None) -> list[dict]:
    """Return optional local Mock add-ons for this plan."""
    if not plan or plan.get("unavailable"):
        return []
    raw = _raw_text(request)
    if any(k in raw for k in ("不要额外", "不用额外", "不想买", "不要加购", "别推荐别的")):
        return []
    merchants = _load_merchants()
    if not merchants:
        return []
    rejected_ids = set(rejected_ids or set())
    flags = _flag_set(request)
    scene = request.get("scene") or request.get("primary_intent") or "unknown"
    out: list[dict] = []

    def add(item: dict | None) -> None:
        if not item:
            return
        key = str(item.get("addon_id") or item.get("id") or item.get("merchant_id") or "")
        merchant_key = str(item.get("merchant_id") or "")
        if key in rejected_ids or merchant_key in rejected_ids:
            return
        if any((x.get("addon_id") or x.get("id")) == (item.get("addon_id") or item.get("id")) for x in out):
            return
        out.append(item)

    if _is_birthday(request):
        anchor = _anchor_for(plan, request, prefer=("restaurant", "activity"))
        merchant = _pick_merchant(merchants, request, categories=RITUAL_CATEGORIES, target_area=anchor.get("area"), exclude_ids=rejected_ids)
        add(_addon_from_merchant(
            "birthday_cake",
            merchant,
            title="生日蛋糕/鲜花送达（Mock）",
            reason=f"绑定到「{anchor.get('name', '目的地')}」，提前送达，不改变主行程。",
            trigger_scene="birthday",
            target_segment=anchor,
            fulfillment_type="mock_delivery",
            constraints=["same_area_or_destination", "birthday_only", "optional_only", "mock_only"],
            category_override="生日补给",
        ) if merchant else None)

    if _is_date(request):
        anchor = _anchor_for(plan, request, prefer=("restaurant", "activity"))
        merchant = _pick_merchant(merchants, request, categories={"甜品", "奶茶"}, target_area=anchor.get("area"), exclude_ids=rejected_ids)
        addon_type = "date_dessert"
        add(_addon_from_merchant(
            addon_type,
            merchant,
            title="约会后甜品/饮品（Mock）",
            reason=f"在「{anchor.get('name', '约会地点')}」附近顺手加一站，作为可选内容，不写入主安排。",
            trigger_scene="date",
            target_segment=anchor,
            fulfillment_type="mock_pickup",
            constraints=["same_area_or_destination", "date_only", "optional_only", "mock_only"],
        ) if merchant else None)

    cats = {s.get("category") for s in _business_steps(plan)}
    long_activity = _duration_minutes(plan, request) >= 240
    if long_activity and cats & {"剧本杀", "密室", "KTV"}:
        anchor = _anchor_for(plan, request, prefer=("activity",))
        if "no_meal" not in flags:
            merchant = _pick_merchant(merchants, request, categories={"外卖"}, target_area=anchor.get("area"), exclude_ids=rejected_ids)
            add(_addon_from_merchant(
                "dinner_delivery",
                merchant,
                title="长场次饭点补给（Mock）",
                reason=f"{anchor.get('category', '活动')}时间较长，饭点外卖可送到活动附近，不占主行程。",
                trigger_scene="long_activity",
                target_segment=anchor,
                fulfillment_type="mock_delivery",
                constraints=["same_area", "long_activity", "optional_only", "mock_only"],
            ) if merchant else None)
        merchant = _pick_merchant(merchants, request, categories={"奶茶", "咖啡"}, target_area=anchor.get("area"), exclude_ids=rejected_ids)
        add(_addon_from_merchant(
            "milk_tea",
            merchant,
            title="长场次饮品补给（Mock）",
            reason="适合等人、开局前或中场休息，加入后才进入 Mock 结算。",
            trigger_scene="long_activity",
            target_segment=anchor,
            fulfillment_type="mock_pickup_or_delivery",
            constraints=["same_area", "optional_only", "mock_only"],
        ) if merchant else None)

    if request.get("scene") == "stay_in" or request.get("primary_intent") == "stay_in":
        anchor = _anchor_for(plan, request, prefer=("stayin",))
        home_area = request.get("home_area") or anchor.get("area") or "新街口"
        if "no_meal" not in flags:
            merchant = _pick_merchant(merchants, request, categories={"外卖"}, target_area=home_area, exclude_ids=rejected_ids)
            add(_addon_from_merchant(
                "dinner_delivery",
                merchant,
                title="宅家外卖补给（Mock）",
                reason="送到宅家地址，适合边看边吃；不推荐线下门店打卡。",
                trigger_scene="stay_in",
                target_segment={**anchor, "area": home_area, "name": "宅家地址"},
                fulfillment_type="mock_home_delivery",
                constraints=["home_delivery", "stay_in", "optional_only", "mock_only"],
            ) if merchant else None)
        merchant = _pick_merchant(merchants, request, categories={"闪购零食"}, target_area=home_area, exclude_ids=rejected_ids)
        add(_addon_from_merchant(
            "xiaoxiang_snacks",
            merchant,
            title="小象超市零食饮料组合（Mock）",
            reason="宅家场景的零食饮料包，送到家；不进入线下行程。",
            trigger_scene="stay_in",
            target_segment={**anchor, "area": home_area, "name": "宅家地址"},
            fulfillment_type="mock_home_delivery",
            constraints=["home_delivery", "stay_in", "optional_only", "mock_only"],
        ) if merchant else None)

    if "no_outdoor" not in flags and ((cats & {"展览", "景区", "市集"}) or _is_date(request)):
        anchor = _anchor_for(plan, request, prefer=("activity",))
        if anchor.get("area") != "线上":
            add(_content_addon(
                "photo_guide",
                title="顺手出片攻略（Mock）",
                reason=f"围绕「{anchor.get('name', '目的地')}」给 3 个拍照点和到店动线，只是内容卡，不进预约/账单。",
                target_segment=anchor,
                trigger_scene="photo_or_date",
            ))

    # Hard stop: no meal means no dinner delivery / restaurant-like add-on.
    if "no_meal" in flags:
        out = [x for x in out if x.get("category") not in MEAL_CATEGORIES and x.get("type") != "dinner_delivery"]
    if any(k in raw for k in ("不要奶茶", "不喝奶茶")):
        out = [x for x in out if x.get("category") != "奶茶"]
    if any(k in raw for k in ("不要花", "不要鲜花", "不要蛋糕")):
        out = [x for x in out if x.get("category") not in RITUAL_CATEGORIES]

    if logbook:
        logbook.add("增值推荐", "success", f"生成 {len(out)} 个可选 Mock add-on，默认不进入主行程")
    return out[:4]


def suggest_addon(plan: dict, request: dict, logbook=None) -> dict | None:
    """
    Backward-compatible helper: return the first checkout-eligible optional add-on.
    """
    for addon in suggest_addons(plan, request, logbook):
        if addon.get("checkout_eligible", True):
            return addon
    return None


if __name__ == "__main__":
    from agent.logbook import LogBook
    log = LogBook()
    plan = {"steps": [{"kind": "restaurant", "area": "新街口"}],
            "total_cost_per_person": 130}
    req = {"transport": "public", "has_kid": False, "budget_per_person": 150}
    r = suggest_addon(plan, req, log)
    print(f"  推荐：{r}")
    log.print_all()
