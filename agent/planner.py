"""
planner.py —— 排方案 / 打分 / 局部重排。纯 Python 规则，毫秒级。
- build_itinerary：按场景模板生成 2 个方案（A 综合最优、B 差异化）。
- score_plan：100 分制 6 维度评分。
- replan：异常时局部重排——只换坏掉的那一环。
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        if filename == "scenes.json":
            return {
                "friends_out": {"label": "兜底朋友局", "slots": [{"role": "PLAY", "title": "先去玩"}]},
                "play_only": {"label": "兜底活动局", "slots": [{"role": "PLAY", "title": "先把活动订好"}]},
                "food_only": {"label": "兜底饭局", "slots": [{"role": "EAT", "title": "先把餐厅订好"}]},
                "addon_only": {"label": "兜底单点", "slots": [{"role": "ADDON", "title": "喝点什么"}]},
                "stay_in": {"label": "兜底宅家", "slots": [{"role": "STAYIN", "title": "宅家安排"}]},
            }
        if filename == "travel.json":
            return {}
        return []


def _travel(from_area: str, to_area: str) -> dict:
    travel = _load_json("travel.json")
    key = f"{from_area}->{to_area}"
    if key not in travel:
        key = f"{to_area}->{from_area}"
    return travel.get(key, {"walk": 60, "taxi": 22, "metro": 30})


def _travel_cost_per_person(tv: dict, mode: str, party_size: int) -> int:
    """Local Mock transit cost used for budget checks; no real map or ride API."""
    if mode == "walk":
        return 0
    if mode in ("public", "metro"):
        return 2
    taxi_total = max(8, int(tv.get("taxi", 22) or 22) * 2)
    return max(1, round(taxi_total / max(1, int(party_size or 1))))


def _to_min(t: str) -> int:
    if isinstance(t, (int, float)):
        t = f"{int(t):02d}:00"
    elif not isinstance(t, str):
        t = "14:00"
    elif ":" not in t and t.isdigit():
        t = f"{int(t):02d}:00"
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _to_str(m: int) -> str:
    m = max(0, round(m))
    return f"{m // 60 % 24:02d}:{m % 60:02d}"


def _merchant_business_fields(merchant: dict) -> dict:
    """Expose category-specific merchant data on plan steps for UI and tests."""
    return {
        "cuisine_tags": merchant.get("cuisine_tags", []),
        "spicy_level": merchant.get("spicy_level"),
        "diet_support": merchant.get("diet_support", []),
        "private_room": merchant.get("private_room"),
        "table_sizes": merchant.get("table_sizes", []),
        "signature_dishes": merchant.get("signature_dishes", []),
        "drink_options": merchant.get("drink_options", {}),
        "body_suitability": merchant.get("body_suitability", {}),
        "coupons": merchant.get("coupons", []),
        "features": merchant.get("features", []),
        "delivery_fee": merchant.get("delivery_fee"),
        "delivery_minutes": merchant.get("delivery_minutes"),
        "open": merchant.get("open"),
        "close": merchant.get("close"),
    }


def _want_list(want) -> list[str]:
    if not want:
        return []
    return [want] if isinstance(want, str) else list(want)


def _slots_from_sequence(request: dict) -> list[dict]:
    slots: list[dict] = []
    for item in request.get("sequence") or []:
        role = item.get("role")
        if role not in ("PLAY", "EAT", "STAYIN", "ADDON"):
            continue
        category = item.get("category")
        slot = {
            "role": role,
            "title": {
                "PLAY": "活动",
                "EAT": "吃点什么",
                "STAYIN": "宅家配送",
                "ADDON": "顺手加购",
            }.get(role, "安排"),
            "source": item.get("source", "explicit_text"),
        }
        if category:
            slot["want"] = category
        slots.append(slot)
    return slots


def _match_script_table(merchant: dict, request: dict) -> dict:
    """为剧本杀节点标注拼场状态，供前端卡片/风险提示展示。"""
    style = request.get("script_style")
    party_size = int(request.get("party_size", 2) or 2)
    tables = merchant.get("open_tables", []) or []
    unlimited = {"不限", "都可以", "随便", "无所谓", "没有偏好", None, ""}

    best = None
    for table in tables:
        if style not in unlimited and table.get("style") != style:
            continue
        required = int(table.get("required_players", 0) or 0)
        current = int(table.get("current_players", 0) or 0)
        if required and party_size > required:
            continue
        can_fill = bool(required and current + party_size >= required)
        rank = 2 if can_fill else (1 if table.get("status") == "assembling" else 0)
        if not best or rank > best["_rank"]:
            best = {**table, "_rank": rank, "can_fill_after_join": can_fill}

    if best:
        best.pop("_rank", None)
        if best.get("can_fill_after_join"):
            best["state_label"] = "加入后可成局"
        elif best.get("status") == "assembling":
            best["state_label"] = "店家正在拼场"
        else:
            best["state_label"] = "可候补"
        return best

    fallback = "密室逃脱 / 桌游"
    return {
        "state_label": "暂无完全匹配的在拼本",
        "style": style or "未指定",
        "deadline": "开场前 40 分钟",
        "fallback": fallback,
        "can_fill_after_join": False,
    }


def _has_birthday_intent(request: dict) -> bool:
    tags = set(request.get("intent_tags", []) or [])
    raw = request.get("raw_text", "") or ""
    return "birthday" in tags or any(k in raw for k in ("生日", "庆生", "过生日", "蛋糕", "鲜花"))


def _explicit_categories_for_role(request: dict, role: str) -> set[str]:
    return {
        item.get("category")
        for item in (request.get("explicit_categories", []) or [])
        if item.get("role") == role and item.get("category")
    }


def _has_explicit_requested_category(request: dict) -> bool:
    return bool(request.get("requested_categories") or request.get("explicit_categories"))


def _relax_options(request: dict, role: str, cats: list[str]) -> list[str]:
    flags = set((request.get("diet_limits") or []) + (request.get("safety_flags") or []))
    if role == "EAT" and "火锅" in cats and "no_spicy" in flags:
        return ["接受鸳鸯锅/番茄锅", "放宽到江浙菜或简餐", "换一个商圈", "提高人均预算"]
    if role == "EAT":
        return ["放宽菜系", "提高人均预算", "换一个商圈", "接受更远距离"]
    if role == "PLAY" and "剧本杀" in cats:
        return ["换剧本类型", "接受拼场等待", "放宽到密室/桌游", "换一个商圈"]
    if role == "ADDON":
        return ["放宽甜度/温度要求", "换到附近商圈", "接受咖啡或甜品"]
    return ["放宽品类", "换一个商圈", "提高预算", "调整时间"]


def _unavailable_plan(request: dict, role: str, cats: list[str], reason: str) -> dict:
    return {
        "status": "needs_relaxation",
        "unavailable": True,
        "title": "需要先放宽条件",
        "focus": "没有静默改题",
        "reason": reason,
        "relaxation_options": _relax_options(request, role, cats),
        "steps": [],
        "slot_alternatives": {},
        "total_cost_per_person": 0,
        "total_minutes": 0,
        "start_time": request.get("start_time", "14:00"),
        "commercial_recommendations": [],
        "optional_addons": [],
        "risks": [reason],
        "score": {"total": 0, "dimensions": {}},
    }


def _allows_after_play_commerce(request: dict) -> bool:
    """用户只要轻量活动/电影时，不主动塞饭和奶茶。"""
    if "no_meal" in (request.get("negative_intents") or []):
        return False
    if request.get("scene") != "play_only":
        return True
    play_cats = _explicit_categories_for_role(request, "PLAY")
    if play_cats and play_cats <= {"电影院", "展览", "市集", "手作", "运动"}:
        return False
    tags = set(request.get("intent_tags", []) or [])
    return bool(tags & {"script_game", "escape_room", "board_game", "ktv", "party", "birthday"})


def _inject_birthday_delivery(plan: dict, request: dict, search_merchants) -> dict:
    """生日蛋糕/鲜花只作为提前准备提示，不混入 Plan A/B 主行程。"""
    if not _has_birthday_intent(request):
        return plan

    restaurant = None
    for step in plan.get("steps", []):
        if step.get("kind") == "restaurant":
            restaurant = step
            break
    if not restaurant:
        return plan

    local_req = dict(request)
    local_req["home_area"] = restaurant.get("area", request.get("home_area", "新街口"))
    local_req["distance_tolerance"] = "same_area"
    candidates = search_merchants("ADDON", local_req, logbook=None, want=["蛋糕鲜花"])
    if not candidates:
        return plan

    merchant = candidates[0]
    plan["long_lead_addon_hint"] = {
        "id": merchant["id"],
        "name": merchant["name"],
        "category": merchant.get("category", "蛋糕鲜花"),
        "target_name": restaurant.get("name", "餐厅"),
        "target_area": restaurant.get("area", ""),
        "suggested_arrival": _to_str(max(_to_min(plan.get("start_time", request.get("start_time", "14:00"))),
                                      _to_min(restaurant.get("start", "18:00")) - 20)),
        "price": merchant.get("price", 0),
        "mock_only": True,
        "optional": True,
    }
    return plan


def _interval_overlaps(start_min: int, end_min: int, window_start: int, window_end: int) -> bool:
    return max(start_min, window_start) < min(end_min, window_end)


def _plan_covers_meal_window(plan: dict) -> str | None:
    business = [s for s in plan.get("steps", []) if s.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery")]
    if not business:
        return None
    start_min = min(_to_min(s.get("start", plan.get("start_time", "14:00"))) for s in business)
    end_min = max(_to_min(s.get("end", s.get("start", plan.get("start_time", "14:00")))) for s in business)
    if _interval_overlaps(start_min, end_min, _to_min("11:30"), _to_min("13:30")):
        return "lunch"
    if _interval_overlaps(start_min, end_min, _to_min("17:30"), _to_min("20:00")):
        return "dinner"
    return None


def _has_confirmed_meal_segment(plan: dict) -> bool:
    for step in plan.get("steps", []):
        if step.get("kind") == "restaurant":
            return True
        if step.get("kind") in ("stayin", "delivery") and step.get("category") == "外卖":
            return True
    return False


def _attach_meal_bridge(plan: dict, request: dict, search_merchants) -> dict:
    """Attach a time-window meal prompt without turning it into a confirmed itinerary segment."""
    flags = set((request.get("negative_intents") or []) + (request.get("diet_limits") or []) + (request.get("safety_flags") or []))
    if "no_meal" in flags or _has_confirmed_meal_segment(plan):
        return plan
    meal_window = _plan_covers_meal_window(plan)
    if not meal_window:
        return plan
    if any((item.get("role") == "EAT") for item in request.get("explicit_categories", []) or []):
        return plan

    anchor = next(
        (s for s in plan.get("steps", []) if s.get("kind") == "activity" and s.get("area") != "线上"),
        next((s for s in plan.get("steps", []) if s.get("kind") in ("activity", "stayin")), {}),
    )
    local_req = dict(request)
    local_req["home_area"] = anchor.get("area") or request.get("home_area") or "新街口"
    local_req["distance_tolerance"] = "same_area"
    want = ["外卖"] if request.get("scene") == "stay_in" or anchor.get("category") in ("剧本杀", "密室", "KTV") else ["简餐", "江浙菜", "外卖"]
    delivery = search_merchants("STAYIN", local_req, logbook=None, want=["外卖"])
    quick_meal = [] if request.get("scene") == "stay_in" else search_merchants("EAT", local_req, logbook=None, want=["简餐", "江浙菜"])
    options = []
    if delivery:
        m = delivery[0]
        options.append({
            "type": "delivery_to_activity",
            "id": m.get("id"),
            "name": m.get("name"),
            "category": m.get("category"),
            "area": m.get("area"),
            "price": m.get("price", 0),
            "source": "time_window",
        })
    if quick_meal:
        m = quick_meal[0]
        options.append({
            "type": "nearby_quick_meal",
            "id": m.get("id"),
            "name": m.get("name"),
            "category": m.get("category"),
            "area": m.get("area"),
            "price": m.get("price", 0),
            "source": "time_window",
        })
    options.append({"type": "skip_meal", "name": "不安排吃的", "source": "user_can_decline"})
    plan["meal_bridge"] = {
        "trigger": meal_window,
        "source": "time_window",
        "requires_user_confirm": True,
        "message": "这段会跨过晚饭/午饭时间，可选：外卖送到活动附近 / 中间简餐 / 不安排。",
        "target_segment": {
            "id": anchor.get("id"),
            "name": anchor.get("name"),
            "category": anchor.get("category"),
            "area": anchor.get("area"),
        },
        "options": options,
    }
    if options and options[0].get("type") != "skip_meal":
        plan.setdefault("meal_bridge_addon", {
            "type": "meal_bridge",
            "title": "饭点补给可选项（Mock）",
            "name": options[0].get("name"),
            "category": options[0].get("category"),
            "area": options[0].get("area"),
            "price": options[0].get("price", 0),
            "optional_only": True,
            "source": "time_window",
        })
    return plan


# ═══════════════════════════════════════════════════════════════════════════
# 主入口：build_itinerary
# ═══════════════════════════════════════════════════════════════════════════
def build_itinerary(request: dict, logbook=None) -> list[dict]:
    """
    按 scenes.json 的槽位模板，给出 1~2 个方案。每个方案含 steps 时间轴、总预算、总时长。
    """
    from agent.catalog import search_merchants

    scene = request.get("scene", "friends_out")
    scenes = _load_json("scenes.json")
    scene_def = scenes.get(scene, scenes.get("friends_out"))
    if not scene_def:
        return [_unavailable_plan(request, request.get("main_role", "PLAY"), request.get("requested_categories", []),
                                  "场景模板不可用，需要检查数据文件或放宽条件")]

    if logbook:
        logbook.add("排方案", "running",
                    f"按「{scene_def.get('label', scene)}」模板生成 2 个候选方案…")

    slots = [dict(slot) for slot in scene_def.get("slots", [])]
    sequence_slots = _slots_from_sequence(request)
    if sequence_slots:
        slots = sequence_slots
    raw_text = request.get("raw_text") or request.get("text") or ""
    if scene == "couple":
        date_preferences = set(request.get("date_preferences") or [])
        wants_food = request.get("date_wants_food") or "吃饭" in date_preferences or any(k in raw_text for k in ("吃饭", "餐厅", "正餐", "晚饭", "约饭"))
        if date_preferences and not wants_food:
            slots = [slot for slot in slots if slot.get("role") != "EAT"]

    # 用户原话点名的品类（如"剧本杀"）→ 锁定到对应 slot_role 的槽位上
    explicit_cats: list[dict] = request.get("explicit_categories", []) or []
    blocked_reason: tuple[str, list[str], str] | None = None

    # 为每个槽位准备候选列表
    slot_candidates: list[list[dict]] = []
    for slot in slots:
        role = slot["role"]
        want = slot.get("want")
        if scene == "couple" and not want:
            if role == "PLAY":
                date_preferences = set(request.get("date_preferences") or [])
                preferred = []
                if "看电影" in date_preferences:
                    preferred.append("电影院")
                if "拍照" in date_preferences:
                    preferred.extend(["展览", "景区"])
                if "散步" in date_preferences:
                    preferred.append("景区")
                want = preferred or ["电影院", "展览", "景区"]
            elif role == "EAT":
                want = ["西餐", "江浙菜", "甜品"]
        if scene == "stay_in" and role == "STAYIN":
            mode = request.get("stayin_mode")
            if slot.get("title") == "吃点什么":
                if mode in ("movie_snacks", "snacks_only"):
                    want = "闪购零食"
                elif mode == "movie_takeaway":
                    want = "外卖"
        # 若用户点名了 PLAY=剧本杀，则该槽 want 锁死为 ["剧本杀"]。
        # 同一 role 有多个槽时（如宅家两个 STAYIN 槽），只锁定落在该槽原始 want 范围内的品类。
        role_cats = [ec["category"] for ec in explicit_cats if ec["role"] == role]
        if role == "EAT" and not role_cats:
            cuisine = request.get("cuisine_preference")
            if isinstance(cuisine, list):
                cuisine = cuisine[0] if cuisine else None
            if cuisine and cuisine not in ("不限", "都可以", "都行", "随便", "any"):
                want = cuisine
        if role_cats:
            base_wants = _want_list(want)
            if base_wants:
                scoped_cats = [cat for cat in role_cats if cat in base_wants]
                if scoped_cats:
                    want = scoped_cats
                elif not (scene == "stay_in" and role == "STAYIN"):
                    want = role_cats
            else:
                want = role_cats
        cs = search_merchants(role, request, logbook, want=want,
                              exclude_ids=request.get("_rejected_ids", set()))
        if not cs and role_cats:
            reason = f"没有找到符合条件的{'/'.join(role_cats)}"
            flags = set((request.get("diet_limits") or []) + (request.get("safety_flags") or []))
            if "no_spicy" in flags:
                reason = f"没有找到符合不辣要求的{'/'.join(role_cats)}"
            if logbook:
                logbook.add("商户检索", "warning",
                            reason + "，不会自动换成无关品类")
            blocked_reason = (role, role_cats, reason)
        slot_candidates.append(cs)

    if blocked_reason:
        role, cats, reason = blocked_reason
        return [_unavailable_plan(request, role, cats, reason)]

    plans: list[dict] = []
    plan_a_ids: list[str] = []
    budget = int(request.get("budget_per_person", 150) or 150)
    party_size = int(request.get("party_size", 1) or 1)

    # 生成 2 个方案：A=综合最优；B=差异化（排除 A 用过的）
    for plan_idx, label in enumerate(["A", "B"]):
        steps: list[dict] = []
        total_cost = 0
        current_time = _to_min(request.get("start_time", "14:00"))
        used_ids: set[str] = set()
        valid = True

        for i, slot in enumerate(slots):
            role = slot["role"]
            available = [c for c in slot_candidates[i] if c["id"] not in used_ids]
            if plan_idx == 1 and plan_a_ids:
                diff = [c for c in available if c["id"] not in plan_a_ids]
                if diff:
                    available = diff
            if not available:
                valid = False
                break

            # 按剩余预算切槽：保证整条方案总价 ≤ 预算（B 方案放宽到 1.2x，允许略超）
            remaining_slots = len(slots) - i
            remaining_budget = budget - total_cost
            if remaining_slots > 0:
                elasticity = 1.0 if plan_idx == 0 else 1.2
                per_slot_cap = (remaining_budget / remaining_slots) * elasticity
                budget_filtered = [c for c in available if c.get("price", 0) <= per_slot_cap]
                if budget_filtered:
                    available = budget_filtered

            # 方案 A：用最终分排序；方案 B：偏好评分高的（拉开差异）
            if plan_idx == 0:
                available.sort(key=lambda x: x["_final_score"], reverse=True)
            else:
                available.sort(key=lambda x: (x.get("rating", 0), -x.get("price", 999)), reverse=True)
            if scene == "couple" and role == "PLAY":
                date_preferences = set(request.get("date_preferences") or [])
                preferred: list[dict] = []
                if plan_idx == 0 and "看电影" in date_preferences:
                    preferred = [c for c in available if c.get("category") == "电影院"]
                elif plan_idx == 1 and ("拍照" in date_preferences or "散步" in date_preferences):
                    preferred = [c for c in available if c.get("category") in ("展览", "景区")]
                if preferred:
                    available = preferred

            merchant = available[0]
            used_ids.add(merchant["id"])

            # 计算到达时间：第 i>0 个节点要加交通（线上节点不加）
            if i > 0 and role != "STAYIN" and steps:
                # 找上一个非 travel 节点的 area
                prev_area = request.get("origin_area") or request.get("home_area") or "待定"
                for s in reversed(steps):
                    if s.get("kind") in ("activity", "restaurant", "addon"):
                        prev_area = s.get("area", prev_area)
                        break
                tv = _travel(prev_area, merchant["area"])
                travel_mode = "walk" if tv.get("walk", 999) <= 15 else ("metro" if request.get("transport") == "public" and tv.get("metro") is not None else "taxi")
                travel_min = tv.get(travel_mode, tv.get("taxi", tv.get("walk", 0)))
                travel_cost = _travel_cost_per_person(tv, travel_mode, party_size)
                steps.append({
                    "kind": "travel",
                    "mode": travel_mode,
                    "minutes": travel_min,
                    "cost": travel_cost,
                    "from": prev_area,
                    "to": merchant["area"],
                    "start": _to_str(current_time),
                    "end": _to_str(current_time + travel_min),
                })
                total_cost += travel_cost
                current_time += travel_min

            duration = merchant.get("duration_minutes", 90)
            start = _to_str(current_time)
            end = _to_str(current_time + duration)

            kind = {
                "PLAY":   "activity",
                "EAT":    "restaurant",
                "STAYIN": "stayin",
                "ADDON":  "addon",
            }.get(role, "activity")

            step = {
                "kind": kind,
                "id": merchant["id"],
                "name": merchant["name"],
                "area": merchant["area"],
                "start": start,
                "end": end,
                "cost": merchant.get("price", 0),
                "rating": merchant.get("rating", 0),
                "category": merchant.get("category", ""),
                "image": merchant.get("image", ""),
                "review_count": merchant.get("review_count", 0),
                "review_snippet": merchant.get("review_snippet", ""),
                "tags": merchant.get("review_tags", []),
                "can_reserve": merchant.get("can_reserve", False),
                "queue_minutes": merchant.get("queue_minutes", 0),
                "is_promoted": merchant.get("is_promoted", False),
                "group_deal": merchant.get("group_deal"),
                "ad_bid": merchant.get("ad_bid", 0),
                "recommended_dishes": merchant.get("recommended_dishes", []),
                "flags": merchant.get("flags", {}),
                **_merchant_business_fields(merchant),
                "script_styles": merchant.get("script_styles", []),
                "player_counts": merchant.get("player_counts", []),
                "open_tables": merchant.get("open_tables", []),
                "difficulty": merchant.get("difficulty"),
                "horror_level": merchant.get("horror_level"),
                "newbie_friendly": merchant.get("newbie_friendly"),
                "dm_rating": merchant.get("dm_rating"),
                "slot_role": role,
                "slot_title": slot.get("title", ""),
            }
            if merchant.get("category") == "剧本杀":
                step["script_status"] = _match_script_table(merchant, request)
            steps.append(step)
            total_cost += merchant.get("price", 0)
            current_time += duration

        if not valid or not steps:
            continue

        start_min = _to_min(request.get("start_time", "14:00"))
        total_minutes = current_time - start_min

        # 每个槽位的备选 id（用于"换一个"）
        slot_alternatives: dict[str, list[str]] = {}
        for i, slot in enumerate(slots):
            role_key = slot["role"].lower()
            alts = [c["id"] for c in slot_candidates[i] if c["id"] not in used_ids][:3]
            if alts:
                slot_alternatives[f"{role_key}_{i}"] = alts

        plan = {
            "title": _make_title(steps, scene, plan_idx),
            "focus": _make_focus(steps, request),
            "steps": steps,
            "slot_alternatives": slot_alternatives,
            "total_cost_per_person": total_cost,
            "total_minutes": total_minutes,
            "start_time": request.get("start_time", "14:00"),
        }
        plan = _inject_birthday_delivery(plan, request, search_merchants)
        plan = _attach_meal_bridge(plan, request, search_merchants)
        if plan.get("long_lead_addon_hint") and "提前准备" not in plan.get("focus", ""):
            plan["focus"] = (plan.get("focus", "") + " · 可提前准备生日蛋糕/鲜花").strip(" ·")
        plan["matching_meta"] = _make_matching_meta(request, steps, slot_candidates)
        plan["commercial_recommendations"] = _make_commercial_recommendations(plan, request, search_merchants)
        if plan.get("meal_bridge_addon"):
            plan["commercial_recommendations"] = [plan["meal_bridge_addon"]] + plan["commercial_recommendations"]
        plan["optional_addons"] = plan["commercial_recommendations"]
        if total_cost > budget:
            plan["needs_user_confirm"] = True
            plan["budget_status"] = "over_budget"
            plan["budget_over_by"] = total_cost - budget
        else:
            plan["needs_user_confirm"] = False
            plan["budget_status"] = "within_budget"
            plan["budget_over_by"] = 0
        plan["score"] = score_plan(plan, request)
        plan["reason"] = _make_reason(plan, request)
        plan["risks"] = _make_risks(plan, request)
        plan_sig = tuple(s.get("id") for s in plan.get("steps", []) if s.get("kind") in ("activity", "restaurant", "stayin", "delivery", "addon"))
        if any(tuple(s.get("id") for s in p.get("steps", []) if s.get("kind") in ("activity", "restaurant", "stayin", "delivery", "addon")) == plan_sig for p in plans):
            continue
        plans.append(plan)

        if plan_idx == 0:
            plan_a_ids = [s["id"] for s in plan.get("steps", []) if s.get("kind") in ("activity", "restaurant", "stayin", "delivery", "addon")]

        if logbook:
            logbook.add("排方案", "success",
                        f"方案 {label}：「{plan['title']}」 人均 ¥{plan.get('total_cost_per_person', total_cost)}，"
                        f"{total_minutes // 60}h{total_minutes % 60}min，评分 {plan['score']['total']}")

    if not plans:
        if logbook:
            logbook.add("排方案", "warning", "未找到完美方案")
        if _has_explicit_requested_category(request):
            plans.append(_unavailable_plan(request, request.get("main_role", "PLAY"), request.get("requested_categories", []), "明确品类下没有可用候选，需要用户放宽条件"))
        else:
            plans.append(_fallback_plan(request))

    return plans


# ═══════════════════════════════════════════════════════════════════════════
# score_plan：100 分制
# ═══════════════════════════════════════════════════════════════════════════
def score_plan(plan: dict, request: dict, profile: dict | None = None) -> dict:
    """
    人群适配 /25  时间 /20  预算 /15  距离 /15  排队 /15  亮点 /10
    profile 命中偏好时额外加分（最高 +3）。
    """
    steps = plan.get("steps", [])
    prefs = request.get("preferences", [])
    budget = int(request.get("budget_per_person", 150) or 150)
    window = int(request.get("window_hours", 5) or 5) * 60

    # 聚合所有标签
    tag_text = ""
    for s in steps:
        if s.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery"):
            tag_text += " " + " ".join(s.get("tags", []) or []) + " " + s.get("category", "")

    # 人群适配
    hit = 0
    for p in prefs:
        if p == "photo" and any(k in tag_text for k in ["出片", "拍照", "网红"]):
            hit += 1
        elif p == "good_food":
            if any(s.get("rating", 0) >= 4.5 for s in steps if s.get("kind") in ("restaurant", "stayin")):
                hit += 1
        elif p == "easy_pace" and any(k in tag_text for k in ["低强度", "室内", "轻松", "安静"]):
            hit += 1
        elif p == "culture" and "文艺" in tag_text:
            hit += 1
        elif p == "kid_friendly":
            hit += 1
        elif p == "light_food" and any(k in tag_text for k in ["清淡", "轻食"]):
            hit += 1
        elif p == "relax" and any(k in tag_text for k in ["轻松", "安静", "方便"]):
            hit += 1
    people_fit = round(25 * min(1, hit / max(1, len(prefs))))

    # 时间
    total_min = plan.get("total_minutes", 0)
    over_min = total_min - window
    time_score = 20 if over_min <= 0 else max(8, 20 - round(over_min / 15))

    # 预算
    over_cost = plan.get("total_cost_per_person", 0) - budget
    budget_score = 15 if over_cost <= 0 else max(4, 15 - round(over_cost / 12))

    # 距离
    travel_mins = sum(s.get("minutes", 0) for s in steps if s.get("kind") == "travel")
    distance = 15 if travel_mins <= 15 else max(7, 15 - round(travel_mins / 4))

    # 排队
    max_queue = max(
        (s.get("queue_minutes", 0) for s in steps if s.get("kind") in ("activity", "restaurant")),
        default=0,
    )
    queue = 15 if max_queue <= 10 else max(5, 15 - round((max_queue - 10) / 4))

    # 亮点
    ratings = [s.get("rating", 0) for s in steps if s.get("kind") in ("activity", "restaurant", "stayin", "delivery")]
    avg_rating = sum(ratings) / max(1, len(ratings))
    hl = round((avg_rating - 4.0) * 10)
    if "出片" in tag_text or "网红" in tag_text:
        hl += 2
    hl = max(2, min(10, hl))

    # 画像额外加分
    profile_bonus = 0
    if profile:
        avoid = profile.get("avoid", [])
        if "排队" in avoid and max_queue <= 5:
            profile_bonus += 2
        prefers = profile.get("prefers", [])
        for w in prefers:
            if w in tag_text:
                profile_bonus += 1
        profile_bonus = min(3, profile_bonus)

    total = min(100, people_fit + time_score + budget_score + distance + queue + hl + profile_bonus)
    return {
        "total": total,
        "people_fit": people_fit,
        "time": time_score,
        "budget": budget_score,
        "distance": distance,
        "queue": queue,
        "highlight": hl,
        "profile_bonus": profile_bonus,
    }


# ═══════════════════════════════════════════════════════════════════════════
# replan：异常时局部重排
# ═══════════════════════════════════════════════════════════════════════════
def _business_positions(steps: list) -> list[tuple[int, int, dict]]:
    out: list[tuple[int, int, dict]] = []
    biz_idx = 0
    for raw_idx, step in enumerate(steps or []):
        if step.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery"):
            out.append((raw_idx, biz_idx, step))
            biz_idx += 1
    return out


def _segment_index_from_context(context: dict | None) -> int | None:
    context = context or {}
    value = context.get("affected_segment_index")
    if value is None:
        segment_id = context.get("affected_segment_id") or context.get("segment_id")
        if isinstance(segment_id, str) and segment_id.startswith("seg_"):
            try:
                value = int(segment_id.split("_", 1)[1]) - 1
            except Exception:
                value = None
    try:
        return int(value) if value is not None else None
    except Exception:
        return None


def _find_affected_step(steps: list, kind: str, context: dict | None) -> tuple[int, int, dict] | None:
    target_segment = _segment_index_from_context(context)
    positions = _business_positions(steps)
    if target_segment is not None:
        for raw_idx, biz_idx, step in positions:
            if biz_idx == target_segment and step.get("kind") == kind:
                return raw_idx, biz_idx, step
    for raw_idx, biz_idx, step in positions:
        if step.get("kind") == kind:
            return raw_idx, biz_idx, step
    return None


def _segment_summary(step: dict | str | None, segment_index: int | None = None) -> dict:
    if isinstance(step, str):
        return {"segment_index": segment_index, "time": step}
    if not isinstance(step, dict):
        return {}
    return {
        "segment_index": segment_index,
        "segment_id": f"seg_{segment_index + 1}" if isinstance(segment_index, int) else None,
        "kind": step.get("kind"),
        "role": step.get("slot_role") or {"activity": "PLAY", "restaurant": "EAT", "stayin": "STAYIN", "addon": "ADDON", "delivery": "ADDON"}.get(step.get("kind")),
        "id": step.get("id"),
        "name": step.get("name"),
        "category": step.get("category"),
        "area": step.get("area"),
        "start": step.get("start"),
        "end": step.get("end"),
        "cost": step.get("cost", step.get("price", 0)),
    }


def _kept_segment_summaries(steps: list, changed_business_indexes: set[int]) -> list[dict]:
    return [
        _segment_summary(step, biz_idx)
        for _, biz_idx, step in _business_positions(steps)
        if biz_idx not in changed_business_indexes
    ]


def _structured_replan_result(
    *,
    issue_type: str,
    changed_kind: str,
    affected_segment_index: int | None,
    before,
    after,
    old_steps: list,
    new_plan: dict,
    reason: str,
    still_ok: dict | None = None,
    needs_user_confirm: bool = False,
    budget_delta: int = 0,
    time_delta: int = 0,
    transport_note: str = "",
    warnings: list[str] | None = None,
    relaxation_options: list[str] | None = None,
) -> dict:
    changed_indexes = set()
    if isinstance(affected_segment_index, int):
        changed_indexes.add(affected_segment_index)
    changed_segments = []
    if isinstance(after, dict):
        changed_segments.append(_segment_summary(after, affected_segment_index))
    elif after is not None:
        changed_segments.append(_segment_summary(after, affected_segment_index))
    return {
        "issue_type": issue_type,
        "affected_segment_index": affected_segment_index,
        "affected_segment_id": f"seg_{affected_segment_index + 1}" if isinstance(affected_segment_index, int) else None,
        "original_segment": _segment_summary(before, affected_segment_index),
        "replacement_segment": _segment_summary(after, affected_segment_index),
        "kept_segments": _kept_segment_summaries(old_steps, changed_indexes),
        "changed_segments": changed_segments,
        "budget_delta": budget_delta,
        "time_delta": time_delta,
        "transport_note": transport_note,
        "needs_user_confirm": bool(needs_user_confirm),
        "reason": reason,
        "before": before,
        "after": after,
        "changed_kind": changed_kind,
        "still_ok": still_ok or {},
        "warnings": warnings or [],
        "relaxation_options": relaxation_options or [],
        "new_plan": new_plan,
    }


def replan(session: dict, exception_type: str, context: dict | None = None, logbook=None) -> dict:
    """
    exception_type ∈ {"restaurant_full","ticket_soldout","time_conflict"}。
    返回 {before, after, reason, still_ok, new_plan}。
    """
    chosen = session.get("chosen") or {}
    request = session.get("request") or {}
    context = context or {}
    context.setdefault("issue_type", exception_type)
    steps = chosen.get("steps", [])

    if logbook:
        label = {
            "restaurant_full": "餐厅满座",
            "ticket_soldout":  "活动门票售罄",
            "time_conflict":   "朋友说时间太赶",
        }.get(exception_type, exception_type)
        logbook.add("收到异常", "warning", f"触发异常：{label}")

    if exception_type == "restaurant_full":
        return _replan_one_node(chosen, request, steps, "restaurant", context, logbook)
    if exception_type == "ticket_soldout":
        return _replan_one_node(chosen, request, steps, "activity", context, logbook)
    if exception_type == "time_conflict":
        return _replan_time(chosen, request, steps, context, logbook)
    if exception_type == "budget_conflict":
        return _replan_budget(chosen, request, steps, context or {}, logbook)
    return _structured_replan_result(
        issue_type=exception_type,
        changed_kind="unknown",
        affected_segment_index=None,
        before=None,
        after=None,
        old_steps=steps,
        new_plan=chosen,
        reason=f"未知异常 {exception_type}",
        still_ok={},
        needs_user_confirm=True,
    )


def _replan_budget(chosen: dict, request: dict, steps: list, context: dict | None = None, logbook=None) -> dict:
    """Replace the most expensive business node with a cheaper same-category candidate."""
    from agent.catalog import search_merchants

    business = [
        (i, s) for i, s in enumerate(steps)
        if s.get("kind") in ("activity", "restaurant", "addon", "stayin")
    ]
    if not business:
        return {"before": None, "after": None, "changed_kind": "budget", "reason": "没有可替换节点",
                "still_ok": {}, "needs_user_confirm": True, "new_plan": chosen}

    old_idx, old_step = max(business, key=lambda item: item[1].get("cost", 0))
    role = old_step.get("slot_role") or {"activity": "PLAY", "restaurant": "EAT", "addon": "ADDON", "stayin": "STAYIN"}.get(old_step.get("kind"), "PLAY")
    rejected = set(request.get("_rejected_ids", set()) or set())
    rejected.add(old_step.get("id"))
    local_request = dict(request)
    local_request["budget_per_person"] = max(1, int(old_step.get("cost", 0) or 0) - 1)
    candidates = search_merchants(role, local_request, logbook=None, want=[old_step.get("category")], exclude_ids=rejected)
    candidates = [c for c in candidates if c.get("price", 0) < old_step.get("cost", 0)]
    candidates.sort(key=lambda c: (c.get("price", 0), -c.get("rating", 0)))
    if not candidates:
        return {
            "before": old_step,
            "after": None,
            "changed_kind": "budget",
            "reason": f"同品类「{old_step.get('category')}」没有更便宜且符合硬约束的备选，需发起人放宽预算或换品类",
            "still_ok": {"budget": False, "time": True, "distance": True},
            "needs_user_confirm": True,
            "relaxation_options": _relax_options(request, role, [old_step.get("category")]),
            "new_plan": chosen,
        }

    new_m = candidates[0]
    new_steps = list(steps)
    new_steps[old_idx] = {
        **old_step,
        "id": new_m["id"],
        "name": new_m["name"],
        "area": new_m["area"],
        "cost": new_m.get("price", 0),
        "rating": new_m.get("rating", 0),
        "category": new_m.get("category"),
        "image": new_m.get("image", ""),
        "tags": new_m.get("review_tags", []),
        "can_reserve": new_m.get("can_reserve", False),
        "queue_minutes": new_m.get("queue_minutes", 0),
        "group_deal": new_m.get("group_deal"),
        "review_count": new_m.get("review_count", 0),
        "review_snippet": new_m.get("review_snippet", ""),
        "recommended_dishes": new_m.get("recommended_dishes", []),
        "flags": new_m.get("flags", {}),
        **_merchant_business_fields(new_m),
    }
    total_cost = sum(s.get("cost", 0) for s in new_steps if s.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery"))
    new_plan = {**chosen, "steps": new_steps, "total_cost_per_person": total_cost}
    new_plan["score"] = score_plan(new_plan, request)
    return {
        "before": old_step,
        "after": new_steps[old_idx],
        "changed_kind": "budget",
        "reason": f"已把「{old_step.get('name')}」换成更便宜的「{new_m.get('name')}」，其它节点不动，人均变为 ¥{total_cost}",
        "still_ok": {"budget": total_cost <= request.get("budget_per_person", 999), "time": True, "distance": True},
        "needs_user_confirm": total_cost > request.get("budget_per_person", 999),
        "new_plan": new_plan,
    }


def _replan_one_node(chosen: dict, request: dict, steps: list, kind: str, context: dict | None = None, logbook=None) -> dict:
    """局部替换一个节点（restaurant 或 activity）。"""
    from agent.catalog import search_merchants

    if logbook:
        ko_label = "餐厅" if kind == "restaurant" else "活动"
        logbook.add("局部重排", "running",
                    f"保留其它节点，正在同商圈检索备选{ko_label}…")

    issue_type = (context or {}).get("issue_type") or ("restaurant_full" if kind == "restaurant" else "ticket_soldout")
    # 找到坏掉的节点：优先使用前端传入的行程段，否则回退到同类第一个节点。
    target = _find_affected_step(steps, kind, context)
    if not target:
        return _structured_replan_result(
            issue_type=issue_type,
            changed_kind=kind,
            affected_segment_index=_segment_index_from_context(context),
            before=None,
            after=None,
            old_steps=steps,
            new_plan=chosen,
            reason=f"未找到 {kind} 节点，无法局部重排",
            still_ok={},
            needs_user_confirm=True,
            warnings=["局部重排失败：当前行程中没有对应类型的可替换段"],
        )
    old_idx, old_segment_index, old_step = target

    # 备选（也要尊重用户原话点名的品类）
    role = "EAT" if kind == "restaurant" else "PLAY"
    explicit_cats = request.get("explicit_categories", []) or []
    role_cats = [ec["category"] for ec in explicit_cats if ec["role"] == role]
    rejected = set(request.get("_rejected_ids", set()) or set())
    rejected.add(old_step["id"])
    context = context or {}
    local_request = dict(request)
    location_state = context.get("location_state", "before_departure")
    anchor_area = context.get("current_area") or old_step.get("area", "")
    if location_state in ("near_current_merchant", "inside_mall", "after_previous_slot") and anchor_area:
        local_request["home_area"] = anchor_area
        local_request["distance_tolerance"] = "same_area"
    elif location_state == "in_transit" and anchor_area:
        local_request["home_area"] = anchor_area
        local_request["distance_tolerance"] = "nearby"
    if role == "EAT" and not role_cats:
        local_request.pop("cuisine_preference", None)
    candidates = search_merchants(role, local_request, logbook=None,
                                  want=role_cats if role_cats else None,
                                  exclude_ids=rejected)
    if not candidates and role_cats:
        return _structured_replan_result(
            issue_type=issue_type,
            changed_kind=kind,
            affected_segment_index=old_segment_index,
            before=old_step,
            after=None,
            old_steps=steps,
            new_plan=chosen,
            reason=f"同位置语境下没有可替换的{'/'.join(role_cats)}，需要发起人放宽条件",
            still_ok={"budget": False, "time": True, "distance": False},
            needs_user_confirm=True,
            relaxation_options=_relax_options(request, role, role_cats),
            warnings=["同类备选不足，已保留原行程等待用户放宽条件"],
        )
    # 优先同商圈、价格接近原节点
    old_area = old_step.get("area", "")
    old_cost = old_step.get("cost", 0)
    candidates.sort(key=lambda x: (
        0 if x.get("area") == old_area else 1,
        abs(x.get("price", 0) - old_cost),
        -x.get("rating", 0),
    ))
    if not candidates:
        return _structured_replan_result(
            issue_type=issue_type,
            changed_kind=kind,
            affected_segment_index=old_segment_index,
            before=old_step,
            after=None,
            old_steps=steps,
            new_plan=chosen,
            reason="无合适备选，当前仅能保留原节点并提示用户放宽条件",
            still_ok={"budget": False, "time": True, "distance": False},
            needs_user_confirm=True,
            warnings=["局部重排未找到可执行替代方案"],
        )

    new_m = candidates[0]
    new_steps = list(steps)
    new_steps[old_idx] = {
        **old_step,
        "id": new_m["id"],
        "name": new_m["name"],
        "area": new_m["area"],
        "cost": new_m["price"],
        "rating": new_m["rating"],
        "category": new_m["category"],
        "image": new_m.get("image", ""),
        "tags": new_m.get("review_tags", []),
        "can_reserve": new_m.get("can_reserve", False),
        "queue_minutes": new_m.get("queue_minutes", 0),
        "is_promoted": new_m.get("is_promoted", False),
        "group_deal": new_m.get("group_deal"),
        "review_count": new_m.get("review_count", 0),
        "review_snippet": new_m.get("review_snippet", ""),
        "ad_bid": new_m.get("ad_bid", 0),
        "recommended_dishes": new_m.get("recommended_dishes", []),
        "flags": new_m.get("flags", {}),
        **_merchant_business_fields(new_m),
        "script_styles": new_m.get("script_styles", []),
        "player_counts": new_m.get("player_counts", []),
        "open_tables": new_m.get("open_tables", []),
        "difficulty": new_m.get("difficulty"),
        "horror_level": new_m.get("horror_level"),
        "newbie_friendly": new_m.get("newbie_friendly"),
        "dm_rating": new_m.get("dm_rating"),
        "script_status": _match_script_table(new_m, request) if new_m.get("category") == "剧本杀" else None,
    }

    # 若区域变了，更新前一个 travel 节点
    transport_note = "替换店铺仍在同商圈，交通不变。"
    if old_idx > 0 and new_steps[old_idx - 1].get("kind") == "travel" and new_m["area"] != old_area:
        prev_area = new_steps[old_idx - 1].get("from")
        tv = _travel(prev_area, new_m["area"])
        mode = "walk" if tv["walk"] <= 15 else "taxi"
        new_steps[old_idx - 1] = {
            **new_steps[old_idx - 1],
            "mode": mode,
            "minutes": tv[mode],
            "to": new_m["area"],
        }
        transport_note = f"替换地点从 {old_area} 调整到 {new_m['area']}，上一段交通已按 {mode} 重新估算。"
    elif new_m["area"] != old_area:
        transport_note = f"替换地点从 {old_area} 调整到 {new_m['area']}，需以现场位置重新确认交通。"

    total_cost = sum(s.get("cost", 0) for s in new_steps if s.get("kind") in ("activity", "restaurant", "stayin", "addon", "delivery"))
    new_plan = {**chosen, "steps": new_steps, "total_cost_per_person": total_cost}
    new_plan["score"] = score_plan(new_plan, request)
    needs_user_confirm = total_cost > request.get("budget_per_person", 999)

    role_label = "餐厅" if kind == "restaurant" else "活动"
    issue_label = "已满座" if kind == "restaurant" else "门票已售罄"
    reason = (f"原「{old_step['name']}」{issue_label}。已就近换到 {new_m['area']} 的「{new_m['name']}」"
              f"（评分 {new_m['rating']}），其它节点不动，"
              f"人均变为 ¥{total_cost}"
              f"{'，仍在预算内' if total_cost <= request.get('budget_per_person', 999) else '，略超预算'}。")

    if logbook:
        logbook.add("重排完成", "success", reason)

    return _structured_replan_result(
        issue_type=issue_type,
        changed_kind=kind,
        affected_segment_index=old_segment_index,
        before=old_step,
        after=new_steps[old_idx],
        old_steps=steps,
        new_plan=new_plan,
        reason=reason,
        still_ok={
            "budget": not needs_user_confirm,
            "time":   True,
            "distance": True,
        },
        needs_user_confirm=needs_user_confirm,
        budget_delta=total_cost - chosen.get("total_cost_per_person", total_cost),
        time_delta=0,
        transport_note=transport_note,
        warnings=["替代方案略超预算，需要发起人确认"] if needs_user_confirm else [],
    )


def _replan_time(chosen: dict, request: dict, steps: list, context: dict | None = None, logbook=None) -> dict:
    """整条行程顺延。节点不动，仅改时间轴。"""
    context = context or {}
    try:
        shift_minutes = int(context.get("shift_minutes") or 60)
    except Exception:
        shift_minutes = 60
    shift_minutes = max(15, min(180, shift_minutes))
    if logbook:
        logbook.add("局部重排", "running", f"整条行程顺延 {shift_minutes} 分钟，重新计算时间轴…")
    old_start = chosen.get("start_time", request.get("start_time", "14:00"))
    new_start = _to_str(_to_min(old_start) + shift_minutes)

    new_steps: list[dict] = []
    current = _to_min(new_start)
    for s in steps:
        kind = s.get("kind", "")
        if kind == "travel":
            new_s = {**s, "start": _to_str(current),
                     "end": _to_str(current + s.get("minutes", 0))}
            current += s.get("minutes", 0)
        else:
            duration = _to_min(s.get("end", "15:00")) - _to_min(s.get("start", "14:00"))
            new_s = {**s, "start": _to_str(current), "end": _to_str(current + duration)}
            current += duration
        new_steps.append(new_s)

    new_plan = {**chosen, "steps": new_steps, "start_time": new_start}
    new_plan["score"] = score_plan(new_plan, request)
    warnings: list[str] = []
    if any(_to_min(s.get("end", "00:00")) >= 24 * 60 for s in new_steps if s.get("kind") != "travel"):
        warnings.append("顺延后部分节点接近或跨过午夜，需要发起人再次确认场次/营业时间。")

    reason = (f"收到反馈「时间太赶」。已把整条行程顺延 {shift_minutes} 分钟——"
              f"出发从 {old_start} 改到 {new_start}，活动和餐厅原样保留，总时长不变。")
    if logbook:
        logbook.add("重排完成", "success", reason)

    return _structured_replan_result(
        issue_type="time_conflict",
        changed_kind="time",
        affected_segment_index=_segment_index_from_context({}),
        before=old_start,
        after=new_start,
        old_steps=steps,
        new_plan=new_plan,
        reason=reason,
        still_ok={"budget": True, "time": not warnings, "distance": True},
        needs_user_confirm=bool(warnings),
        budget_delta=0,
        time_delta=shift_minutes,
        transport_note="地点不变，交通方式不变；仅整体顺延时间。",
        warnings=warnings,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 辅助：标题 / 焦点 / 推荐理由 / 风险
# ═══════════════════════════════════════════════════════════════════════════
def _make_matching_meta(request: dict, steps: list[dict], slot_candidates: list[list[dict]]) -> dict:
    merchants = _load_json("merchants.json")
    if isinstance(merchants, dict):
        merchants = merchants.get("merchants", [])
    if not isinstance(merchants, list):
        merchants = []
    area = request.get("home_area")
    budget = int(request.get("budget_per_person") or 0)
    selected_ids = [s.get("id") for s in steps if s.get("id")]
    candidates = [m for group in slot_candidates for m in group]
    category_candidates = len(candidates)
    area_candidates = [m for m in candidates if not area or m.get("area") in (area, "线上")]
    budget_candidates = [m for m in area_candidates if not budget or int(m.get("price") or 0) <= budget]
    constraints = request.get("constraints") or {}
    hard_limits = constraints.get("hard_constraints") or constraints.get("limits") or []
    return {
        "candidate_pool_size": len(merchants),
        "filtered_by_area_count": len(area_candidates),
        "filtered_by_category_count": category_candidates,
        "filtered_by_budget_count": len(budget_candidates),
        "filtered_by_constraints": hard_limits,
        "selected_merchant_ids": selected_ids,
    }


def _make_title(steps: list, scene: str, plan_idx: int) -> str:
    return "Plan A" if plan_idx == 0 else "Plan B"


def _make_focus(steps: list, request: dict) -> str:
    bits: list[str] = []
    prefs = request.get("preferences", [])
    has_food_step = any(s.get("kind") in ("restaurant", "stayin", "delivery") for s in steps)
    date_prefs = [x for x in (request.get("date_preferences") or []) if x]
    if date_prefs:
        bits.append("包含：" + "、".join(date_prefs[:4]))
    areas = []
    for s in steps:
        area = s.get("area")
        if area and area not in ("线上", "待定") and area not in areas:
            areas.append(area)
    if areas:
        bits.append("区域：" + "、".join(areas[:2]))
    if request.get("start_time"):
        bits.append(f"开始：{request['start_time']}")
    duration = 0
    for s in steps:
        if s.get("kind") not in ("activity", "restaurant", "stayin", "delivery", "addon"):
            continue
        if s.get("duration_minutes"):
            duration += int(s.get("duration_minutes") or 0)
        elif s.get("start") and s.get("end"):
            duration += max(0, _to_min(s.get("end")) - _to_min(s.get("start")))
    if not duration:
        try:
            duration = int(request.get("window_hours") or 0) * 60
        except Exception:
            duration = 0
    if duration:
        bits.append(f"时长约{round(duration / 60, 1)}小时")
    if request.get("budget_per_person"):
        bits.append(f"预算¥{request['budget_per_person']}/人")
    categories = []
    for s in steps:
        cat = s.get("category")
        if cat and cat not in categories:
            categories.append(cat)
    if categories:
        bits.append("品类：" + "、".join(categories[:2]))
    if "light_food" in prefs and has_food_step:
        bits.append("忌口：清淡")
    if request.get("script_style") and request.get("script_style") != "不限":
        bits.append(request["script_style"])
    cuisine = request.get("cuisine_preference")
    if cuisine and cuisine not in ("不限", "都可以", "any"):
        bits.append(str(cuisine))
    for s in steps:
        if s.get("category") == "剧本杀":
            status = s.get("script_status") or {}
            if status.get("state_label"):
                bits.append(status["state_label"])
            break
    if not bits:
        bits.append("按已确认条件生成")
    return " · ".join(bits[:3])


def _make_commercial_recommendations(plan: dict, request: dict, search_merchants) -> list[dict]:
    """
    生成非必选的商业推荐：用户没要求也可以直接给，但不计入主行程预算。
    典型场景：打完剧本杀后顺手给一张附近餐厅/奶茶推荐卡。
    """
    if request.get("scene") not in ("play_only", "friends_out", "couple"):
        return []
    if not _allows_after_play_commerce(request):
        return []
    anchor = None
    for step in reversed(plan.get("steps", [])):
        if step.get("kind") in ("activity", "restaurant"):
            anchor = step
            break
    if not anchor or anchor.get("area") == "线上":
        return []

    local_req = dict(request)
    local_req["home_area"] = anchor.get("area", request.get("home_area", "新街口"))
    local_req["distance_tolerance"] = "same_area"
    local_req["_rejected_ids"] = set(request.get("_rejected_ids", set()) or set())
    out: list[dict] = []

    if request.get("scene") == "play_only":
        eats = search_merchants("EAT", local_req, logbook=None, want=None,
                                exclude_ids=local_req.get("_rejected_ids", set()))
        if eats:
            m = eats[0]
            out.append({
                "type": "meal_after_play",
                "title": "散场可顺手订饭",
                "id": m["id"],
                "name": m["name"],
                "category": m["category"],
                "area": m["area"],
                "price": m.get("price", 0),
                "rating": m.get("rating", 0),
                "reason": f"离活动点近，评分 {m.get('rating', 0)}，不进入主预算，适合散场再决定。",
            })

    addons = search_merchants("ADDON", local_req, logbook=None, want=["奶茶", "咖啡", "甜品", "冰淇淋"],
                              exclude_ids=local_req.get("_rejected_ids", set()))
    if addons:
        m = addons[0]
        out.append({
            "type": "small_addon",
            "title": "路上加一杯",
            "id": m["id"],
            "name": m["name"],
            "category": m["category"],
            "area": m["area"],
            "price": m.get("price", 0),
            "rating": m.get("rating", 0),
            "reason": "不占太多时间，适合等人、散场或转场时顺手买。",
        })

    return out[:2]


def _make_reason(plan: dict, request: dict) -> str:
    bits: list[str] = []
    cost = plan.get("total_cost_per_person", 0)
    budget = int(request.get("budget_per_person", 150) or 150)
    if cost <= budget:
        bits.append(f"人均 <b>¥{cost}</b>，在 ¥{budget} 预算内")
    else:
        bits.append(f"人均 ¥{cost}，略超预算 ¥{cost - budget}")

    travel_mins = sum(s.get("minutes", 0) for s in plan.get("steps", []) if s.get("kind") == "travel")
    offline_nodes = [s for s in plan.get("steps", []) if s.get("kind") in ("activity", "restaurant", "addon", "delivery") and s.get("area") != "线上"]
    if travel_mins == 0:
        bits.append("全程在线、足不出户" if not offline_nodes else "单点直达，不需要跨商圈折腾")
    elif travel_mins <= 15:
        bits.append(f"两站距离近、步行 {travel_mins} 分钟可达，照顾「不想太累」")
    elif travel_mins <= 30:
        bits.append(f"两站间打车约 {travel_mins} 分钟")
    else:
        bits.append(f"两站之间打车约 {travel_mins} 分钟，略远")

    for s in plan.get("steps", []):
        if s.get("kind") == "restaurant":
            if s.get("queue_minutes", 99) <= 10 and s.get("can_reserve"):
                bits.append("餐厅可预约、晚上基本不排队")
            cuisine = request.get("cuisine_preference")
            if cuisine and cuisine != "不限" and s.get("category") == cuisine:
                bits.append(f"菜系锁定为「{cuisine}」，没有混推其它餐厅")
            break

    if plan.get("birthday_delivery"):
        bits.append("生日场景已自动安排蛋糕/鲜花提前送达餐厅，展示跨品类履约")

    for s in plan.get("steps", []):
        if s.get("category") == "剧本杀":
            status = s.get("script_status") or {}
            style = status.get("style") or request.get("script_style")
            label = status.get("state_label")
            if style and style != "不限":
                bits.append(f"剧本杀偏好匹配「{style}」")
            if label:
                bits.append(f"拼本状态：{label}")
            break

    if request.get("origin_mode") == "separate":
        bits.append("多人各自出发，优先选中心/交通折中位置")

    all_tags = " ".join([" ".join(s.get("tags", []) or []) for s in plan.get("steps", [])])
    if "出片" in all_tags or "拍照" in all_tags:
        bits.append("活动 / 餐厅都适合拍照")

    hrs = f"{plan.get('total_minutes', 0) / 60:.1f}"
    bits.append(f"全程约 {hrs} 小时，落在你的时间窗口里")
    return "；".join(bits) + "。"


def _make_risks(plan: dict, request: dict) -> list[str]:
    r: list[str] = []
    if plan.get("total_cost_per_person", 0) > request.get("budget_per_person", 150):
        r.append("人均略超预算")
    for s in plan.get("steps", []):
        if s.get("kind") == "restaurant" and s.get("queue_minutes", 0) > 10:
            r.append(f"餐厅约需排队 {s['queue_minutes']} 分钟")
            break
    for s in plan.get("steps", []):
        if s.get("category") != "剧本杀":
            continue
        status = s.get("script_status") or {}
        label = status.get("state_label", "")
        if "暂无" in label:
            r.append(f"当前没有完全匹配的在拼本，已同步店家；若{status.get('deadline', '截止前')}仍未成局，建议改 {status.get('fallback', '密室/桌游')}")
        elif "正在拼" in label:
            r.append(f"店家正在拼「{status.get('style', '剧本杀')}」，截止 {status.get('deadline', '开场前')} 未拼满则建议切换密室/桌游")
        break
    if "no_cilantro" in (request.get("diet_limits") or []):
        r.append("香菜这类细忌口需要下单备注，当前商户标签无法完全自动过滤")
    travel_mins = sum(s.get("minutes", 0) for s in plan.get("steps", []) if s.get("kind") == "travel")
    if travel_mins >= 20:
        r.append("晚高峰打车可能略堵")
    return r


def _fallback_plan(request: dict) -> dict:
    """所有候选都拿不出时的最终兜底——免费市集 + 简餐。"""
    start = request.get("start_time", "14:00")
    sm = _to_min(start)
    steps = [
        {"kind": "activity", "id": "m_005", "name": "屋顶花园市集", "area": "新街口",
         "start": _to_str(sm + 30), "end": _to_str(sm + 90),
         "cost": 0, "rating": 4.5, "category": "市集", "image": "🎪",
         "tags": ["免费", "出片"], "can_reserve": False, "queue_minutes": 0,
         "is_promoted": False, "slot_role": "PLAY", "slot_title": "先去玩"},
        {"kind": "travel", "mode": "walk", "minutes": 10, "from": "新街口", "to": "新街口",
         "start": _to_str(sm + 90), "end": _to_str(sm + 100)},
        {"kind": "restaurant", "id": "m_018", "name": "巷子咖啡馆", "area": "新街口",
         "start": _to_str(sm + 100), "end": _to_str(sm + 160),
         "cost": 62, "rating": 4.4, "category": "简餐", "image": "🥗",
         "tags": ["出片", "不排队"], "can_reserve": True, "queue_minutes": 0,
         "is_promoted": False, "slot_role": "EAT", "slot_title": "再去吃"},
    ]
    plan = {
        "title": "轻松兜底 Plan A",
        "focus": "免费市集 · 不排队 · 轻松",
        "steps": steps,
        "slot_alternatives": {},
        "total_cost_per_person": 62,
        "total_minutes": 160,
        "start_time": start,
    }
    plan["score"] = score_plan(plan, request)
    plan["reason"] = "兜底方案：免费市集 + 简餐，预算友好，不排队。"
    plan["risks"] = ["这是兜底方案，可能不是最优匹配"]
    return plan


if __name__ == "__main__":
    from agent.logbook import LogBook
    log = LogBook()

    req = {
        "scene": "friends_out",
        "party_size": 4,
        "has_kid": False,
        "transport": "public",
        "start_time": "14:00",
        "window_hours": 5,
        "home_area": "新街口",
        "budget_per_person": 150,
        "preferences": ["photo", "good_food", "easy_pace"],
        "hard_limits": ["no_evening_queue", "stay_near"],
    }

    print("\n=== 测试朋友局方案生成 ===")
    plans = build_itinerary(req, log)
    for i, p in enumerate(plans):
        print(f"\n方案 {chr(65+i)}: {p['title']} (评分 {p['score']['total']})")
        print(f"  聚焦：{p['focus']}")
        for s in p["steps"]:
            if s["kind"] == "travel":
                print(f"    [{s['mode']} {s['minutes']}min] {s['from']}→{s['to']}")
            else:
                print(f"    {s['start']}-{s['end']} {s['name']} ({s['category']}) ¥{s['cost']}")
        print(f"  人均 ¥{p['total_cost_per_person']}，{p['total_minutes']}min")
        print(f"  理由：{p['reason']}")

    print("\n\n=== 测试 replan: 餐厅满座 ===")
    session = {"chosen": plans[0], "request": req}
    result = replan(session, "restaurant_full", {"location_state": "before_departure"}, log)
    print(f"  {result['reason']}")
    print(f"  新人均 ¥{result['new_plan']['total_cost_per_person']}")

    print("\n=== 日志 ===")
    log.print_all()
