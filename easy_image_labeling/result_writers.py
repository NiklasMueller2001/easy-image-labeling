import csv
import json
from easy_image_labeling.db.db import LabeledImage, LabeledImageColumns
from flask import current_app


def write_to_csv(upload_file_name: str, results: list[LabeledImage]) -> None:
    """Write results to csv file."""

    with open(
        (current_app.config["UPLOAD_FOLDER"] / upload_file_name).with_suffix(".csv"),
        "w",
    ) as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(LabeledImageColumns)
        csv_writer.writerows(results)


def write_to_json(upload_file_name: str, results: list[LabeledImage]) -> None:
    """Write results to json file."""

    results_dict = {image_name: label_name for _, image_name, label_name in results}
    print(results_dict)
    with open(
        (current_app.config["UPLOAD_FOLDER"] / upload_file_name).with_suffix(".json"),
        "w",
    ) as result_file:
        json.dump(results_dict, result_file)
