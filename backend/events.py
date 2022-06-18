import bson.errors
from flask import Blueprint, render_template, request, redirect, url_for, abort
from . import login_required, get_email, events_db, groups_db
from bson.objectid import ObjectId

events = Blueprint('events', __name__)


@events.route('/events')
@login_required
def view_events():
    email = get_email()
    group_ids_with_user = [group["_id"] for group in groups_db.find({"$or": [{"emails": email}, {"host": email}]})]
    users_events = events_db.find({"$or": [{"host": email}, *({"groups": g_id} for g_id in group_ids_with_user)]})
    return render_template('events.html', events=users_events)


@events.route("/event/<string:event_id>")
@login_required
def view_event(event_id):
    try:
        event_id_obj = ObjectId(event_id)
    except bson.errors.InvalidId:
        abort(404)
    else:
        event = events_db.find_one({"_id": event_id_obj})
        if event is None:
            abort(404)
        return render_template("event.html", **event)


@events.route('/event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == "GET":
        return render_template('create_event.html')
    elif request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        start = request.form["start"]
        end = request.form["end"]
        host = get_email()
        event_id = events_db.insert_one(
            {"name": name, "description": description, "start": start, "end": end, "host": host, "groups": []})
        return redirect(url_for("events.view_event", event_id=event_id.inserted_id))
