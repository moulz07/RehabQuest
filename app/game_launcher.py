
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
    PROJECT_ROOT
    / "communication"
    / "mediapipe_unity_server.py"
)

PYTHON_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

if not PYTHON_EXE.is_file():
    PYTHON_EXE = Path(sys.executable)

UNITY_EXE = (
    PROJECT_ROOT
    / "unity_build"
    / "RehabQuest-Unity.exe"
)

UNITY_SESSION_FILENAME = "reach_and_collect_session_*.json"

UNITY_SESSION_DIRS = [
    Path.home()
    / "AppData"
    / "LocalLow"
    / "DefaultCompany"
    / "RehabQuest-Unity"
    / "RehabQuestSessions",
    PROJECT_ROOT / "RehabQuestSessions",
    PROJECT_ROOT
    / "RehabQuest-Unity"
    / "RehabQuestSessions",
]


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

        # Track session files so an old export is not imported
        # accidentally when a new game produces no export.
        self._session_files_before_launch = {}

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(500)
        self._poll_timer.timeout.connect(
            self._check_process_status
        )

    # -----------------------------------------------------
    # Launch
    # -----------------------------------------------------

    def launch(self, game_id: str, user_id: str):
        """Start the tracking server and the requested Unity game."""
        if self._session_is_running():
            print(
                "[game_launcher] A session is already active."
            )
            return

        if not SERVER_SCRIPT.is_file():
            print(
                "[game_launcher] Tracking server not found: "
                f"{SERVER_SCRIPT}"
            )
            return

        if not PYTHON_EXE.is_file():
            print(
                "[game_launcher] Python executable not found: "
                f"{PYTHON_EXE}"
            )
            return

        if not UNITY_EXE.is_file():
            print(
                "[game_launcher] Unity executable not found: "
                f"{UNITY_EXE}"
            )
            print(
                "[game_launcher] Build the Unity game and place "
                "RehabQuest-Unity.exe in unity_build."
            )
            return

        self._active_game_id = game_id
        self._user_id = user_id
        self._finishing = False

        self._session_files_before_launch = (
            self._snapshot_session_files()
        )

        try:
            # Start the MediaPipe tracking server.
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

            # Give the tracking server time to initialize.
            QTimer.singleShot(1500, self._launch_unity)

        except Exception as exc:
            print(
                "[game_launcher] Failed to start tracking: "
                f"{exc}"
            )
            self._stop_server()
            self._reset_session()

    def _launch_unity(self):
        """Launch Unity after confirming tracking is still running."""
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
                "[game_launcher] Failed to launch Unity: "
                f"{exc}"
            )
            self._finish_session()

    # -----------------------------------------------------
    # Process monitoring
    # -----------------------------------------------------

    def _session_is_running(self):
        return (
            self._active_game_id is not None
            and not self._finishing
        )

    def _check_process_status(self):
        """Detect Unity exit and unexpected tracking-server exit."""
        if self._finishing:
            return

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

    # -----------------------------------------------------
    # Stop and cleanup
    # -----------------------------------------------------

    def stop(self):
        """Stop the active game and tracking server."""
        if self._active_game_id is None:
            return

        if self._finishing:
            return

        self._finishing = True
        self._poll_timer.stop()

        self._stop_process(self._unity_process)
        self._stop_process(self._server_process)

        game_id = self._active_game_id

        self._check_and_import_latest_session()

        self._reset_session()
        self.game_finished.emit(game_id)

    def _finish_session(self):
        """Finish a session after Unity exits."""
        if self._finishing:
            return

        self._finishing = True
        self._poll_timer.stop()

        game_id = self._active_game_id or "reach_and_collect"

        # Stop tracking if it is still running.
        self._stop_process(self._server_process)

        self._check_and_import_latest_session()

        self._reset_session()
        self.game_finished.emit(game_id)

    def _stop_server(self):
        self._stop_process(self._server_process)
        self._server_process = None

    @staticmethod
    def _stop_process(process):
        """Terminate a process and force-kill it if necessary."""
        if process is None or process.poll() is not None:
            return

        try:
            process.terminate()
            process.wait(timeout=3)

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)

        except Exception as exc:
            print(
                "[game_launcher] Process cleanup error: "
                f"{exc}"
            )

    def _reset_session(self):
        self._server_process = None
        self._unity_process = None
        self._active_game_id = None
        self._finishing = False
        self._session_files_before_launch = {}

    # -----------------------------------------------------
    # Session discovery and import
    # -----------------------------------------------------

    def _snapshot_session_files(self):
        """Record session file modification times before launch."""
        snapshot = {}

        for directory in UNITY_SESSION_DIRS:
            if not directory.is_dir():
                continue

            try:
                for path in directory.glob(
                    UNITY_SESSION_FILENAME
                ):
                    if path.is_file():
                        try:
                            snapshot[str(path.resolve())] = (
                                path.stat().st_mtime_ns
                            )
                        except OSError:
                            continue

            except OSError as exc:
                print(
                    "[game_launcher] Could not scan "
                    f"{directory}: {exc}"
                )

        return snapshot

    def _check_and_import_latest_session(self):
        """Import the newest session file created or modified this run."""
        candidates = []

        for directory in UNITY_SESSION_DIRS:
            if not directory.is_dir():
                continue

            try:
                for path in directory.glob(
                    UNITY_SESSION_FILENAME
                ):
                    if not path.is_file():
                        continue

                    try:
                        modified_ns = path.stat().st_mtime_ns
                    except OSError:
                        continue

                    previous_ns = (
                        self._session_files_before_launch.get(
                            str(path.resolve())
                        )
                    )

                    # Ignore files that existed unchanged before
                    # the current game was launched.
                    if (
                        previous_ns is not None
                        and modified_ns <= previous_ns
                    ):
                        continue

                    candidates.append(path)

            except OSError as exc:
                print(
                    "[game_launcher] Could not scan "
                    f"{directory}: {exc}"
                )

        if not candidates:
            print(
                "[game_launcher] No new or updated Unity session "
                "JSON found for this run."
            )
            return

        try:
            latest_file = max(
                candidates,
                key=lambda path: path.stat().st_mtime_ns,
            )
        except OSError as exc:
            print(
                "[game_launcher] Could not identify latest "
                f"session file: {exc}"
            )
            return

        print(
            "[game_launcher] Importing Unity session: "
            f"{latest_file}"
        )

        try:
            import_unity_session(
                str(latest_file),
                self._user_id,
            )

            print(
                "[game_launcher] Session import completed."
            )

        except Exception as exc:
            print(
                "[game_launcher] Session import failed: "
                f"{exc}"
            )
