"""Compare redirected probe output with the synthetic paths supplied by Python."""

import ctypes
import os
import platform
import subprocess
import sys
from pathlib import Path


def check_path(probe, folder):
    windows = "C:\\Exports\\" + folder
    posix = "/mnt/c/Exports/" + folder
    results = []
    for option, source, expected in (
        ("--to-posix", windows, posix),
        ("--to-windows", posix, windows),
    ):
        run = subprocess.run([probe, option, source], capture_output=True)
        expected_line = (source + " -> " + expected).encode("utf-8")
        lines = [line for line in run.stdout.splitlines() if b" -> " in line]
        matches = run.returncode == 0 and lines == [expected_line]
        print(option, ascii(folder), "exit", run.returncode, "utf8_match", matches)
        print("  captured", lines, "stderr", run.stderr)
        results.append(matches)
    return all(results)


if __name__ == "__main__":
    probe = Path(sys.argv[1]).resolve(strict=True)
    print(platform.platform(), platform.machine())
    if os.name == "nt":
        print("Windows ANSI code page", ctypes.windll.kernel32.GetACP())
    assert check_path(probe, "music"), "ASCII control failed"
    emoji_matches = check_path(probe, "music-\U0001f600")
    check_path(probe, "\u4e57")
    if os.name != "nt":
        assert emoji_matches, "POSIX control failed"
