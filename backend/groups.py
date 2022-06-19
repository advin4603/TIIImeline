from flask import Blueprint, render_template, request, abort, redirect, url_for
from . import login_required, get_email, groups_db, events_db
from bson.objectid import ObjectId
import bson.errors

groups = Blueprint('groups', __name__)


@groups.route('/groups')
@login_required
def view_groups():
    email = get_email()
    users_groups = groups_db.find(
        {"$and": [{"name": {"$regex": "^" + request.args.get("searchQuery", ""), '$options': 'i'}},
                  {"$or": [{"host": email}, {"emails": email}]}]})
    return render_template('groups.html', groups=users_groups, search_query=request.args.get("searchQuery", ""))


@groups.route("/group/<string:group_id>")
@login_required
def view_group(group_id):
    try:
        group_id_obj = ObjectId(group_id)
    except bson.errors.InvalidId:
        abort(404)
    else:
        group = groups_db.find_one({"_id": group_id_obj})
        if group is None:
            abort(404)
        return render_template("group.html", **group, is_host=group["host"] == get_email())


@groups.route("/group", methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == "GET":
        return render_template("create_group.html")
    elif request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        emails = request.form["emails"].split()
        host = get_email()
        group_id = groups_db.insert_one({"name": name, "description": description, "emails": emails, "host": host})
        return redirect(url_for("groups.view_group", group_id=group_id.inserted_id))


@groups.route("/editGroup/<string:group_id>", methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    try:
        group_id_obj = ObjectId(group_id)
    except bson.errors.InvalidId:
        abort(404)
        return

    group = groups_db.find_one({"_id": group_id_obj})
    if group is None or group["host"] != get_email():
        abort(404)
        return

    if request.method == "GET":
        return render_template("edit_group.html", group=group, emails="\n".join(group["emails"]))
    elif request.method == "POST":
        query = {"_id": group_id_obj}
        name = request.form["name"]
        description = request.form["description"]
        emails = request.form["emails"].split()
        host = get_email()
        new_values = {"name": name, "description": description, "emails": emails, "host": host}
        groups_db.update_one(query, {"$set": new_values})
        return redirect(url_for("groups.view_group", group_id=group["_id"]))


@groups.route("/deleteGroup/<string:group_id>")
@login_required
def delete_group(group_id):
    try:
        group_id_obj = ObjectId(group_id)
    except bson.errors.InvalidId:
        abort(404)
        return

    group = groups_db.find_one({"_id": group_id_obj})
    if group is None or group["host"] != get_email():
        abort(404)
        return

    events_db.update_many({"groups": group_id_obj}, {"$pull": {"groups": group_id_obj}})
    groups_db.delete_one({"_id": group_id_obj})
    return redirect(url_for("groups.view_groups"))


@groups.route("/leaveGroup/<string:group_id>")
@login_required
def leave_group(group_id):
    try:
        group_id_obj = ObjectId(group_id)
    except bson.errors.InvalidId:
        abort(404)
        return

    group = groups_db.find_one({"_id": group_id_obj})
    if group is None or get_email() not in group["emails"]:
        abort(404)
        return

    groups_db.update_one({"_id": group_id_obj}, {"$pull": {"emails": get_email()}})
    return redirect(url_for("groups.view_groups"))
