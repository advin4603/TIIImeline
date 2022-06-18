from flask import Blueprint, render_template, request, abort, redirect, url_for
from . import login_required, get_email, groups_db
from bson.objectid import ObjectId
import bson.errors

groups = Blueprint('groups', __name__)


@groups.route('/groups')
@login_required
def view_groups():
    email = get_email()
    users_groups = groups_db.find({"$or": [{"host": email}, {"emails": email}]})
    return render_template('groups.html', groups=users_groups)


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
        return render_template("group.html", **group)


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
