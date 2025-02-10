from easy_image_labeling import create_app
from flask import render_template, session
from waitress import serve
from flask_wtf import CSRFProtect
from easy_image_labeling.dataset_manager import DatasetManager

app = create_app()
csrf = CSRFProtect(app)


@app.route("/")
@app.route("/index")
def index():
    session["datasets"] = list(
        map(lambda data: data.address.stem, DatasetManager().managed_datasets)
    )
    print(list(map(lambda data: data.address.stem, DatasetManager().managed_datasets)))
    return render_template("index.html")


if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=8080)
    app.run(host="0.0.0.0", port=8000, debug=True)
