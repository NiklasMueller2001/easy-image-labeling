from easy_image_labeling import create_app
from flask import render_template
from waitress import serve
from werkzeug.utils import secure_filename
from flask_wtf import CSRFProtect

app = create_app()
csrf = CSRFProtect(app)
print()


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=8080)
    app.run(host="0.0.0.0", port=8000, debug=True)  
