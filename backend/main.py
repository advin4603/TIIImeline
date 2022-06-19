from flask import Blueprint, render_template
from . import login_required, events_db, groups_db, get_email, prettify_date
from datetime import datetime
import pymongo
from pprint import pprint

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    now = datetime.now().replace(second=0, microsecond=0).isoformat()[:-3]
    email = get_email()
    group_ids_with_user = (group["_id"] for group in
                           groups_db.find({"$or": [{"emails": email}, {"host": email}]}))
    user_event_query = {"$or": [{"host": email}, *({"groups": g_id} for g_id in group_ids_with_user)]}
    ongoing_query = {"start": {"$lt": now}, "end": {"$gt": now}}
    upcoming_query = {"start": {"$gt": now}}
    ongoing_events = events_db.find({"$and": [ongoing_query, user_event_query]}).sort("end",
                                                                    pymongo.ASCENDING)
    upcoming_events = events_db.find({"$and": [user_event_query, upcoming_query]}).sort("end", pymongo.ASCENDING)
    ongoing_events = list(ongoing_events)
    upcoming_events = list(upcoming_events)
    for e in ongoing_events:
        e["start"] = prettify_date(e["start"])
        e["end"] = prettify_date(e["end"])

    for e in upcoming_events:
        e["start"] = prettify_date(e["start"])
        e["end"] = prettify_date(e["end"])
    return render_template('index.html', ongoing_events=list(ongoing_events), upcoming_events=list(upcoming_events))
