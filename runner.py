"""通用桌面应用签到自动化 runner。

用法：
  python runner.py --app <App.exe路径> --signin <signin.py路径> [--wait N秒]

环境变量覆盖（与命令行冲突时命令行优先）：
  APP_EXE        - 应用可执行文件路径
  SIGNIN_SCRIPT  - 签到脚本路径
  WAIT_SECONDS   - 启动后等待秒数（默认30）
  LOG_FILE       - 日志文件路径（默认 <脚本目录>/signin.log）
  SIGNIN_LOG     - 签到脚本静默日志（传给 SIGNIN_SCRIPT 的 WORKBUDDY_SIGNIN_LOG）

依赖：Python 3.6+，零外部包。
"""
import argparse
import json
import os
import subprocess
import sys
import time


def detect_platform():
    """简单平台检测"""
    return "win" if sys.platform.startswith("win") else "posix"


def is_process_running(name: str) -> bool:
    """检测进程是否在运行。Windows 用 tasklist，其他用 pgrep。"""
    try:
        if detect_platform() == "win":
            result = subprocess.run(
                ["tasklist", "/fi", f"imagename eq {name}", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=10
            )
            return name in result.stdout
        else:
            result = subprocess.run(["pgrep", "-f", name], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
    except Exception:
        return False


def ensure_running(exe_path: str, wait: int = 30) -> bool:
    """确保应用正在运行，未运行则启动并等待。"""
    name = os.path.basename(exe_path)
    if is_process_running(name):
        return True
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"应用可执行文件不存在: {exe_path}")
    subprocess.Popen(exe_path, shell=False)
    print(json.dumps({"step": "launched", "exe": exe_path}))
    time.sleep(wait)
    if not is_process_running(name):
        raise RuntimeError(f"应用启动后未在 {wait}s 内运行: {exe_path}")
    return True


def run_signin(signin_script: str, log_file: str) -> int:
    """调用签到脚本，返回退出码。"""
    env = os.environ.copy()
    env["WORKBUDDY_SIGNIN_LOG"] = log_file
    result = subprocess.run(
        [sys.executable, signin_script, "silent"],
        capture_output=True, text=True, timeout=120,
        env=env
    )
    if result.returncode != 0:
        print(json.dumps({
            "step": "error",
            "detail": result.stderr[:300] if result.stderr else result.stdout[:300]
        }))
        return 1
    # 读取并打印最新日志行
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                if last_line:
                    print(last_line)
    except Exception:
        pass
    return 0


def main():
    parser = argparse.ArgumentParser(description="通用桌面应用签到自动化 runner")
    parser.add_argument("--app", required=True, help="应用可执行文件路径（如 D:/Programs/App/App.exe）")
    parser.add_argument("--signin", required=True, help="签到脚本路径（如 .../examples/workbuddy/signin.py）")
    parser.add_argument("--wait", type=int, default=30, help="启动后等待秒数（默认30）")
    parser.add_argument("--log", default=None, help="日志文件路径（默认与 signin 同目录）")
    args = parser.parse_args()

    exe_path = args.app or os.environ.get("APP_EXE")
    signin_path = args.signin or os.environ.get("SIGNIN_SCRIPT")
    wait = args.wait or int(os.environ.get("WAIT_SECONDS", "30"))
    log_file = args.log or os.environ.get("LOG_FILE")

    if not signin_path:
        print(json.dumps({"error": "SIGNIN_SCRIPT not found"}))
        return 1

    if log_file is None:
        log_file = os.path.join(os.path.dirname(os.path.abspath(signin_path)), "signin.log")

    try:
        ensure_running(exe_path, wait)
    except (FileNotFoundError, RuntimeError) as e:
        print(json.dumps({"step": "error", "detail": str(e)}))
        return 1

    return run_signin(signin_path, log_file)


if __name__ == "__main__":
    sys.exit(main())
