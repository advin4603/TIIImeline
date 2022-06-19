from flask import Blueprint, render_template
from . import login_required, events_db, groups_db, get_email
from datetime import datetime
import pymongo

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    now = datetime.now().replace(second=0, microsecond=0).isoformat()[:-3]
    email = get_email()
    group_ids_with_user = (group["_id"] for group in
                           groups_db.find({"$or": [{"emails": email}, {"host": email}]}))
    ongoing_events = events_db.find({"$and": [{"start": {"$lt": now}, "end": {"$gt": now}}, {
        "$or": [{"host": email}, *({"groups": g_id} for g_id in group_ids_with_user)]}]}).sort("end",
                                                                                               pymongo.ASCENDING)
    upcoming_events = events_db.find({"$and": [{"start": {"$gt": now}}, {
        "$or": [{"host": email}, *({"groups": g_id} for g_id in group_ids_with_user)]}]}).sort("end", pymongo.ASCENDING)
    return render_template('index.html', ongoing_events=list(ongoing_events), upcoming_events=list(upcoming_events))
