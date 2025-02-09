import os
from easy_image_labeling.config import DevConfig
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="./templates")
    app.config.from_object(DevConfig)
    from easy_image_labeling.pages import selection
    app.register_blueprint(selection.bp)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
