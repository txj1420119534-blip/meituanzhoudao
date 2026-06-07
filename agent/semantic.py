"""
semantic.py —— 把口语化表达归一成稳定的意图标签。

LLM 负责理解自然语言；这里负责兜住高频业务语义，避免现场演示被黑话、
情绪化表达或同义词带偏。
"""
from __future__ import annotations

INTENT_LEXICON = {
    "stay_home": [
        "宅家", "在家", "不想出门", "不想出去", "不出门", "待着", "呆着",
        "窝着", "躺着", "躺平", "摆烂", "不想动", "懒得动", "懒得走",
        "懒得折腾", "不想折腾", "低能量",
    ],
    "low_energy": [
        "好困", "困", "累", "好累", "疲惫", "没精神", "不想动",
        "懒", "躺", "休息", "轻松点", "不要太累", "不想太累",
    ],
    "casual_play": [
        "又菜又爱玩", "菜又爱玩", "菜但爱玩", "想玩", "玩点",
        "找点乐子", "消磨时间", "打发时间", "随便玩玩", "轻松玩",
    ],
    "script_game": ["剧本杀", "打本", "约本", "推本", "本子", "剧本", "沉浸本", "凶案本", "恐怖本", "欢乐本", "盒装本"],
    "script_fun": ["欢乐本", "欢乐盒装", "欢乐盒装本", "搞笑本", "轻松本"],
    "script_reasoning": ["推理本", "硬核本", "硬核", "本格", "还原本"],
    "script_mechanism": ["机制本", "阵营本", "机制", "阵营"],
    "script_emotion": ["情感本", "哭本", "情感"],
    "script_horror": ["恐怖本", "惊悚本", "微恐"],
    "escape_room": ["密室", "逃脱", "解谜"],
    "board_game": ["桌游", "狼人杀", "棋牌", "麻将", "卡牌"],
    "ktv": ["KTV", "ktv", "唱歌", "唱K", "唱k", "欢唱", "包厢"],
    "movie": ["看电影", "电影", "电影院", "影院", "观影"],
    "exhibition": ["看展", "展览", "美术馆", "博物馆", "文艺"],
    "citywalk": ["citywalk", "Citywalk", "城市漫步", "压马路", "逛街", "散步", "随便走走", "拍街景"],
    "handmade": ["手作", "陶艺", "做手工", "diy", "DIY"],
    "market": ["市集", "集市", "逛摊"],
    "sport": ["运动", "滑冰", "骑行", "高尔夫", "保龄球"],
    "billiards": ["台球", "桌球", "黑八", "斯诺克"],
    "massage": ["按摩", "足疗", "spa", "SPA", "推拿", "捏肩", "放松一下"],
    "hotel": ["酒店", "订个酒店", "休息房", "钟点房", "开个房", "休息一下"],
    "birthday": ["生日", "庆生", "过生日", "蛋糕"],
    "party": ["聚会", "团建", "朋友聚", "组局", "局"],
    "date": ["情侣", "对象", "约会", "男朋友", "女朋友", "暧昧", "二人世界"],
    "family": ["孩子", "娃", "宝宝", "亲子", "老婆孩子", "儿子", "女儿"],
    "dinner": ["吃饭", "吃点", "美食", "餐厅", "晚饭", "午饭", "正餐", "聚餐"],
    "cuisine_hotpot": ["火锅", "涮锅", "麻辣锅"],
    "cuisine_bbq": ["烧烤", "烤串", "撸串", "烤肉", "烤鱼"],
    "cuisine_seafood": ["海鲜", "河鲜", "鱼虾", "虾", "生蚝"],
    "cuisine_jiangzhe": ["江浙菜", "杭帮菜", "淮扬菜", "炒菜", "家常菜"],
    "takeaway": ["点外卖", "外卖", "夜宵"],
    "snacks": ["零食", "闪购", "便利店", "小象超市", "囤点"],
    "milk_tea": ["奶茶", "茶饮", "喝奶茶", "喝点", "饮料"],
    "coffee": ["咖啡", "美式", "拿铁", "喝咖啡"],
    "photo": ["拍照", "出片", "打卡", "网红"],
    "avoid_queue": ["别排队", "不排队", "不要排队", "少排队", "排队少"],
    "nearby": ["别太远", "不要太远", "离家近", "近一点", "附近"],
    "light_food": ["清淡", "减肥", "低脂", "轻食", "不辣"],
    "no_spicy": ["不吃辣", "不要辣", "不能吃辣", "不辣"],
    "no_alcohol": ["不喝酒", "不要酒", "不能喝酒", "别有酒", "无酒精", "不含酒", "不要喝酒"],
    "caffeine_free": ["不要咖啡因", "不含咖啡因", "不能有咖啡因", "无咖啡因", "低咖啡因"],
    "no_meal": ["不想吃饭", "不吃饭", "不要吃饭", "不安排吃饭", "不要餐厅"],
    "no_ice": ["不能喝冰", "不能冰", "不要冰", "去冰", "不加冰", "热的", "热饮"],
    "not_too_sweet": ["不要太甜", "别太甜", "不太甜", "少糖", "低糖", "半糖", "三分糖", "无糖"],
    "body_uncomfortable": ["生理期", "姨妈", "来例假", "肚子不舒服", "胃不舒服", "身体不舒服", "感冒"],
    "self_drive": ["自驾", "开车", "自己开车"],
    "newbie": ["第一次玩", "新手", "有人第一次", "没玩过", "小白"],
    "alcohol_request": ["喝酒", "小酒", "精酿", "啤酒", "酒吧", "喝点酒"],
}


