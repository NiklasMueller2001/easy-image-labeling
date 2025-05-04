import pytest
import sqlite3

from pathlib import Path


DB_SCHEMA_PATH = Path(__file__).parents[1] / "easy_image_labeling" / "db" / "schema.sql"
DB_PATH = Path(__file__).parent / "test_db.sqlite"


@pytest.fixture()
def get_empty_db():
    """
    Fixture to create an empty database with schema as specified in
    project.
    """

    try:
        db_con = sqlite3.connect(DB_PATH)
        db_cursor = db_con.cursor()
        db_cursor.executescript(DB_SCHEMA_PATH.read_text(encoding="utf8"))
        yield db_cursor
    finally:
        db_con.close()
