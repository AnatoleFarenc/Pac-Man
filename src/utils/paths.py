"""Path resolution helpers for development and PyInstaller frozen builds."""

import os
import sys
import platform


_MEIPASS: str | None = getattr(sys, '_MEIPASS', None)


def resource_path(relative_path: str) -> str:
    """Return the absolute path to a read-only bundled resource.

    In a PyInstaller bundle, files are extracted to sys._MEIPASS.
    In development, paths are resolved relative to the project root.
    """
    if _MEIPASS is not None:
        return os.path.join(_MEIPASS, relative_path)
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )))
    return os.path.join(root, relative_path)


def get_scores_path() -> str:
    """Return a writable path for high_scores.json.

    When frozen, scores are stored in the OS user-data directory so the
    bundle stays read-only. In development, the project-local file is used.
    """
    if _MEIPASS is None:
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)
        )))
        return os.path.join(root, "data", "high_scores.json")

    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME",
                              os.path.expanduser("~/.local/share"))

    data_dir = os.path.join(base, "pacman")
    os.makedirs(data_dir, exist_ok=True)

    path = os.path.join(data_dir, "high_scores.json")
    if not os.path.exists(path):
        import shutil
        shutil.copy(os.path.join(_MEIPASS, "data", "high_scores.json"), path)
    return path
