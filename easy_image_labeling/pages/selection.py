from easy_image_labeling.forms import (
    LabelNameFormContainer,
    UploadFolderForm,
    RemoveMultipleDatasetsForm,
)
from easy_image_labeling.dataset_manager import Dataset, DatasetManager
from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    url_for,
    redirect,
    render_template,
    request,
    session,
)
from pathlib import Path
from werkzeug.utils import secure_filename

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
    upload_form = UploadFolderForm()
    if request.method == "POST":
        label_names_form = LabelNameFormContainer()
        label_names_form.process(request.form)
        label_names = dict()
        if not label_names_form.validate_on_submit():
            return render_template("class_names.html", form=label_names_form)
        for i, label_name in enumerate(label_names_form.label_names.data):
            label_names[f"label_{i}"] = label_name["label_name"]
        session["label_names"] = label_names
    return render_template("upload_dataset.html", form=upload_form)


@bp.route("/", methods=["POST"])
def upload_folder():
    if request.method == "POST":
        upload_form = UploadFolderForm()
        upload_form.process(request.form)
        uploaded_files = request.files.getlist("files")
        dataset_name = upload_form.dataset_name.data
        if dataset_name is None:
            flash("Invalid dataset name.")
            return render_template("index.html")
        dataset_name = secure_filename(dataset_name)
        upload_form.files.data = uploaded_files
        if upload_form.validate_on_submit():
            upload_path = current_app.config["DATASET_FOLDER"] / dataset_name
            if not Path(upload_path).exists():
                Path(upload_path).mkdir(parents=True)  # Ensure upload directory exists
            for file in upload_form.files.data:
                filename = secure_filename(file.filename)
                file.save(upload_path / filename)
            DatasetManager().add(Dataset(upload_path))
            flash("Files uploaded successfully!", "success")
            return redirect(url_for("index"))
        for field in upload_form.errors:
            if upload_form.errors[field]:
                for error in upload_form.errors[field]:
                    flash(error)
    return redirect(url_for("config.set_class_names"))


@bp.route("/remove_datasets", methods=["POST", "GET"])
def select_datasets_to_remove():
    remove_datasets_form = RemoveMultipleDatasetsForm()
    if request.method == "GET":
        for dataset_name in g.dataset_names:
            remove_datasets_form.remove_datasets_forms.append_entry(
                {"dataset_name": dataset_name}
            )
        print(DatasetManager().managed_datasets)
    return render_template("remove_datasets.html", form=remove_datasets_form)


@bp.route("/index", methods=["POST"])
def remove_datasets():
    remove_datasets_form = RemoveMultipleDatasetsForm()
    if request.method == "POST":
        remove_datasets_form.process(request.form)
        if remove_datasets_form.validate_on_submit():
            for input_form_data in remove_datasets_form.remove_datasets_forms.data:
                if input_form_data["marked"]:
                    dataset_to_remove = input_form_data["dataset_name"]
                    DatasetManager().remove(dataset_to_remove)
                    flash(f"Removed dataset {dataset_to_remove}")
    return redirect(url_for("index"))
