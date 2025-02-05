import os
from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="./templates")
    with open("secret.env") as f:
        app.secret_key = f.read()
    from easy_image_labeling.pages import selection
    app.register_blueprint(selection.bp)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
