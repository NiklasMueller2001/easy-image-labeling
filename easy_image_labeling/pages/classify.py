from flask import Blueprint, render_template, redirect, url_for, current_app, request
from easy_image_labeling.db.db import (
    sqlite_connection,
    get_lowest_image_id,
    get_labels,
    get_image_name,
    set_image_label,
)
from easy_image_labeling.dataset_manager import DatasetManager
from easy_image_labeling.forms import MutliButtonForm
from pathlib import Path

bp = Blueprint("classify", __name__)


def create_multibutton_form(labels: list[str]) -> MutliButtonForm:
    multi_button_form = MutliButtonForm()
    for i, label in enumerate(labels):
        multi_button_form.label_buttons.append_entry(label)
        multi_button_form.label_buttons[i].label.text = label
        multi_button_form.label_buttons[i].id = label
    return multi_button_form


@bp.route("/classify/<dataset>", methods=["POST", "GET"])
def classify_next_image(dataset: str):
    with sqlite_connection(current_app.config["DB_URL"]) as cur:
        image_id = get_lowest_image_id(cur, dataset)
    return redirect(url_for("classify.classify", dataset=dataset, id=image_id))


@bp.route("/classify/<dataset>/<id>", methods=["POST", "GET"])
def classify(dataset: str, id: int):
    """
    Render html template for displaying one image from given Dataset
    and DatasetID and form for labelling said image.
    """
    with sqlite_connection(current_app.config["DB_URL"]) as cur:
        dataset_labels = get_labels(cur, dataset)
        image_name = get_image_name(cur, dataset, id)
    image_address = f"datasets/{dataset}/{image_name}"
    multi_button_form = create_multibutton_form(dataset_labels)
    return render_template(
        "classify_image.html",
        image=image_address,
        form=multi_button_form,
        dataset=dataset,
        image_id=id,
    )


@bp.route("/classify/<dataset>/<id>/submit", methods=["POST"])
def submit_classification(dataset: str, id: int):
    """
    Process the submitted form, update image label in the database, and
    load the next image.
    """
    multi_button_form = MutliButtonForm()
    id = int(id)
    if request.method == "POST":
        if multi_button_form.validate_on_submit():
            for k, v in request.form.items():
                if k.startswith("label_buttons"):
                    selected_label = v

        with sqlite_connection(current_app.config["DB_URL"]) as cur:
            set_image_label(cur, dataset, id, selected_label)
    return redirect(url_for("classify.classify", dataset=dataset, id=id + 1))


@bp.route("/classify/<dataset>/<id>/skip", methods=["POST"])
def handle_move_button(dataset: str, id: int):
    """
    Process the submitted form, update image label in the database, and
    load the next image.
    """
    action = request.form.get("action")
    id = int(id)
    match action:
        case "skip":
            with sqlite_connection(current_app.config["DB_URL"]) as cur:
                set_image_label(cur, dataset, id, None)
            return redirect(url_for("classify.classify", dataset=dataset, id=id + 1))
        case "back":
            return redirect(url_for("classify.classify", dataset=dataset, id=id - 1))
        case _:
            return redirect(url_for("/"))
