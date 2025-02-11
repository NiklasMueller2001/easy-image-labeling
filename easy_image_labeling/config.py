from pathlib import Path


class Config:
    with open("secret.env") as f:
        SECRET_KEY = f.read()
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 10MB
    DATASET_FOLDER = Path(__file__).parent / "static" / "datasets"


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False
