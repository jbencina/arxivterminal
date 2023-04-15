from pathlib import Path

from appdirs import user_data_dir, user_log_dir

APP_NAME = "arxivterminal"
DATABASE_PATH = Path(user_data_dir(APP_NAME)) / "papers.db"
MODEL_PATH = Path(user_data_dir(APP_NAME)) / "model.joblib"
LOG_PATH = Path(user_log_dir(APP_NAME)) / f"{APP_NAME}.log"

__all__ = ["APP_NAME", "DATABASE_PATH", "MODEL_PATH", "LOG_PATH"]
