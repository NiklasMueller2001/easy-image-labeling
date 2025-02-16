import sqlite3
from contextlib import contextmanager


@contextmanager
def sqlite_connection(db_path):
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert_labels(cur: sqlite3.Cursor, dataset: str, labels: list[str]) -> None:
    """
    Insert labels into database.
    """
    dataset_ids = list(range(1, len(labels) + 1))
    dataset_name_list = [dataset] * len(labels)
    data = list(zip(dataset_name_list, labels, dataset_ids))
    print(data)
    cur.executemany(
        "INSERT INTO Label (Dataset, LabelName, DatasetID) VALUES (?, ?, ?)",
        data,
    )


def bulk_insert_images(
    cur: sqlite3.Cursor, dataset: str, image_names: list[str], chunk_size: int
) -> None:
    """
    Insert entire dataset of images into Image table in a chunked-wise
    fashion.
    """

    def chunk_data(data):
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    dataset_ids = list(range(1, len(image_names) + 1))
    dataset_name_list = [dataset] * len(image_names)
    data = list(zip(dataset_name_list, image_names, dataset_ids))
    for chunked_data in chunk_data(data):
        cur.executemany(
            "INSERT INTO Image (Dataset, ImageName, DatasetID) VALUES (?, ?, ?)",
            chunked_data,
        )


def remove_dataset_from_db(cur: sqlite3.Cursor, dataset: str) -> None:
    """
    Remove all images and labels that belong to the given dataset.
    """
    cur.execute("DELETE FROM Image WHERE Dataset = ?", (dataset,))
    cur.execute("DELETE FROM Label WHERE Dataset = ?", (dataset,))
