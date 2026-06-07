"""
category_schema.py —— 业务品类、子类和口语信号的统一归一层。

这里不直接做推荐，只回答两件事：
1. 用户说的黑话/口语，稳定映射成品类、子类、忌口、距离偏好等字段。
2. 提供 parser/clarify/catalog 都能复用的基础识别函数，避免规则散落各处。
"""
from __future__ import annotations

import re


AREAS = ["新街口", "老门东", "河西", "夫子庙", "鼓楼", "玄武湖", "江宁", "仙林", "百家湖", "奥体", "马鞍山"]
UNLIMITED = {"不限", "都可以", "随便", "无所谓", "没有偏好", "any"}

CN_NUM = {
    "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12,
}


SCRIPT_STYLE_ALIASES = {
    "欢乐本": ["欢乐本", "欢乐盒装", "欢乐盒装本", "搞笑本", "轻松本", "欢乐"],
    "推理本": ["推理本", "硬核本", "硬核", "本格", "还原本", "推理", "烧脑"],
    "机制本": ["机制本", "阵营本", "阵营", "机制"],
    "情感本": ["情感本", "哭本", "情感", "沉浸情感"],
    "恐怖本": ["恐怖本", "惊悚本", "微恐", "恐怖", "惊悚"],
}

CUISINE_ALIASES = {
    "火锅": ["火锅", "涮锅", "川锅", "麻辣锅"],
    "烧烤": ["烧烤", "烤串", "撸串", "烤肉", "烤鱼"],
    "海鲜": ["海鲜", "河鲜", "鱼虾", "虾", "生蚝"],
    "江浙菜": ["江浙菜", "杭帮菜", "本帮菜", "淮扬菜", "炒菜", "家常菜"],
    "本地面食": ["面馆", "吃面", "面条", "粉丝汤", "鸭血粉丝"],
    "简餐": ["简餐", "轻食", "沙拉", "三明治", "咖啡馆"],
    "西餐": ["西餐", "牛排", "意面", "披萨"],
    "融合菜": ["融合菜", "创意菜", "精致一点"],
}

DIET_LIMIT_ALIASES = {
    "no_spicy": ["不吃辣", "不要辣", "不能吃辣", "不辣", "少辣", "清淡点"],
    "no_alcohol": ["不喝酒", "不要酒", "不能喝酒", "不开酒", "不碰酒"],
    "light_food": ["清淡", "低脂", "减肥", "轻食"],
    "no_cilantro": ["不吃香菜", "不要香菜", "香菜过敏"],
}

DISTANCE_ALIASES = {
    "nearby": ["附近", "近一点", "离家近", "别太远", "不要太远", "别离家太远", "不要离家太远", "懒得跑", "不想跑太远"],
    "same_area": ["同商圈", "这一片", "这附近", "就近", "附近逛逛"],
    "flexible": ["远一点也行", "不怕远", "多远都行", "可以跑远点"],
    "food_first": ["为了好吃", "好吃就行", "美食优先", "评分高就行", "值得跑"],
}

ORIGIN_ALIASES = {
    "together": ["一起出发", "都在一起", "我们在一起", "同一个地方出发"],
    "separate": ["各自出发", "分头过去", "不同地方", "不在一起", "分散"],
    "organizer_area": ["离我近", "按我的位置", "我来定"],
}

STAYIN_MODE_ALIASES = {
    "movie_takeaway": ["电影外卖", "看电影点外卖", "在线电影外卖"],
    "movie_snacks": ["追剧零食", "电影零食", "看剧零食"],
    "snacks_only": ["只想吃零食", "囤点零食", "买点零食"],
}


def has_party_size(text: str) -> bool:
    return parse_party_size(text) is not None


def parse_party_size(text: str, default: int | None = None) -> int | None:
    text = text or ""
    m = re.search(r"(?:我和|我跟|我带|加我|和|跟|带)\s*(\d+)\s*(个)?\s*(朋友|同学|同事|人)", text)
    if m:
        return int(m.group(1)) + 1
    m = re.search(r"(?:我和|我跟|我带|加我|和|跟|带)\s*([一二两三四五六七八九十])\s*(个)?\s*(朋友|同学|同事|人)", text)
    if m:
        value = CN_NUM.get(m.group(1), 0)
        return value + 1 if value else default
    m = re.search(r"(\d+)\s*(个朋友|朋友|个人|人|位)", text)
    if m:
        return int(m.group(1))
    m = re.search(r"([一二两三四五六七八九十])\s*(个朋友|朋友|个人|人|位)", text)
    if m:
        return CN_NUM.get(m.group(1), default)
    return default


