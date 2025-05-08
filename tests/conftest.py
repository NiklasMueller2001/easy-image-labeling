import pytest
import sqlite3

from pathlib import Path


DB_SCHEMA_PATH = Path(__file__).parents[1] / "easy_image_labeling" / "db" / "schema.sql"
DB_PATH = Path(__file__).parent / "test_db.sqlite"


@pytest.fixture()
def get_test_db():
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


@pytest.fixture()
def add_dataset(get_test_db):
    """
    Factory as fixture to add a dataset with specified number of image
    name entries to database.
    """

    created_datasets = []

    def _add_dataset(name: str, number_of_images: int):
        # Create data to add to Image table
        # DatasetIDs start at 0 and go until number_of_images - 1
        dataset_ids = list(range(number_of_images))
        image_names = [f"{name}Image{i}" for i in range(number_of_images)]
        dataset_name_list = [name] * number_of_images
        data = list(zip(dataset_name_list, image_names, dataset_ids))

        # Exectute transaction
        get_test_db.executemany(
            "INSERT INTO Image (Dataset, ImageName, DatasetID) VALUES (?, ?, ?)",
            data,
        )
        created_datasets.append(name)

    yield _add_dataset

    for dataset in created_datasets:
        get_test_db.execute("DELETE FROM Image WHERE Dataset = ?", (dataset,))


@pytest.fixture()
def add_labels(get_test_db):
    """
    Factory as fixture to add categories belonging to a dataset.
    """

    created_labels = dict()

    def _add_labels(labels: list[str], dataset: str):
        # Create data to add to Image table
        dataset_ids = list(range(1, len(labels) + 1))
        dataset_name_list = [dataset] * len(labels)
        data = list(zip(dataset_name_list, labels, dataset_ids))

        # Exectute transaction
        get_test_db.executemany(
            "INSERT INTO Label (Dataset, LabelName, DatasetID) VALUES (?, ?, ?)",
            data,
        )
        created_labels[dataset] = labels

    yield _add_labels

    for dataset, labels in created_labels.items():
        get_test_db.execute(
            f"DELETE FROM Label WHERE Dataset = ? AND LabelName IN ({('?,' * len(labels))[:-1]})",
            (
                dataset,
                *labels,
            ),
        )


@pytest.fixture()
def assign_label(get_test_db):
    """
    Factory as fixture to update the LabelName value for a specified
    ImageID in the database.
    """

    changed_image_ids = []

    def _assign_label(label: str, image_id: int):
        get_test_db.execute(
            "UPDATE IMAGE SET LabelName = ? WHERE ImageId = ?",
            (label, image_id),
        )
        changed_image_ids.append(image_id)

    yield _assign_label

    for id in changed_image_ids:
        get_test_db.execute(
            "UPDATE IMAGE SET LabelName = NULL WHERE ImageId = ?",
            (id,),
        )


@pytest.fixture()
def fill_db(add_dataset, add_labels, assign_label):
    """
    Fixture to fill a database with 2 datasets and corresponding
    labels, as well as assign labels to most images.

    Parameters
    ----------
    class_ids_list: list[list[int]] | None = None
        List of the form [[Index_4, Index_9, ...], [Index_j, ...], ...]
        where list i contains the indices j...k. An image in the
        database with ImageId l will be given the LabelName Class{i}
        if the i_th list in class_ids contains the index l.
    skipped_ids_list: list[int] | None = None
        List of image ids to assign the label 'Unknown',
        corresponding to a skipped label.
    """

    datasets = ["Dataset1", "Dataset2"]

    def _fill_db(
        class_ids_list: list[list[int]], skipped_ids_list: list[int] | None = None
    ):
        if class_ids_list is None:
            class_ids_list = []
        if skipped_ids_list is None:
            skipped_ids_list = []

        label_names = [f"Class{i}" for i in range(1, len(class_ids_list) + 1)]
        # Create datasets and label categories
        for dataset in datasets:
            add_dataset(dataset, 10)
            add_labels(label_names, dataset)
        # Assign labels
        for i, ids in enumerate(class_ids_list):
            label_name_i = f"Class{i + 1}"
            for id in ids:
                assign_label(label_name_i, id)
        # Assign skipped labels
        for id in skipped_ids_list:
            assign_label("Unknown", id)

    yield _fill_db
