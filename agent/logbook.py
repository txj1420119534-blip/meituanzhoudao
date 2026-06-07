"""
执行日志：把 agent 的每一步可视化展示给评委 / 用户。
"""
import sys
import io
import time
from datetime import datetime

# Windows 终端 UTF-8 兼容（避免 emoji / 中文乱码）
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


class LogBook:
    """执行日志收集器。每个 tool / planner 函数都往里写。"""

    STATUS_ICONS = {
        "pending": "○",
        "running": "…",
        "success": "✓",
        "warning": "!",
        "error":   "✗",
    }

    def __init__(self):
        self.entries: list[dict] = []

    def add(self, step: str, status: str, message: str) -> None:
        """添加一条日志。status: pending/running/success/warning/error"""
        entry = {
            "step": step,
            "status": status,
            "message": message,
            "time": datetime.now().strftime("%H:%M:%S"),
            "ts": time.time(),
        }
        self.entries.append(entry)

    def print_all(self) -> None:
        """命令行下按时间顺序打印所有日志。"""
        for e in self.entries:
            icon = self.STATUS_ICONS.get(e["status"], "?")
            print(f"  [{e['time']}] {icon} {e['step']}：{e['message']}")

    def to_list(self) -> list[dict]:
        """返回纯数据列表，方便给网页 / API 用。"""
        return list(self.entries)

    def clear(self) -> None:
        self.entries.clear()


if __name__ == "__main__":
    log = LogBook()
    log.add("理解需求", "running", "正在解析这句话里的人群、预算、时间和偏好…")
    time.sleep(0.3)
    log.add("理解需求", "success", "识别为「朋友局」，4 人，预算 ¥150/人")
    log.add("检索活动", "running", "正在按场景和偏好筛选周边活动…")
    log.add("检索活动", "success", "找到 8 个候选活动")
    log.add("查询余位", "warning", "原餐厅需排队 55 分钟，正在寻找备选…")
    log.add("重排完成", "success", "已替换餐厅，预算不变")
    log.print_all()
    print(f"\n共 {len(log.to_list())} 条日志")
