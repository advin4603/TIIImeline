import bson.errors
from flask import Blueprint, render_template, request, redirect, url_for, abort
from . import login_required, get_email, events_db, groups_db
from bson.objectid import ObjectId

events = Blueprint('events', __name__)


@events.route('/events')
@login_required
def view_events():
    email = get_email()
    group_ids_with_user = (group["_id"] for group in groups_db.find({"$or": [{"emails": email}, {"host": email}]}))
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
        found_event = events_db.find_one({"_id": event_id_obj})
        if found_event is None:
            abort(404)

        found_groups = groups_db.find({"_id": {"$in": found_event["groups"]}})
        return render_template("event.html", **found_event, found_groups=list(found_groups))


@events.route('/event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == "GET":
        return render_template('create_event.html', groups=groups_db.find({"host": get_email()}))
    elif request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        start = request.form["start"]
        end = request.form["end"]
        host = get_email()
        group_ids = [ObjectId(id)
                     for id in request.form
                     if id not in {"name", "description", "start", "end", "host"}
                     ]
        event_id = events_db.insert_one(
            {"name": name, "description": description, "start": start, "end": end, "host": host, "groups": group_ids})
        return redirect(url_for("events.view_event", event_id=event_id.inserted_id))


@events.route('/editEvent/<string:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    try:
        event_id_obj = ObjectId(event_id)
    except bson.errors.InvalidId:
        abort(404)
        return
    edit_event = events_db.find_one({"_id": event_id_obj})
    if edit_event is None:
        abort(404)
        return

    if request.method == "GET":
        return render_template("edit_event.html", event=edit_event, groups=groups_db.find({"host": get_email()}))
