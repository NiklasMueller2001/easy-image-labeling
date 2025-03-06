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


def get_lowest_image_id(cur: sqlite3.Cursor, dataset: str) -> int:
    """
    Rtrieve lowest DatasetId of row in Image table, that contains
    unlabelled image.
    """
    min_dataset_id = cur.execute(
        "SELECT MIN(DatasetID) FROM Image WHERE Dataset = ? AND LabelName IS NULL",
        (dataset,),
    ).fetchone()[0]
    return min_dataset_id


def get_image_name(cur: sqlite3.Cursor, dataset: str, dataset_id: int) -> int:
    """
    Retrieve image name for given Dataset and DatasetId.
    """
    image_name = cur.execute(
        "SELECT ImageName FROM Image WHERE Dataset = ? AND DatasetID = ?",
        (dataset, dataset_id),
    ).fetchone()[0]
    return image_name


def get_size_of_dataset(cur: sqlite3.Cursor, dataset: str) -> int:
    """
    Retrieve the totatl number of images in the specified dataset.
    """
    return cur.execute(
        "SELECT MAX(DatasetID) FROM Image WHERE Dataset = ?",
        (dataset,),
    ).fetchone()[0]


def get_num_of_skipped_images(cur: sqlite3.Cursor, dataset: str) -> int:
    """
    Retrieve the number of skipped images in the specified dataset.
    """
    return cur.execute(
        "SELECT COUNT(*) FROM Image WHERE Dataset = ? AND LabelName = ?",
        (dataset, "Unknown"),
    ).fetchone()[0]


def get_num_of_labelled_images(cur: sqlite3.Cursor, dataset: str) -> int:
    """
    Retrieve the number of labelled images (skipped images included) in
    the specified dataset.
    """
    return cur.execute(
        "SELECT COUNT(*) FROM Image WHERE Dataset = ? AND LabelName IS NOT NULL",
        (dataset,),
    ).fetchone()[0]


def get_labels(cur: sqlite3.Cursor, dataset: str) -> list[str]:
    """
    Retrieve all labels belonging to a dataset.
    """
    labels = cur.execute(
        "SELECT LabelName FROM Label WHERE Dataset = ?",
        (dataset,),
    ).fetchall()
    return list(map(lambda _tuple: _tuple[0], labels))


def set_image_label(
    cur: sqlite3.Cursor, dataset: str, dataset_id: int, label: str | None
) -> None:
    """
    Set label column of image inside dataset with given dataset id to
    specified value. If no label is specified, set label to 'Unknown'.
    """
    if label is None:
        label = "Unknown"  # Skipped images appear with label "Unknown" in database
    cur.execute(
        "UPDATE IMAGE SET LabelName = ? WHERE Dataset = ? AND DatasetID = ?",
        (label, dataset, dataset_id),
    )


def reset_dataset_labels(cur: sqlite3.Cursor, dataset: str) -> None:
    cur.execute(
        "UPDATE IMAGE SET LabelName = NULL WHERE Dataset = ?",
        (dataset,),
    )
