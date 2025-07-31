
import subprocess


def shell_cli_output(cmd: str, redirect_stderr=False) -> str:
    stderr = subprocess.STDOUT if redirect_stderr else None
    return subprocess.check_output(cmd, stderr=stderr, shell=True, encoding='utf-8', text=True).strip()
