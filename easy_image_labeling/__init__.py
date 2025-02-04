import os
from flask import Flask


def create_app():
    app = Flask(__name__, template_folder="./templates")
    from easy_image_labeling.pages import config
    app.register_blueprint(config.bp)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
