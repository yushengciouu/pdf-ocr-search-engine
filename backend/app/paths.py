"""
Runtime paths for source and packaged deployments.
"""
import os
from pathlib import Path


def get_app_root() -> Path:
    """Return the folder that owns fuyu.sqlite, factory, backend, and frontend."""
    env_dir = os.environ.get("FUYU_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    cwd = Path.cwd().resolve()
    if cwd.name.lower() == "backend":
        return cwd.parent
    if (cwd / "backend").is_dir():
        return cwd

    # backend/app/paths.py -> backend/app -> backend -> project root
    return Path(__file__).resolve().parents[2]


def get_database_path() -> Path:
    return get_app_root() / "fuyu.sqlite"


def get_factory_path() -> Path:
    return get_app_root() / "factory"
