import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


SYNCHRONIZE = 0x00100000
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008


def append_log(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def wait_for_process_exit(pid: int, timeout_seconds: int = 60) -> bool:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        return True
    try:
        result = kernel32.WaitForSingleObject(handle, timeout_seconds * 1000)
        return result == WAIT_OBJECT_0
    finally:
        kernel32.CloseHandle(handle)


def launch_target(target: Path, ack_path: Path | None, token: str) -> subprocess.Popen:
    environment = os.environ.copy()
    if ack_path is not None:
        environment["BANKBIN_UPDATE_ACK"] = str(ack_path)
        environment["BANKBIN_UPDATE_TOKEN"] = token
    else:
        environment.pop("BANKBIN_UPDATE_ACK", None)
        environment.pop("BANKBIN_UPDATE_TOKEN", None)
    return subprocess.Popen(
        [str(target)],
        cwd=str(target.parent),
        env=environment,
        close_fds=True,
        creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
    )


def schedule_cleanup(helper_dir: Path) -> None:
    command = f'ping 127.0.0.1 -n 3 >nul & rmdir /s /q "{helper_dir}"'
    subprocess.Popen(
        ["cmd.exe", "/d", "/c", command],
        close_fds=True,
        creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
    )


def run_update(source: Path, target: Path, old_pid: int, log_path: Path, token: str) -> int:
    backup = target.with_name(target.name + ".update-backup")
    ack_path = source.parent / "startup.ack"
    new_process = None
    replaced = False
    try:
        append_log(log_path, f"Updater started for PID {old_pid}.")
        if not wait_for_process_exit(old_pid):
            raise RuntimeError("旧程序未在 60 秒内退出。")
        if not source.is_file():
            raise RuntimeError("下载文件不存在。")
        if not target.is_file():
            raise RuntimeError("旧程序文件不存在。")

        backup.unlink(missing_ok=True)
        os.replace(target, backup)
        os.replace(source, target)
        replaced = True

        ack_path.unlink(missing_ok=True)
        new_process = launch_target(target, ack_path, token)
        deadline = time.monotonic() + 60
        acknowledged = False
        while time.monotonic() < deadline:
            if ack_path.is_file():
                try:
                    acknowledged = ack_path.read_text(encoding="ascii").strip() == token
                except OSError:
                    acknowledged = False
                if acknowledged:
                    break
            if new_process.poll() is not None:
                break
            time.sleep(0.25)
        if not acknowledged:
            raise RuntimeError("新程序未能确认启动。")

        backup.unlink()
        ack_path.unlink(missing_ok=True)
        append_log(log_path, "Update completed; old executable removed and new executable started.")
        return 0
    except Exception as exc:
        append_log(log_path, f"Update failed: {exc}")
        if new_process is not None and new_process.poll() is None:
            new_process.kill()
            time.sleep(0.5)
        if replaced and backup.is_file():
            target.unlink(missing_ok=True)
            os.replace(backup, target)
        if target.is_file():
            launch_target(target, None, "")
            append_log(log_path, "Rollback completed; previous executable restarted.")
        return 1
    finally:
        source.unlink(missing_ok=True)
        ack_path.unlink(missing_ok=True)
        schedule_cleanup(source.parent)


def main() -> int:
    update_ack_path = os.environ.pop("BANKBIN_UPDATE_ACK", "")
    update_ack_token = os.environ.pop("BANKBIN_UPDATE_TOKEN", "")
    if update_ack_path and update_ack_token:
        ack_path = Path(update_ack_path)
        ack_temp_path = ack_path.with_name(ack_path.name + ".tmp")
        ack_temp_path.write_text(update_ack_token, encoding="ascii")
        os.replace(ack_temp_path, ack_path)
        return 0

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--old-pid", required=True, type=int)
    parser.add_argument("--log-path", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    return run_update(
        Path(args.source).resolve(),
        Path(args.target).resolve(),
        args.old_pid,
        Path(args.log_path).resolve(),
        args.token,
    )


if __name__ == "__main__":
    sys.exit(main())
