from flask import Blueprint, render_template, jsonify
from managers import data_manager as data

user_bp = Blueprint('user', __name__)

@user_bp.route('/users')
def show_users():
    try:
        users = data.get_all_users()

        return render_template('users.html', users=users)
    except Exception as error:
        return jsonify({'error': str(error)}), 404

