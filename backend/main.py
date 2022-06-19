from flask import Blueprint, render_template
from . import login_required, events_db
from datetime import datetime
import pymongo

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    now = datetime.now().replace(second=0, microsecond=0).isoformat()[:-3]
    ongoing_events = events_db.find({"start": {"$lt": now}, "end": {"$gt": now}}).sort("end", pymongo.ASCENDING)
    upcoming_events = events_db.find({"start": {"$gt": now}}).sort("end", pymongo.ASCENDING)
    return render_template('index.html', ongoing_events=ongoing_events, upcoming_events=upcoming_events)
