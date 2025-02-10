import os
from easy_image_labeling.config import DevConfig
from easy_image_labeling.pages import selection
from easy_image_labeling.pages import classify
from flask import Flask, current_app
from easy_image_labeling.dataset_manager import Dataset, DatasetManager
from pathlib import Path


def create_app():
    app = Flask(__name__, template_folder="./templates")
    app.config.from_object(DevConfig)
    app.register_blueprint(selection.bp)
    app.register_blueprint(classify.bp)
    app.jinja_env.filters['zip'] = zip
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    fetch_existing_datasets(app)

    return app


def fetch_existing_datasets(app: Flask):
    with app.app_context():
        dataset_folder = current_app.config.get("DATASET_FOLDER", None)
        Dataset.dataset_root_folder = current_app.config["DATASET_FOLDER"]
    if dataset_folder is None:
        raise RuntimeError("DATASET_FOLDER missing in app config.")
    for dataset_path in Path(dataset_folder).glob("*"):
        DatasetManager().add(Dataset(dataset_path))
