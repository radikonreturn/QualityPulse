"""
QualityPulse — Desktop Entry Point (main.py)
Launches Streamlit in a background subprocess, polls until ready,
then opens the pywebview window. Gracefully shuts down on window close.
"""

import subprocess
import sys
import os
import time
import threading
import urllib.request
import urllib.error

import webview


# ── Config ────────────────────────────────────────────────────────────────────
PORT    = 8502
URL     = f"http://localhost:{PORT}"
TIMEOUT = 30  # seconds to wait for Streamlit to become ready
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _start_streamlit() -> subprocess.Popen:
    """Spawn Streamlit as a subprocess."""
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(APP_DIR, "streamlit_app.py"),
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ]
    return subprocess.Popen(
        cmd,
        cwd=APP_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )


def _wait_for_server(url: str, timeout: int) -> bool:
    """Poll the Streamlit URL until it responds or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    return False


def main():
    # 1 — Start Streamlit subprocess
    proc = _start_streamlit()
    print(f"[QualityPulse] Streamlit starting on {URL} …", flush=True)

    # 2 — Wait until ready
    if not _wait_for_server(URL, TIMEOUT):
        proc.terminate()
        print("[QualityPulse] ERROR: Streamlit did not start in time. Exiting.", flush=True)
        sys.exit(1)

    print("[QualityPulse] Streamlit ready. Opening window …", flush=True)

    # 3 — Create pywebview window
    window = webview.create_window(
        title="QualityPulse — Quality Management System",
        url=URL,
        width=1280,
        height=820,
        resizable=True,
        min_size=(1024, 700),
        text_select=True,
    )

    def on_closed():
        """Kill Streamlit when the window closes."""
        print("[QualityPulse] Window closed. Shutting down …", flush=True)
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        sys.exit(0)

    window.events.closed += on_closed

    # 4 — Start pywebview (blocking call)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