def has_budget(text: str) -> bool:
    return parse_budget(text) is not None


def parse_budget(text: str, default: int | None = None) -> int | None:
    text = text or ""
    for pattern in (r"人均\s*(\d+)", r"(\d+)\s*(元|块)", r"预算\s*(\d+)"):
        m = re.search(pattern, text)
        if m:
            return int(m.group(1))
    return default


def parse_spoken_time(text: str) -> str | None:
    """只解析明确到“几点/HH:MM”的时间；“下午/晚上”这类粗时间不算明确。"""
    text = text or ""
    m = re.search(r"(\d{1,2})\s*[:：]\s*(\d{2})", text)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"

    time_word = r"(上午|早上|中午|下午|傍晚|晚上|今晚)?"
    hour_word = r"(\d{1,2}|十一|十二|十|九|八|七|六|五|四|三|两|二|一)"
    m = re.search(time_word + r"\s*" + hour_word + r"\s*点\s*(半|[0-5]?\d\s*分?)?", text)
    if not m:
        return None
    period = m.group(1) or ""
    hour_raw = m.group(2)
    minute_raw = (m.group(3) or "").strip()
    hour = int(hour_raw) if hour_raw.isdigit() else CN_NUM.get(hour_raw)
    if hour is None:
        return None
    minute = 30 if "半" in minute_raw else 0
    if minute_raw and "半" not in minute_raw:
        mm = re.search(r"\d+", minute_raw)
        minute = int(mm.group(0)) if mm else 0
    if period in ("下午", "傍晚", "晚上", "今晚") and hour < 12:
        hour += 12
    return f"{hour:02d}:{minute:02d}"


def has_exact_start_time(text: str) -> bool:
    return parse_spoken_time(text) is not None


def parse_coarse_start_time(text: str, default: str = "14:00") -> str:
    text = text or ""
    explicit = parse_spoken_time(text)
    if explicit:
        return explicit
    if re.search(r"上午|早上", text):
        return "10:00"
    if "中午" in text:
        return "12:00"
    if "下午" in text:
        return "14:00"
    if re.search(r"晚上|傍晚|今晚", text):
        return "18:00"
    return default


def has_duration(text: str) -> bool:
    text = text or ""
    return bool(re.search(r"\d+\s*个?小时|\d+\s*h|半天|一下午|一晚上", text, re.I))


def has_area(text: str) -> bool:
    return any(area in (text or "") for area in AREAS)


def first_area(text: str, default: str | None = None) -> str | None:
    for area in AREAS:
        if area in (text or ""):
            return area
    return default


def extract_domain_signals(text: str) -> dict:
    text = text or ""
    diet_limits = _multi_alias(text, DIET_LIMIT_ALIASES)
    distance = _first_alias(text, DISTANCE_ALIASES)
    return {
        "script_style": _first_alias(text, SCRIPT_STYLE_ALIASES),
        "cuisine_preference": _first_alias(text, CUISINE_ALIASES),
        "diet_limits": diet_limits,
        "distance_tolerance": distance,
        "origin_mode": _first_alias(text, ORIGIN_ALIASES),
        "stayin_mode": _first_alias(text, STAYIN_MODE_ALIASES),
    }


def categories_for_cuisine(cuisine: str | None) -> list[str]:
    if not cuisine or cuisine in UNLIMITED:
        return []
    return [cuisine]


def _first_alias(text: str, alias_map: dict[str, list[str]]) -> str | None:
    for value, words in alias_map.items():
        if any(word in text for word in words):
            return value
    return None


def _multi_alias(text: str, alias_map: dict[str, list[str]]) -> list[str]:
    out = []
    for value, words in alias_map.items():
        if any(word in text for word in words):
            out.append(value)
    return out
