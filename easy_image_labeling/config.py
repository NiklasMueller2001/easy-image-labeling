from pathlib import Path


class Config:
    with open("secret.env") as f:
        SECRET_KEY = f.read()
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 10MB
    DATASET_FOLDER = Path(__file__).parent / "static" / "datasets"
    DB_URL = Path(__file__).parent / "db" / "database.sqlite"
    DB_SCHEMA = Path(__file__).parent / "db" / "schema.sql"
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"
    UPLOAD_FILENAME = "LabelingResults"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
