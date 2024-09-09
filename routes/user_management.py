from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from ..models.user import User

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/users', methods=['GET'])
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('users.html', users=users)
