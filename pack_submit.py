"""Create the current submission zip with POSIX archive paths."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "weekend-agent-phase2c-itinerary-flow.zip"
PACK_STATUS = ROOT / ".pack_submit_status.json"

INCLUDE = [
    "agent",
    "data",
    "web",
    "cli.py",
    "server.py",
    "config.py",
    "requirements.txt",
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "PROJECT_STATUS.md",
    "TASK.md",
    "TASK_PHASE2B_BOOKING_SLICE3.md",
    "TASK_PHASE2B_CHECKOUT_SLICE4_PLUS.md",
    "TASK_PHASE2B_SUPPORT_SLICE5.md",
    "TASK_PHASE2B_ADDON_SLICE6.md",
    "TASK_PHASE2B_FINAL_INTEGRATION_SLICE7.md",
    "TASK_PHASE2C_WORKFLOW_FIRST_REBUILD.md",
    "TASK_PHASE2C_POLISH_CATALOG_EXPANSION.md",
    "TASK_PHASE2C_BROWSER_DEPLOY_POLISH.md",
    "TASK_PHASE2C_USER_FLOW_PATCH.md",
    "TASK_PHASE2C_NATURAL_INTENT_FIX.md",
    "acceptance_check.py",
    "pack_submit.py",
    "render.yaml",
    "DEMO_PLAYBOOK.md",
    "DEPLOY_RENDER_GUIDE.md",
    "FRIEND_TEST_CHECKLIST.md",
    "ACCEPTANCE_REPORT.md",
    "BROWSER_QA_REPORT.md",
    "CODE_QUALITY_REPORT.md",
    "CHANGE_SUMMARY.md",
    "HARDENING2_REPORT.md",
    "SUBMISSION_CLEANUP_REPORT.md",
    "CORE_WORKFLOW_REBUILD_REPORT.md",
    "WORKFLOW_REBUILD_REPORT.md",
    "PHASE2C_POLISH_REPORT.md",
    "CATALOG_EXPANSION_REPORT.md",
    "PHASE2C_USER_FLOW_PATCH_REPORT.md",
    "PHASE2C_ITINERARY_FLOW_REPORT.md",
    "NATURAL_INTENT_COORDINATION_REPORT.md",
    "PHASE2A_ITINERARY_REPORT.md",
    "PHASE2A_CLEANUP_REPORT.md",
    "PHASE2B_RESCUE_REPORT.md",
    "PHASE2B_VOTE_REPORT.md",
    "PHASE2B_BOOKING_REPORT.md",
    "PHASE2B_CHECKOUT_REPORT.md",
    "PHASE2B_SUPPORT_REPORT.md",
    "PHASE2B_ADDON_REPORT.md",
    "PHASE2B_FINAL_INTEGRATION_REPORT.md",
    "DOC_ENCODING_FIX_REPORT.md",
    "ACCEPTANCE_RUNNER_FIX_REPORT.md",
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".playwright-cli",
    "output",
    ".acceptance_tmp",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".log",
    ".zip",
}

SKIP_NAMES = {
    ".env",
}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in rel.parts):
        return True
    if path.name in SKIP_NAMES:
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    if path.name.endswith(".env"):
        return True
    return False


def iter_files():
    for item in INCLUDE:
        path = ROOT / item
        if not path.exists():
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and not should_skip(child):
                    yield child
        elif path.is_file() and not should_skip(path):
            yield path


def update_report(posix_paths: bool, file_count: int) -> None:
    line = f"- Zip internal paths use POSIX `/`: {'YES' if posix_paths else 'NO'}"
    for name in (
        "ACCEPTANCE_REPORT.md",
        "PHASE2A_CLEANUP_REPORT.md",
        "PHASE2B_RESCUE_REPORT.md",
        "PHASE2B_VOTE_REPORT.md",
        "PHASE2B_BOOKING_REPORT.md",
        "PHASE2B_CHECKOUT_REPORT.md",
        "PHASE2B_SUPPORT_REPORT.md",
        "PHASE2B_ADDON_REPORT.md",
        "PHASE2B_FINAL_INTEGRATION_REPORT.md",
        "WORKFLOW_REBUILD_REPORT.md",
        "PHASE2C_POLISH_REPORT.md",
        "CATALOG_EXPANSION_REPORT.md",
        "BROWSER_QA_REPORT.md",
        "PHASE2C_USER_FLOW_PATCH_REPORT.md",
        "NATURAL_INTENT_COORDINATION_REPORT.md",
        "DEPLOY_RENDER_GUIDE.md",
        "FRIEND_TEST_CHECKLIST.md",
        "DOC_ENCODING_FIX_REPORT.md",
        "ACCEPTANCE_RUNNER_FIX_REPORT.md",
        "CHANGE_SUMMARY.md",
    ):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("- Final zip POSIX paths: UNKNOWN", f"- Final zip POSIX paths: {'YES' if posix_paths else 'NO'}")
        text = text.replace("- zip 内路径是否为 POSIX `/`：UNKNOWN", line)
        text = text.replace("- zip 内路径是否为 POSIX `/`：YES", line)
        text = text.replace("- zip 鍐呰矾寰勬槸鍚︿负 POSIX `/`锛歎NKNOWN", line)
        text = text.replace("- zip 鍐呰矾寰勬槸鍚︿负 POSIX `/`锛歒ES", line)
        text = text.replace("- packaging: UNKNOWN/FAIL", f"- packaging: {'PASS' if posix_paths else 'FAIL'}")
        text = text.replace("- Packaging: UNKNOWN/FAIL", f"- Packaging: {'PASS' if posix_paths else 'FAIL'}")
        text = text.replace("- packaging：UNKNOWN/FAIL", f"- packaging：{'PASS' if posix_paths else 'FAIL'}")
        text = text.replace("- packaging锛歎NKNOWN/FAIL", f"- packaging: {'PASS' if posix_paths else 'FAIL'}")
        if "## Packaging Status" in text:
            text = text.split("## Packaging Status", 1)[0].rstrip() + "\n"
        text += "\n## Packaging Status\n\n"
        text += f"{line}\n"
        text += f"- zip file: `{OUTPUT.name}`\n"
        text += f"- packaged files: {file_count}\n"
        path.write_text(text, encoding="utf-8")


def main() -> int:
    if OUTPUT.exists():
        OUTPUT.unlink()
    files = list(iter_files())
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(ROOT).as_posix()
            zf.write(path, arcname)

    with zipfile.ZipFile(OUTPUT, "r") as zf:
        names = zf.namelist()
    posix_paths = all("\\" not in name for name in names)
    status = {
        "zip": OUTPUT.name,
        "posix_paths": posix_paths,
        "file_count": len(names),
        "bad_paths": [name for name in names if "\\" in name],
    }
    PACK_STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    update_report(posix_paths, len(names))
    print(json.dumps(status, ensure_ascii=False), flush=True)
    return 0 if posix_paths else 1


if __name__ == "__main__":
    raise SystemExit(main())
