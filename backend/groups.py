from flask import Blueprint, render_template
from . import login_required

groups = Blueprint('groups', __name__)


@groups.route('/groups')
@login_required
def view_groups():
    return render_template('groups.html')


