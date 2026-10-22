"""
Game Launcher for RehabQuest
----------------------------
Orchestrates launching the Python MediaPipe tracking server in a visible console
so the user and Unity can verify the socket connection in real-time.
"""

import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
SERVER_SCRIPT = PROJECT_ROOT / "communication" / "mediapipe_unity_server.py"
PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

from local_data import import_unity_session


class GameLauncher(QObject):
    game_started = pyqtSignal(str)
    game_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popen = None
        self._active_game_id = None
        self._user_id = "PATIENT_01"

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(500)
        self._poll_timer.timeout.connect(self._check_process_status)

    def launch(self, game_id: str, user_id: str):
        if self._popen and self._popen.poll() is None:
            print("[game_launcher] Process already active")
            return

        self._active_game_id = game_id
        self._user_id = user_id

        # Launch in a visible, new console window so output is clear
        flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        try:
            self._popen = subprocess.Popen(
                [str(PYTHON_EXE), str(SERVER_SCRIPT)],
                cwd=str(PROJECT_ROOT),
                creationflags=flags
            )
            self._poll_timer.start()
            self.game_started.emit(game_id)
            print(f"[game_launcher] Started MediaPipe tracking server for {game_id} (PID {self._popen.pid})")
        except Exception as exc:
            print(f"[game_launcher] Failed to start tracking server: {exc}")

    def stop(self):
        if self._popen and self._popen.poll() is None:
            self._popen.terminate()
            try:
                self._popen.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                self._popen.kill()
        self._poll_timer.stop()

    def _check_process_status(self):
        if self._popen and self._popen.poll() is not None:
            exit_code = self._popen.poll()
            self._poll_timer.stop()
            self._on_finished(exit_code)

    def _on_finished(self, exit_code):
        print(f"[game_launcher] Session process finished with code {exit_code}")
        game_id = self._active_game_id or "reach_and_collect"
        self._active_game_id = None
        self._popen = None

        # Check for newly generated session files to analyze
        self._check_and_import_latest_session()

        self.game_finished.emit(game_id)

    def _check_and_import_latest_session(self):
        userprofile = Path(os.environ.get("USERPROFILE", ""))
        search_dirs = [
            userprofile / "AppData" / "LocalLow" / "DefaultCompany" / "RehabQuest-Unity" / "RehabQuestSessions",
            PROJECT_ROOT / "RehabQuestSessions",
            userprofile / "AppData" / "LocalLow"
        ]

        found_files = []
        for d in search_dirs:
            if d.exists():
                for p in d.rglob("reach_and_collect_session_*.json"):
                    found_files.append(p)

        if found_files:
            latest_file = max(found_files, key=lambda f: f.stat().st_mtime)
            print(f"[game_launcher] Found latest Unity session: {latest_file}")
            import_unity_session(str(latest_file), self._user_id)
