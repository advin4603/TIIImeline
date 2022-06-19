import bson.errors
from flask import Blueprint, render_template, request, redirect, url_for, abort
from . import login_required, get_email, events_db, groups_db, prettify_date
from bson.objectid import ObjectId
from datetime import datetime

events = Blueprint('events', __name__)


@events.route('/events')
@login_required
def view_events():
    email = get_email()
    group_ids_with_user = (group["_id"] for group in
                           groups_db.find({"$or": [{"emails": email}, {"host": email}]}))
    users_events = events_db.find(
        {"$and": [{"name": {"$regex": "^" + request.args.get("searchQuery", ""), '$options': 'i'}}, {
            "$or": [{"host": email}, *({"groups": g_id} for g_id in group_ids_with_user)]}]})
    users_events = list(users_events)
    for e in users_events:
        e["start"] = prettify_date(e["start"])
        e["end"] = prettify_date(e["end"])
    return render_template('events.html', events=users_events, search_query=request.args.get("searchQuery", ""))


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
        return render_template("event.html", **found_event, found_groups=list(found_groups),
                               is_host=found_event["host"] == get_email(),
                               start_date=datetime.strptime(found_event["start"], "%Y-%m-%dT%H:%M").ctime(),
                               end_date=datetime.strptime(found_event["end"], "%Y-%m-%dT%H:%M").ctime())


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
    edit_this_event = events_db.find_one({"_id": event_id_obj})
    if edit_this_event is None or edit_this_event["host"] != get_email():
        abort(404)
        return

    if request.method == "GET":
        return render_template("edit_event.html", event=edit_this_event, groups=groups_db.find({"host": get_email()}))
    elif request.method == "POST":
        query = {"_id": event_id_obj}
        name = request.form["name"]
        description = request.form["description"]
        start = request.form["start"]
        end = request.form["end"]
        host = get_email()
        group_ids = [ObjectId(id)
                     for id in request.form
                     if id not in {"name", "description", "start", "end", "host"}
                     ]
        new_values = {"name": name, "description": description, "start": start, "end": end, "host": host,
                      "groups": group_ids}
        events_db.update_one(query, {"$set": new_values})
        return redirect(url_for("events.view_event", event_id=edit_this_event["_id"]))


@events.route("/deleteEvent/<string:event_id>")
@login_required
def delete_event(event_id):
    try:
        event_id_obj = ObjectId(event_id)
    except bson.errors.InvalidId:
        abort(404)
        return
    delete_this_event = events_db.find_one({"_id": event_id_obj})
    if delete_this_event is None or delete_this_event["host"] != get_email():
        abort(404)
        return
    events_db.delete_one({"_id": event_id_obj})
    return redirect(url_for("events.view_events"))