INTENT_CATEGORY_MAP = {
    "script_game": {"role": "PLAY", "category": "剧本杀"},
    "escape_room": {"role": "PLAY", "category": "密室"},
    "board_game": {"role": "PLAY", "category": "桌游"},
    "ktv": {"role": "PLAY", "category": "KTV"},
    "billiards": {"role": "PLAY", "category": "台球"},
    "massage": {"role": "PLAY", "category": "按摩"},
    "citywalk": {"role": "PLAY", "category": "景区"},
    "hotel": {"role": "PLAY", "category": "酒店"},
    "movie": {"role": "PLAY", "category": "电影院"},
    "exhibition": {"role": "PLAY", "category": "展览"},
    "handmade": {"role": "PLAY", "category": "手作"},
    "market": {"role": "PLAY", "category": "市集"},
    "takeaway": {"role": "STAYIN", "category": "外卖"},
    "snacks": {"role": "STAYIN", "category": "闪购零食"},
    "milk_tea": {"role": "ADDON", "category": "奶茶"},
    "coffee": {"role": "ADDON", "category": "咖啡"},
    "cuisine_hotpot": {"role": "EAT", "category": "火锅"},
    "cuisine_bbq": {"role": "EAT", "category": "烧烤"},
    "cuisine_seafood": {"role": "EAT", "category": "海鲜"},
    "cuisine_jiangzhe": {"role": "EAT", "category": "江浙菜"},
}


def analyze_semantics(text: str) -> dict:
    """
    返回稳定语义信号：
      - scene: 强场景提示，可为空
      - intent_tags: 标准意图标签
      - explicit_categories: 可直接锁槽的品类
      - preferences / hard_limits: 给排序和追问使用
    """
    text = text or ""
    tags = _collect_intents(text)
    tag_set = set(tags)

    scene = None
    if "stay_home" in tag_set or ("low_energy" in tag_set and "casual_play" in tag_set):
        scene = "stay_in"
    elif "family" in tag_set:
        scene = "family_out"
    elif "date" in tag_set:
        scene = "couple"
    elif "dinner" in tag_set and not (tag_set & {
        "script_game", "escape_room", "board_game", "ktv", "movie", "exhibition",
        "citywalk", "handmade", "market", "sport", "massage", "billiards", "hotel"
    }):
        scene = "food_only"
    elif tag_set & {
        "script_game", "escape_room", "board_game", "ktv", "movie", "exhibition",
        "citywalk", "handmade", "market", "sport", "massage", "billiards", "hotel", "birthday", "party",
        "dinner",
    }:
        scene = "friends_out"

    preferences = []
    if tag_set & {"photo", "citywalk", "exhibition"}:
        preferences.append("photo")
    if tag_set & {"dinner", "takeaway", "birthday", "party"}:
        preferences.append("good_food")
    if tag_set & {"low_energy", "stay_home", "casual_play"}:
        preferences.extend(["easy_pace", "relax"])
    if tag_set & {"exhibition", "citywalk", "handmade"}:
        preferences.append("culture")
    if "family" in tag_set:
        preferences.extend(["kid_friendly", "easy_pace"])
    if "light_food" in tag_set:
        preferences.append("light_food")
    if "newbie" in tag_set:
        preferences.append("newbie_friendly")

    hard_limits = []
    if "avoid_queue" in tag_set:
        hard_limits.append("no_evening_queue")
    if "nearby" in tag_set or "low_energy" in tag_set:
        hard_limits.append("stay_near")
    if "family" in tag_set:
        hard_limits.append("kid_safe")
    if "self_drive" in tag_set:
        hard_limits.append("drive_safe")

    explicit_categories = []
    for tag in tags:
        mapped = INTENT_CATEGORY_MAP.get(tag)
        if not mapped:
            continue
        role = mapped["role"]
        category = mapped["category"]
        if tag == "movie" and scene == "stay_in":
            role, category = "STAYIN", "在线电影"
        explicit_categories.append({
            "role": role,
            "category": category,
            "keyword": _first_hit(text, INTENT_LEXICON[tag]) or tag,
        })

    return {
        "scene": scene,
        "intent_tags": tags,
        "explicit_categories": _dedupe_categories(explicit_categories),
        "preferences": _dedupe(preferences),
        "hard_limits": _dedupe(hard_limits),
        "home_area": "线上" if scene == "stay_in" else None,
        "transport": "self_drive" if "self_drive" in tag_set else None,
    }


def has_intent(text: str, intent: str) -> bool:
    return intent in _collect_intents(text or "")


def _collect_intents(text: str) -> list[str]:
    hits = []
    for intent, words in INTENT_LEXICON.items():
        if _first_hit(text, words):
            hits.append(intent)
    return hits


def _first_hit(text: str, words: list[str]) -> str | None:
    for word in words:
        if word in text:
            return word
    return None


def _dedupe(values: list[str]) -> list[str]:
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
