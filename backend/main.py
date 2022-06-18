from flask import Flask, render_template
from pathlib import Path

template_dir = Path("..", "frontend", "templates")
static_dir = Path("..", "frontend", "static")
app = Flask(__name__, template_folder=str(template_dir.absolute()), static_folder=(static_dir.absolute()))


@app.route("/")
def index():
    return render_template("index.html")
