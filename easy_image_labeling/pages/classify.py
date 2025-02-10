from flask import Blueprint, render_template

bp = Blueprint("classify", __name__)


@bp.route("/classify/<dataset>", methods=["POST", "GET"])
def classify(dataset: str):
    return dataset
