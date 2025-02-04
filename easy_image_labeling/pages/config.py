from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

bp = Blueprint("config", __name__)


@bp.route("/set_class_number", methods=["GET", "POST"])
def configure_labels():
    # g.num_classes = request.form["num_classes"]
    return render_template("class_number.html")


@bp.route("/set_number_of_classes", methods=["POST"])
def set_number_of_classes():
    if request.method == "POST":
        g.num_classes = int(request.form["number_of_classes"])
    return render_template("class_names.html")
