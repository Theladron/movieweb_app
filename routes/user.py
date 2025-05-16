import sqlalchemy
from flask import Blueprint, render_template, jsonify, request
from managers import data_manager as data
from sqlalchemy.exc import SQLAlchemyError

user_bp = Blueprint('user', __name__)

@user_bp.route('/users')
def show_users():
    try:
        users = data.get_all_users()
        message = "No users found." if not users else None
        return render_template('users.html', users=users, message=message)
    except Exception as error:
        return render_template("users.html", users=[], message=f"str( {error})")

@user_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
                               message="User added successfully")

    return render_template("add_user.html")

@user_bp.route('/users/<user_id>', methods=['GET'])
def user_movies(user_id):
    try:

        # Fetch user details
        user_name = data.get_user(user_id)
        if not user_name:
            return render_template('user_movies.html',
                                   user=None, movies=None)

        # Fetch user movies
        movies = data.get_user_movies(user_id)
        if not movies:
            return render_template('user_movies.html',
                                   user=user_name, movies=None)

        return render_template('user_movies.html',
                               user=user_name, movies=movies)

    except SQLAlchemyError as error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(error))
    except Exception as error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(error))

@user_bp.route('/users/<int:user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    try:
        user = data.get_user(user_id)
    except sqlalchemy.exc.NoResultFound:
        return render_template('update_user.html',
                               user=None, user_id=user_id, message="User not found.")

    if request.method == "POST":
        name = request.form.get("name").strip()

        # Check if the name is provided
        if not name:
            return render_template("update_user.html",
                                   message="Name is required.")

        # Check if the name is valid
        if len(name) < 2:
            return render_template("update_user.html",
                                   message=f"Name must be at least 2 characters long.")
        if len(name) > 20:
            return render_template("update_user.html",
                                   message=f"Name must be at most 20 characters long.")

        # Check if the name already exists
        try:
            existing_user = data.get_user_by_name(name)
            if existing_user:
                return render_template("update_user.html",
                                       message=f"The user '{name}' already exists.")
        except ValueError as error:
            return render_template("update_user.html",
                                   message=str(error))
        except SQLAlchemyError as error:
            return render_template("update_user.html",
                                   message=str(error))
        except Exception as error:
            return render_template("update_user.html",
                                   message=str(error))

        return render_template("update_user.html",
                               message="user updated successfully")

    return render_template('update_user.html', user=user, user_id=user_id)

@user_bp.route('/users/<user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    """Delete a user from the system."""
    try:
        user_name = data.delete_user(user_id)
        if not user_name:
            return render_template('users.html',
                                   message=f"User with ID {user_id} not found.")

        return render_template('users.html',
                               message=f"User '{user_name}' deleted successfully!")
    except ValueError as error:
        return render_template('users.html', message=str(error))
    except Exception as error:
        return render_template('users.html',
                               message=f"An unexpected error occurred: {str(error)}")