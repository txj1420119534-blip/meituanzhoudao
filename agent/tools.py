"""
tools.py —— 所有 Mock 工具函数。
返回固定外壳 {"ok","data","message"}；失败也返回 dict，绝不抛异常。
内部 sleep 0.3~0.8 秒模拟接口延迟（硬上限 0.8s）。
"""
import sys
import os
import json
import time
import random
import string

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [] if filename == "merchants.json" else {}


def _gen_order_id(prefix: str = "MT") -> str:
    """生成模拟订单号，带美团式前缀（MT/AC/RS/SY）。"""
    num = "".join(random.choices(string.digits, k=8))
    return f"{prefix}{num}"


def _to_min(t: str) -> int:
    if isinstance(t, (int, float)):
        t = f"{int(t):02d}:00"
    elif not isinstance(t, str):
        t = "00:00"
    elif ":" not in t and t.isdigit():
        t = f"{int(t):02d}:00"
    h, m = (t or "00:00").split(":")
    return int(h) * 60 + int(m)


def _sleep_mock():
    """模拟接口延迟（硬上限 0.8s）。"""
    time.sleep(random.uniform(0.3, 0.8))


def _find(merchant_id: str) -> dict | None:
    for m in _load_json("merchants.json"):
        if m["id"] == merchant_id:
            return m
    return None


# ─────────────────────────────────────────────────────────────────
# Tool 1：查可用性（座位 / 余票 / 排队）
# ─────────────────────────────────────────────────────────────────
def check_availability(merchant_id: str, time_str: str, party_size: int, logbook=None) -> dict:
    if logbook:
        logbook.add("查询余位", "running",
                    f"正在检查商户 {merchant_id} 在 {time_str} 是否有位…")
    _sleep_mock()
    target = _find(merchant_id)
    if not target:
        msg = f"未找到商户 {merchant_id}"
        if logbook:
            logbook.add("查询余位", "error", msg)
        return {"ok": False, "data": None, "message": msg}

    slot_role = target["slot_role"]
    available = False
    queue = target.get("queue_minutes", 0)
    stock = target.get("stock", 0)
    slots = target.get("slots", [])

    if slot_role in ("PLAY", "STAYIN", "ADDON"):
        if stock > 0 and (not slots or time_str in slots):
            available = True
        elif slot_role in ("PLAY", "ADDON") and stock > 0 and slots:
            target_min = _to_min(time_str)
            nearest = min(slots, key=lambda x: abs(_to_min(x) - target_min))
            if abs(_to_min(nearest) - target_min) <= 30:
                available = True
    elif slot_role == "EAT":
        if stock > 0 and (not slots or time_str in slots):
            available = True
        elif stock > 0 and slots:
            target_min = _to_min(time_str)
            nearest = min(slots, key=lambda x: abs(_to_min(x) - target_min))
            if abs(_to_min(nearest) - target_min) <= 30:
                available = True

    data = {
        "merchant_id": merchant_id,
        "name": target["name"],
        "available": available,
        "queue_minutes": queue,
        "time": time_str,
    }
    category = target.get("category", "")
    if category == "电影院":
        status_text = "有票" if available else "无票"
        wait_text = "出票/入场约"
    elif slot_role == "EAT":
        status_text = "有位" if available else "无位"
        wait_text = "需排队约"
    else:
        status_text = "有位/有票" if available else "无位/无票"
        wait_text = "等候约"
    msg = f"{target['name']}：{status_text}"
    if available and queue > 0:
        msg += f"，{wait_text} {queue} 分钟"
    if logbook:
        logbook.add("查询余位", "success" if available else "warning", msg)
    return {"ok": True, "data": data, "message": msg}


# ─────────────────────────────────────────────────────────────────
# Tool 2：查交通时间
# ─────────────────────────────────────────────────────────────────
def get_travel_time(from_area: str, to_area: str, logbook=None) -> dict:
    if logbook:
        logbook.add("查询交通", "running",
                    f"正在查询 {from_area} → {to_area} 的交通…")
    time.sleep(random.uniform(0.2, 0.5))
    travel = _load_json("travel.json")
    key = f"{from_area}->{to_area}"
    if key not in travel:
        key = f"{to_area}->{from_area}"
    data = travel.get(key, {"walk": 60, "taxi": 22, "metro": 30})
    msg = f"{from_area} → {to_area}：步行 {data['walk']}min / 打车 {data['taxi']}min / 地铁 {data['metro']}min"
    if logbook:
        logbook.add("查询交通", "success", msg)
    return {"ok": True, "data": data, "message": msg}


