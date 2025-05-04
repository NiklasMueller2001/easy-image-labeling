from easy_image_labeling.db.db import insert_labels, bulk_insert_images

import random


def test_insert_labels(get_empty_db):
    """
    GIVEN an empty database
    WHEN labels are added to  two datasets
    THEN check Dataset, LabelName, DatasetID fields from the Label
    table are defined correctly.
    """

    dataset_name1 = "Dataset1"
    dataset_name2 = "Dataset2"

    # Create new labels
    labels1 = ["MyLabel1", "MyLabel2", "MyLabel3"]
    labels2 = ["MyOtherLabel1", "MyOtherLabel2"]

    # Insert into database
    insert_labels(get_empty_db, dataset_name1, labels1)
    insert_labels(get_empty_db, dataset_name2, labels2)

    # Check labels
    data = get_empty_db.execute("SELECT * FROM Label").fetchall()
    total_ids, datasets, label_names, dataset_ids = tuple(zip(*data))
    assert total_ids == tuple(range(1, len(labels1) + len(labels2) + 1))
    assert datasets == tuple(
        [dataset_name1] * len(labels1) + [dataset_name2] * len(labels2)
    )
    assert label_names == tuple(labels1 + labels2)
    assert dataset_ids == tuple(
        list(range(1, len(labels1) + 1)) + list(range(1, len(labels2) + 1))
    )


def test_bulk_insert_images(get_empty_db):
    """
    GIVEN an empty database
    WHEN 2 new datasets are added with 10 images each
    THEN check the Dataset, ImageName, DatasetID fields are defined
    correctly.
    """

    # Create 2 datasets
    dataset_name1 = "MyDataset"
    dataset_name2 = "MyOtherDataset"
    image_names1 = [f"MyImage{i}" for i in range(1, 11)]
    image_names2 = image_names1.copy()
    random.shuffle(image_names2)

    # Insert into database
    bulk_insert_images(get_empty_db, dataset_name1, image_names1, chunk_size=10)
    bulk_insert_images(get_empty_db, dataset_name2, image_names2, chunk_size=10)

    # Check results
    data = get_empty_db.execute("SELECT * FROM Image").fetchall()
    total_ids, datasets, image_names, dataset_ids, labels = tuple(zip(*data))
    assert total_ids == tuple(range(1, 21))
    assert datasets == tuple([dataset_name1] * 10 + [dataset_name2] * 10)
    assert image_names[: len(image_names1)] == tuple(image_names1)
    assert image_names[len(image_names1) :] == tuple(image_names2)
    assert dataset_ids == tuple(
        list(range(1, len(image_names1) + 1)) + list(range(1, len(image_names2) + 1))
    )
    assert all(label == None for label in labels)
