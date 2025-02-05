from flask import (
    Blueprint,
    g,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
)
from easy_image_labeling.forms import LabelNameFormContainer

bp = Blueprint("config", __name__)


@bp.route("/set_number_of_labels", methods=["GET", "POST"])
def configure_labels():
    return render_template("class_number.html")


@bp.route("/set_label_names", methods=["POST", "GET"])
def set_number_of_classes():
    if request.method == "POST":
        session["num_classes"] = int(request.form["number_of_classes"])
        label_names_form = LabelNameFormContainer()
        for _ in range(session["num_classes"]):
            label_names_form.label_names.append_entry()
    return render_template("class_names.html", form=label_names_form)


@bp.route("/upload_dataset", methods=["POST", "GET"])
def set_class_names():
    if request.method == "POST":
        label_names_form = LabelNameFormContainer()
        label_names_form.process(request.form)
        label_names = dict()
        if not label_names_form.validate_on_submit():
            return render_template("class_names.html", form=label_names_form)
        for i, label_name in enumerate(label_names_form.label_names.data):
            label_names[f"label_{i}"] = label_name["label_name"]
        session["label_names"] = label_names
    return "<br>".join(session["label_names"])