# ─────────────────────────────────────────────────────────────────
# Tool 3：模拟下单 / 预约
# ─────────────────────────────────────────────────────────────────
def book_item(merchant_id: str, time_str: str, party_size: int, logbook=None) -> dict:
    if logbook:
        logbook.add("模拟预订", "running",
                    f"正在为 {merchant_id} 的 {time_str} 场次下单…")
    _sleep_mock()
    target = _find(merchant_id)
    if not target:
        msg = f"未找到商户 {merchant_id}"
        if logbook:
            logbook.add("模拟预订", "error", msg)
        return {"ok": False, "data": None, "message": msg}

    role = target["slot_role"]
    prefix = {"EAT": "RS", "PLAY": "AC", "STAYIN": "SY", "ADDON": "AD"}.get(role, "MT")
    order_id = _gen_order_id(prefix)
    data = {
        "order_id": order_id,
        "merchant_id": merchant_id,
        "name": target["name"],
        "time": time_str,
        "party_size": party_size,
        "status": "confirmed",
    }
    msg = f"{target['name']} 预订成功，订单号 {order_id}"
    if logbook:
        logbook.add("模拟预订", "success", msg)
    return {"ok": True, "data": data, "message": msg}


# ─────────────────────────────────────────────────────────────────
# Tool 4：生成群聊分享卡（LLM 出场点 2/2）
# ─────────────────────────────────────────────────────────────────
def compose_share_card(plan: dict, logbook=None) -> dict:
    """先试 LLM 润色，失败/超时走规则模板。永远返回有 text 的 dict。"""
    if logbook:
        logbook.add("生成分享卡", "running", "正在生成发到群里的方案文案…")
    time.sleep(random.uniform(0.3, 0.6))

    # 尝试 LLM
    text = _llm_share_card(plan)
    if text:
        if logbook:
            logbook.add("生成分享卡", "success", "已生成群聊文案（LLM 润色）")
        return {"ok": True, "data": {"text": text, "method": "llm"}, "message": "已生成"}

    # 模板兜底
    text = _template_share_card(plan)
    if logbook:
        logbook.add("生成分享卡", "success", "已生成群聊文案（模板兜底）")
    return {"ok": True, "data": {"text": text, "method": "template"}, "message": "已生成"}


def _llm_share_card(plan: dict) -> str | None:
    try:
        from agent.llm import ask_llm
        prompt = (
            "请把以下行程方案变成一段简洁、轻松的群聊消息，像在和朋友说话。\n"
            "要求：\n"
            "1. 第一句先把出发时间说清楚\n"
            "2. 每个节点单独一行，写时间和名称（活动 / 餐厅 / 顺路）\n"
            "3. 最后写人均预算和总时长\n"
            "4. 末尾让朋友回个👌就行\n"
            "5. 不要 markdown 不要列表符号，纯文本，用换行分行\n\n"
            f"方案 JSON：\n{json.dumps(plan, ensure_ascii=False)}"
        )
        raw = ask_llm(prompt, timeout=5)
        if raw and len(raw.strip()) > 20:
            return raw.strip()
    except Exception:
        return None
    return None


def _template_share_card(plan: dict) -> str:
    steps = plan.get("steps", [])
    start_time = plan.get("start_time", "14:00")
    cost = plan.get("total_cost_per_person", 0)
    total_min = plan.get("total_minutes", 0)
    hrs = f"{total_min / 60:.1f}"

    lines = [f"搞定啦，{start_time} 出发 👇\n"]
    for s in steps:
        kind = s.get("kind", "")
        if kind == "travel":
            mode = "步行" if s.get("mode") == "walk" else "打车"
            lines.append(f"  {mode}约 {s.get('minutes', 0)} 分钟")
        elif kind == "activity":
            lines.append(f"{s.get('start', '')}  先去【{s.get('name', '')}】（{s.get('area', '')}）")
        elif kind == "restaurant":
            lines.append(f"{s.get('start', '')}  到【{s.get('name', '')}】吃饭，已订座")
        elif kind == "delivery":
            lines.append(f"{s.get('start', '')}  【{s.get('name', '')}】提前送到{s.get('target_name', '餐厅')}")
        elif kind == "stayin":
            lines.append(f"{s.get('start', '')}  在线享受【{s.get('name', '')}】")
        elif kind == "addon":
            lines.append(f"散场顺路【{s.get('name', '')}】来一份")

    lines.append(f"\n人均 ¥{cost}，全程约 {hrs} 小时")
    lines.append("觉得 OK 就回个 👌")
    return "\n".join(lines)


if __name__ == "__main__":
    from agent.logbook import LogBook
    log = LogBook()

    print("\n=== check_availability ===")
    r = check_availability("m_013", "18:00", 4, log)
    print(f"  {r}")

    print("\n=== get_travel_time ===")
    r = get_travel_time("新街口", "老门东", log)
    print(f"  {r}")

    print("\n=== book_item ===")
    r = book_item("m_014", "18:00", 4, log)
    print(f"  {r}")

    print("\n=== compose_share_card ===")
    fake_plan = {
        "steps": [
            {"kind": "activity", "name": "城市影像展", "area": "新街口", "start": "14:30", "end": "16:00"},
            {"kind": "travel", "mode": "walk", "minutes": 12},
            {"kind": "restaurant", "name": "院子里", "area": "新街口", "start": "17:30", "end": "19:00"},
        ],
        "start_time": "14:00",
        "total_cost_per_person": 146,
        "total_minutes": 300,
    }
    r = compose_share_card(fake_plan, log)
    print(f"  文案：\n{r['data']['text']}")

    print("\n=== 日志 ===")
    log.print_all()
