from flask import Flask, redirect, url_for, session
from flask_cas import CAS
from functools import wraps
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("localhost", 27017)
mongodb = client.TIIImeline
events_db = mongodb.events
groups_db = mongodb.groups


def create_app():
    template_dir = Path("frontend", "templates")
    static_dir = Path("frontend", "static")

    app = Flask(__name__, template_folder=str(template_dir.absolute()), static_folder=(static_dir.absolute()))
    CAS(app)
    app.config['CAS_SERVER'] = 'https://login.iiit.ac.in'
    app.config['CAS_AFTER_LOGIN'] = 'main.index'
    app.config['CAS_AFTER_LOGOUT'] = 'logout'
    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .events import events as events_blueprint
    app.register_blueprint(events_blueprint)

    from .groups import groups as groups_blueprint
    app.register_blueprint(groups_blueprint)

    return app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session["CAS_ATTRIBUTES"]["cas:E-Mail"]
        except KeyError:
            return redirect(url_for('cas.login'))
        else:
            return f(*args, **kwargs)

    return decorated_function


def get_email():
    return session["CAS_ATTRIBUTES"]["cas:E-Mail"]


def prettify_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M").ctime()
