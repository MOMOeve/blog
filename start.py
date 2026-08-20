#!/usr/bin/env python3
"""星野文记：一键启动前后端开发服务。

用法（在项目根目录 blog/ 下）：
    python start.py

停止：在终端按 Ctrl+C
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173


def die(msg: str) -> None:
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(1)


def find_backend_python() -> Path:
    if sys.platform == "win32":
        candidates = [
            BACKEND / ".venv" / "Scripts" / "python.exe",
            ROOT / ".venv" / "Scripts" / "python.exe",
        ]
    else:
        candidates = [
            BACKEND / ".venv" / "bin" / "python",
            ROOT / ".venv" / "bin" / "python",
        ]
    for path in candidates:
        if path.is_file():
            return path
    die(
        "未找到后端虚拟环境。请先执行：\n"
        "  cd backend\n"
        "  python -m venv .venv\n"
        "  .\\.venv\\Scripts\\activate   # Windows\n"
        "  pip install -r requirements.txt"
    )


def ensure_env_files() -> None:
    pairs = [
        (BACKEND / ".env.example", BACKEND / ".env"),
        (FRONTEND / ".env.example", FRONTEND / ".env"),
    ]
    for example, target in pairs:
        if not target.exists() and example.exists():
            target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"[提示] 已从 {example.name} 生成 {target.relative_to(ROOT)}")


def check_frontend() -> None:
    if not (FRONTEND / "package.json").is_file():
        die(f"找不到前端目录：{FRONTEND}")
    if not (FRONTEND / "node_modules").is_dir():
        die(
            "前端依赖未安装。请先执行：\n"
            "  cd frontend\n"
            "  npm install"
        )


def start_process(name: str, args: list[str], cwd: Path) -> subprocess.Popen:
    print(f"[启动] {name}: {' '.join(args)}")
    creationflags = 0
    if sys.platform == "win32":
        # 新进程组，便于 Ctrl+C 时一起结束子进程
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    return subprocess.Popen(
        args,
        cwd=str(cwd),
        env=os.environ.copy(),
        creationflags=creationflags,
    )


def stop_process(proc: subprocess.Popen | None, name: str) -> None:
    if proc is None or proc.poll() is not None:
        return
    print(f"[停止] {name} (pid={proc.pid})")
    try:
        if sys.platform == "win32":
            proc.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            try:
                proc.wait(timeout=3)
                return
            except subprocess.TimeoutExpired:
                pass
            proc.terminate()
        else:
            proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    except Exception as exc:  # noqa: BLE001
        print(f"[警告] 停止 {name} 时出错：{exc}", file=sys.stderr)


def main() -> None:
    if not BACKEND.is_dir() or not FRONTEND.is_dir():
        die("请在项目根目录（含 frontend/ 与 backend/）运行本脚本。")

    ensure_env_files()
    py = find_backend_python()
    check_frontend()

    npm = "npm.cmd" if sys.platform == "win32" else "npm"

    backend = start_process(
        "Django",
        [str(py), "manage.py", "runserver", str(BACKEND_PORT)],
        BACKEND,
    )
    time.sleep(0.8)
    frontend = start_process(
        "Vite",
        [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)],
        FRONTEND,
    )

    print()
    print("=" * 48)
    print("  星野文记已启动")
    print(f"  前端  http://127.0.0.1:{FRONTEND_PORT}/")
    print(f"  后端  http://127.0.0.1:{BACKEND_PORT}/api/docs/")
    print(f"  演示  demo@example.com / demo1234")
    print("  按 Ctrl+C 同时停止前后端")
    print("=" * 48)
    print()

    try:
        while True:
            if backend.poll() is not None:
                print(f"[错误] Django 已退出，code={backend.returncode}", file=sys.stderr)
                break
            if frontend.poll() is not None:
                print(f"[错误] Vite 已退出，code={frontend.returncode}", file=sys.stderr)
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[提示] 收到中断，正在关闭…")
    finally:
        stop_process(frontend, "Vite")
        stop_process(backend, "Django")
        print("[完成] 已全部停止。")


if __name__ == "__main__":
    main()
