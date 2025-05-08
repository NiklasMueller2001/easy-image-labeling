import os
from easy_image_labeling.config import DevConfig
from easy_image_labeling.db.db import sqlite_connection
from easy_image_labeling.pages import selection
from easy_image_labeling.pages import classify
from easy_image_labeling.pages import export
from flask import Flask, current_app
from easy_image_labeling.dataset_manager import Dataset, DatasetManager
from pathlib import Path

__version__ = "0.2.2"


def create_app() -> Flask:
    app = Flask(__name__, template_folder="./templates")
    app.config.from_object(DevConfig)
    app.register_blueprint(selection.bp)
    app.register_blueprint(classify.bp)
    app.register_blueprint(export.bp)
    app.jinja_env.filters["zip"] = zip
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    fetch_existing_datasets(app)
    initialize_database(app)
    return app


def fetch_existing_datasets(app: Flask) -> None:
    with app.app_context():
        dataset_folder = current_app.config.get("DATASET_FOLDER", None)
        Dataset.dataset_root_folder = current_app.config["DATASET_FOLDER"]
    if dataset_folder is None:
        raise RuntimeError("DATASET_FOLDER missing in app config.")
    for dataset_path in Path(dataset_folder).glob("*"):
        DatasetManager().add(Dataset(dataset_path))


def initialize_database(app: Flask) -> None:
    with app.app_context():
        db_path = current_app.config.get("DB_URL", None)
        db_schema_path: Path | None = current_app.config.get("DB_SCHEMA", None)
        for parameter in ("DB_URL", "DB_SCHEMA"):
            if current_app.config.get(parameter, None) is None:
                raise RuntimeError(f"{parameter} missing in app config.")
        if db_schema_path is None:
            raise KeyError("DB_SCHEMA parameter is missing in app config.")
        if not db_schema_path.exists():
            raise RuntimeError(f"Database schema file {db_schema_path} does not exist.")
        with sqlite_connection(db_path) as cur:
            cur.executescript(db_schema_path.read_text(encoding="utf8"))
