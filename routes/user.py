from flask import Blueprint, render_template, jsonify, request
from managers import data_manager as data
from sqlalchemy.exc import SQLAlchemyError

user_bp = Blueprint('user', __name__)

@user_bp.route('/users')
def show_users():
    try:
        users = data.get_all_users()

        return render_template('users.html', users=users)
    except Exception as error:
        return jsonify({'error': str(error)}), 404

@user_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user to the system by submitting a form with their name."""
    if request.method == "POST":
        name = request.form.get('name').strip()

        # Check if the name is provided
        if not name:
            return render_template("add_user.html",
                                   message="Name is required.")

        # Check if the name is valid
        if len(name) < 2:
            return render_template("add_user.html",
                                   message=f"Name must be at least 2 characters long.")
        if len(name) > 20:
            return render_template("add_user.html",
                                   message=f"Name must be at most 20 characters long.")
        # Check if the name already exists
        try:
            existing_user = data.get_user_by_name(name)
            if existing_user:
                return render_template("add_user.html",
                                       message=f"The user '{name}' already exists.")

            data.add_user(name)

        except ValueError as error:
            return jsonify({"message": str(error)}), 400
        except SQLAlchemyError as error:
            return jsonify({"message": str(error)}), 500
        except Exception as error:
            return jsonify({"message": str(error)}), 500

        return render_template("add_user.html",
                               message="Book added successfully")

    return render_template("add_user.html")