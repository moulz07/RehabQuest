
"""
Game Launcher for RehabQuest
----------------------------
Launches the MediaPipe tracking server and standalone Unity game,
monitors both processes, and imports the session when the game ends.
"""

import os
import sys
import subprocess
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from local_data import import_unity_session


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

SERVER_SCRIPT = (
    PROJECT_ROOT / "communication" / "mediapipe_unity_server.py"
)

PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

# Build your Unity game into this location.
UNITY_EXE = (
    PROJECT_ROOT / "unity_build" / "RehabQuest-Unity.exe"
)


class GameLauncher(QObject):
    game_started = pyqtSignal(str)
    game_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._server_process = None
        self._unity_process = None

        self._active_game_id = None
        self._user_id = "PATIENT_01"
        self._finishing = False

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(500)
        self._poll_timer.timeout.connect(
            self._check_process_status
        )

    def launch(self, game_id: str, user_id: str):
        # Prevent launching another session while one is running.
        if self._session_is_running():
            print("[game_launcher] A session is already active.")
            return

        # Validate the required files before launching anything.
        if not SERVER_SCRIPT.is_file():
            print(
                "[game_launcher] Tracking server not found: "
                f"{SERVER_SCRIPT}"
            )
            return

        if not UNITY_EXE.is_file():
            print(
                "[game_launcher] Unity executable not found: "
                f"{UNITY_EXE}"
            )
            print(
                "[game_launcher] Build the Unity game and place "
                "ReachAndCollect.exe at the configured path."
            )
            return

        self._active_game_id = game_id
        self._user_id = user_id
        self._finishing = False

        try:
            # 1. Start the MediaPipe tracking server.
            flags = (
                subprocess.CREATE_NEW_CONSOLE
                if os.name == "nt"
                else 0
            )

            self._server_process = subprocess.Popen(
                [str(PYTHON_EXE), str(SERVER_SCRIPT)],
                cwd=str(PROJECT_ROOT),
                creationflags=flags,
            )

            print(
                "[game_launcher] Tracking server started. "
                f"PID: {self._server_process.pid}"
            )

            # 2. Launch Unity after a short startup interval.
            # This gives the tracking server time to initialize.
            QTimer.singleShot(1500, self._launch_unity)

        except Exception as exc:
            print(
                f"[game_launcher] Failed to start tracking: {exc}"
            )
            self._stop_server()
            self._reset_session()

    def _launch_unity(self):
        # The session may have been stopped during the startup delay.
        if self._active_game_id is None or self._finishing:
            return

        if (
            self._server_process is None
            or self._server_process.poll() is not None
        ):
            print(
                "[game_launcher] Tracking server exited before "
                "Unity could launch."
            )
            self._finish_session()
            return

        try:
            # 3. Launch the standalone Unity game.
            self._unity_process = subprocess.Popen(
                [str(UNITY_EXE)],
                cwd=str(UNITY_EXE.parent),
            )

            print(
                "[game_launcher] Unity game launched. "
                f"PID: {self._unity_process.pid}"
            )

            self._poll_timer.start()
            self.game_started.emit(self._active_game_id)

        except Exception as exc:
            print(
                f"[game_launcher] Failed to launch Unity: {exc}"
            )
            self._finish_session()

    def _session_is_running(self):
        return (
            self._active_game_id is not None
            and not self._finishing
        )

    def _check_process_status(self):
        # The Unity game controls the end of the session.
        if (
            self._unity_process is not None
            and self._unity_process.poll() is not None
        ):
            exit_code = self._unity_process.returncode

            print(
                "[game_launcher] Unity game exited with code "
                f"{exit_code}"
            )

            self._finish_session()
            return

        # If tracking unexpectedly stops while Unity is running,
        # report it in the console without ending the game.
        if (
            self._server_process is not None
            and self._server_process.poll() is not None
            and self._unity_process is not None
            and self._unity_process.poll() is None
        ):
            print(
                "[game_launcher] Warning: tracking server "
                "has stopped while Unity is still running."
            )

    def stop(self):
        """Stop the Unity game and tracking server if necessary."""
        self._finishing = True
        self._poll_timer.stop()

        self._stop_process(self._unity_process)
        self._stop_process(self._server_process)

        self._check_and_import_latest_session()
        game_id = self._active_game_id or "reach_and_collect"

        self._reset_session()
        self.game_finished.emit(game_id)

    def _finish_session(self):
        if self._finishing:
            return

        self._finishing = True
        self._poll_timer.stop()

        game_id = self._active_game_id or "reach_and_collect"

        # Unity has exited; stop tracking if it is still running.
        self._stop_process(self._server_process)

        # Import the session recorded by Unity.
        self._check_and_import_latest_session()

        self._reset_session()
        self.game_finished.emit(game_id)

    def _stop_server(self):
        self._stop_process(self._server_process)
        self._server_process = None

    @staticmethod
    def _stop_process(process):
        if process is None or process.poll() is not None:
            return

        try:
            process.terminate()
            process.wait(timeout=2)

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

        except Exception as exc:
            print(f"[game_launcher] Process cleanup error: {exc}")

    def _reset_session(self):
        self._server_process = None
        self._unity_process = None
        self._active_game_id = None
        self._finishing = False

    def _check_and_import_latest_session(self):
        userprofile = Path(
            os.environ.get("USERPROFILE", str(Path.home()))
        )

        search_dirs = [
            userprofile
            / "AppData"
            / "LocalLow"
            / "DefaultCompany"
            / "RehabQuest-Unity"
            / "RehabQuestSessions",
            PROJECT_ROOT / "RehabQuestSessions",
            userprofile / "AppData" / "LocalLow",
        ]

        found_files = []

        for directory in search_dirs:
            if not directory.exists():
                continue

            try:
                for path in directory.rglob(
                    "reach_and_collect_session_*.json"
                ):
                    if path.is_file():
                        found_files.append(path)
            except OSError as exc:
                print(
                    "[game_launcher] Could not scan "
                    f"{directory}: {exc}"
                )

        if not found_files:
            print(
                "[game_launcher] No Unity session JSON found."
            )
            return

        latest_file = max(
            found_files,
            key=lambda path: path.stat().st_mtime,
        )

        print(
            "[game_launcher] Latest Unity session: "
            f"{latest_file}"
        )

        try:
            import_unity_session(
                str(latest_file),
                self._user_id,
            )
        except Exception as exc:
            print(
                "[game_launcher] Session import failed: "
                f"{exc}"
            )
