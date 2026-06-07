"""
cli.py —— 命令行 Demo。一句话进，全流程跑通；交互式确认 / 模拟异常。
直接运行：python cli.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import Agent
from agent.logbook import LogBook


BANNER = """
═══════════════════════════════════════════════════════════════
        美团周到 · 本地生活执行助手 (CLI Demo)
        美团 2026 黑客松 · 命题六
═══════════════════════════════════════════════════════════════
"""

EXAMPLES = [
    "今天下午和朋友4个人出去玩，想拍照吃饭不要太累，人均150，晚上别排队",
    "今天下午想带5岁的孩子和老婆出去玩几个小时，老婆在减肥要清淡点，别离家太远",
    "周末不想出门，想在家看个电影点个外卖，轻松一点",
    "和对象周末下午想约会，文艺一点的，人均120",
]


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def _print_plan(p: dict, idx: int):
    print(f"\n┌─ 方案 {chr(65 + idx)} · {p['title']} (评分 {p['score']['total']}/100)")
    print(f"│  聚焦：{p['focus']}")
    for s in p["steps"]:
        if s["kind"] == "travel":
            mode = "🚶 步行" if s["mode"] == "walk" else "🚕 打车"
            print(f"│      {mode}约 {s['minutes']} 分钟  ({s['from']} → {s['to']})")
        else:
            tag = " [推广]" if s.get("is_promoted") else ""
            print(f"│  {s['start']}–{s['end']}  {s.get('image', '')} {s['name']}（{s['category']}·{s['area']}）¥{s['cost']}{tag}")
    print(f"│  人均 ¥{p['total_cost_per_person']} · 全程 {p['total_minutes']//60}h{p['total_minutes']%60}min")
    print(f"│  推荐理由：{p['reason']}")
    if p.get("risks"):
        for r in p["risks"]:
            print(f"│  ⚠ {r}")
    print("└─")


def main():
    print(BANNER)
    print("示例（输入数字直接用）：")
    for i, ex in enumerate(EXAMPLES, 1):
        print(f"  {i}. {ex}")
    print("  你也可以直接输入自己的一句话。\n")

    user_input = _ask("> ")
    if user_input.isdigit():
        n = int(user_input)
        if 1 <= n <= len(EXAMPLES):
            user_input = EXAMPLES[n - 1]
    if not user_input:
        user_input = EXAMPLES[0]
        print(f"使用示例：{user_input}")

    agent = Agent()
    print("\n─── 阶段 1：理解 + 规划 ─────────────────────────")
    session = agent.run(user_input)
    print()
    agent.logbook.print_all()

    plans = session.get("plans", [])
    if not plans:
        print("\n✗ 未生成任何方案。")
        return

    print(f"\n生成了 {len(plans)} 个方案：")
    for i, p in enumerate(plans):
        _print_plan(p, i)

    # 选方案
    pick = _ask(f"\n选择哪个方案 [1-{len(plans)}]，回车默认 1：") or "1"
    try:
        idx = max(0, min(len(plans) - 1, int(pick) - 1))
    except ValueError:
        idx = 0
    agent.choose(idx)

    print("\n─── 阶段 2：确认 + 执行 ─────────────────────────")
    session = agent.confirm_and_execute()
    print()
    agent.logbook.print_all()

    # 增值推荐
    if session.get("addon"):
        a = session["addon"]
        print(f"\n💡 顺路加一份：{a['image']} {a['name']}（{a['category']}·{a['area']}）¥{a['price']} · 评分 {a['rating']}")

    print("\n─── 分享卡（可复制到群里）─────────────────────")
    print(session.get("share_card", "(空)"))

    # 异常演示
    print("\n─── 阶段 3：异常局部重排（演示）────────────────")
    print("  1. restaurant_full  餐厅突然满座")
    print("  2. ticket_soldout   活动门票售罄")
    print("  3. time_conflict    朋友说时间太赶")
    print("  0. 跳过")
    exc = _ask("选一个触发 [0-3]：") or "0"
    type_map = {"1": "restaurant_full", "2": "ticket_soldout", "3": "time_conflict"}
    if exc in type_map:
        session = agent.inject_exception(type_map[exc])
        print()
        agent.logbook.print_all()
        result = session.get("exception_result", {})
        print(f"\n调整原因：{result.get('reason', '')}")
        print("\n更新后的方案：")
        _print_plan(session["chosen"], 0)
        print(f"\n更新后的分享卡：\n{session.get('share_card', '')}")

    print("\n═══════════════════════════════════════════════")
    print("    全流程演示结束 · 感谢观看")
    print("═══════════════════════════════════════════════")


if __name__ == "__main__":
    main()
