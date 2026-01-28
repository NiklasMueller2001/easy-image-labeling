import re


def test_create_new_dataset(client, tmp_path, create_tmp_dataset):
    """
    GIVEN an app instance
    WHEN dataset is uploaded in /config/upload_dataset
    THEN check if the uploaded images are accessible from the classfication endpoint.
    """

    create_tmp_dataset("dataset")

    # CASE 1: TRY TO UPLOAD ENTIRE DATASET IN ONE BATCH
    data = {"files": [], "dataset_name": "temp_dataset"}

    # Open each file and add it as a tuple: (filename, file object)
    for file in (tmp_path / "temp_dataset").glob("*"):
        with open(file, "rb") as f:
            data["files"].append((file.absolute(), file.name))

    # Add 2 labels inside the session object
    label_names = dict()
    for i in (1, 2):
        label_names[f"label_{i}"] = f"test_label_{i}"
    with client.session_transaction() as session:
        session["label_names"] = label_names

    # Add new temporary dataset
    response = client.post(
        "/config/upload_folder", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 204
    response = client.get("/config/upload_complete")
    assert response.status_code == 302  # Redirection to index page is expected

    # Check if every of the 20 different images are available via the classify/<dataset_name>/<dataset_index> url
    requests = [f"classify/temp_dataset/{i}" for i in range(1, 21)]
    responses = map(client.get, requests)
    assert all(map(lambda r: r.status_code == 200, responses))

    # # CASE 2: TRY TO UPLOAD ENTIRE DATASET IN MULTIPLE BATCHES
    create_tmp_dataset("dataset2")

    data = {"files": [], "dataset_name": "temp_dataset2"}

    for file in (tmp_path / "temp_dataset2").glob("*"):
        with open(file, "rb") as f:
            data["files"].append((file.absolute(), file.name))

    batch_size = 2
    num_batches = len(data["files"]) // batch_size + (
        len(data["files"]) % batch_size != 0
    )
    for i in range(num_batches):
        start_idx = i * batch_size
        stop_idx = (i + 1) * batch_size
        data_batch = {
            "files": data["files"][start_idx:stop_idx],
            "dataset_name": data["dataset_name"],
        }
        response = client.post(
            "/config/upload_folder",
            data=data_batch,
            query_string={"batch_idx": i},
            content_type="multipart/form-data",
        )
        assert response.status_code == 204
    requests = [f"classify/temp_dataset2/{i}" for i in range(1, 21)]
    responses = map(client.get, requests)
    assert all(map(lambda r: r.status_code == 200, responses))


def test_upload_fails_for_duplicate_dataset(client, tmp_path, create_tmp_dataset):
    """
    GIVEN an app instance
    WHEN dataset is uploaded in /config/upload_dataset
    THEN check if trying to upload the same dataset again fails with the expected error.
    """

    create_tmp_dataset("unsupported_dset")

    data = {"files": [], "dataset_name": "temp_unsupported_dset"}

    # Open each file and add it as a tuple: (filename, file object)
    for file in (tmp_path / "temp_unsupported_dset").glob("*"):
        with open(file, "rb") as f:
            data["files"].append((file.absolute(), file.name))

    # Add 2 labels inside the session object
    label_names = dict()
    for i in (1, 2):
        label_names[f"label_{i}"] = f"test_label_{i}"
    with client.session_transaction() as session:
        session["label_names"] = label_names

    # Add new temporary dataset
    response = client.post(
        "/config/upload_folder", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 204
    # Add same dataset again, expect error
    response = client.post(
        "/config/upload_folder", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 400
    # Check if flashed error message contains expected content
    exptected_flashed_message = "A dataset called temp_unsupported_dset already exists"
    response = client.post(
        "/config/dataset_upload_failed", data=data, content_type="multipart/form-data"
    )
    with client.session_transaction() as session:
        assert dict(session["_flashes"]).get("error") == exptected_flashed_message


def test_upload_fails_for_unsupported_file_types(
    client, tmp_path, create_unsupported_test_dataset
):
    """
    GIVEN an app instance
    WHEN dataset is uploaded in /config/upload_dataset
    THEN check if trying to upload a dataset containing unsupported file types fails as expected.
    """

    create_unsupported_test_dataset("unsupported_dset2")

    data = {"files": [], "dataset_name": "temp_unsupported_dset2"}

    # Open each file and add it as a tuple: (filename, file object)
    for file in (tmp_path / "temp_unsupported_dset2").glob("*"):
        with open(file, "rb") as f:
            data["files"].append((file.absolute(), file.name))

    # Add 2 labels inside the session object
    label_names = dict()
    for i in (1, 2):
        label_names[f"label_{i}"] = f"test_label_{i}"
    with client.session_transaction() as session:
        session["label_names"] = label_names

    # CASE 1: TRY TO UPLOAD ENTIRE DATASET IN ONE BATCH
    # Add new temporary dataset
    response = client.post(
        "/config/upload_folder", data=data, content_type="multipart/form-data"
    )
    # Expect failure because of unsupported file extensions
    assert response.status_code == 400
    # Check if flashed error message contains expected content
    response = client.post(
        "/config/dataset_upload_failed", data=data, content_type="multipart/form-data"
    )
    with client.session_transaction() as session:
        error_msg: str = dict(session["_flashes"]).get("error", "")
        assert re.match(
            r"Invalid file type: temp_image_\d+\.txt\.\nAllowed filetypes are \('jpg', 'jpeg', 'JPEG', 'png', 'pdf'\)",
            error_msg,
        )

    # CASE 2: TRY TO UPLOAD ENTIRE DATASET IN MULTIPLE BATCHES
    create_unsupported_test_dataset("unsupported_dset3")

    data = {"files": [], "dataset_name": "temp_unsupported_dset3"}

    # Open each file and add it as a tuple: (filename, file object)
    for file in sorted((tmp_path / "temp_unsupported_dset3").glob("*")):
        with open(file, "rb") as f:
            data["files"].append((file.absolute(), file.name))

    batch_size = 2
    num_batches = len(data["files"]) // batch_size + (
        len(data["files"]) % batch_size != 0
    )
    for i in range(num_batches):
        start_idx = i * batch_size
        stop_idx = (i + 1) * batch_size
        data_batch = {
            "files": data["files"][start_idx:stop_idx],
            "dataset_name": data["dataset_name"],
        }
        response = client.post(
            "/config/upload_folder",
            data=data_batch,
            query_string={"batch_idx": i},
            content_type="multipart/form-data",
        )
        if not any(map(lambda t: t[1].endswith(".txt"), data_batch["files"])):
            assert response.status_code == 204
        else:
            assert response.status_code == 400
            response = client.post(
                "/config/dataset_upload_failed",
                data=data_batch,
                query_string={"batch_idx": i},
                content_type="multipart/form-data",
            )
            expected_first_failed_file_name = next(
                filter(lambda t: t[1].endswith(".txt"), data_batch["files"])
            )[1]
            with client.session_transaction() as session:
                assert (
                    dict(session["_flashes"]).get("error")
                    == f"Invalid file type: {expected_first_failed_file_name}.\nAllowed filetypes are ('jpg', 'jpeg', 'JPEG', 'png', 'pdf')"
                )
