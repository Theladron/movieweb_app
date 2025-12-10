import sqlalchemy
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

from datamanager import data_manager as data

user_bp = Blueprint('user', __name__)


@user_bp.route('/users')
def show_users():
    """Shows all users in the system, handles exceptions"""
    try:
        users = data.get_all_users()
        message = "No users found." if not users else None
        return render_template('users.html', users=users, message=message)
    except Exception as error:
        return render_template("users.html", users=[], message=f"str( {error})")


@user_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Adds a user to the system, handles exceptions"""
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
            return render_template("add_user.html", message=str(error))
        except SQLAlchemyError as error:
            return render_template("add_user.html", message=f"Database error: {str(error)}")
        except Exception as error:
            return render_template("add_user.html", message=f"Error: {str(error)}")

        return redirect(url_for('user.show_users'))

    return render_template("add_user.html")


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """Shows the movies associated with a user, handles exceptions"""
    try:
        # Fetch user details
        user = data.get_user(user_id)

        # Fetch user movies
        movies = data.get_user_movies(user_id)
        if not movies:
            return render_template('user_movies.html',
                                   user=user, movies=None)

        return render_template('user_movies.html',
                               user=user, movies=movies)

    except ValueError as error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(error))
    except SQLAlchemyError as error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(error))
    except Exception as error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(error))


@user_bp.route('/users/<int:user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    """Updates a user's name in the system, handles exceptions"""
    if request.method == "POST":
        name = request.form.get("name").strip()

        # Get current user first (needed for template)
        try:
            current_user = data.get_user(user_id)
        except ValueError as error:
            return render_template("update_user.html",
                                   user=None, user_id=user_id, message=str(error))

        # Check if the name is provided
        if not name:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message="Name is required.")

        # Check if the name is valid
        if len(name) < 2:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id,
                                   message=f"Name must be at least 2 characters long.")
        if len(name) > 20:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id,
                                   message=f"Name must be at most 20 characters long.")

        # Check if the name already exists (but only if it's a different user)
        if name != current_user.name:
            try:
                existing_user = data.get_user_by_name(name)
                if existing_user and existing_user.id != user_id:
                    return render_template("update_user.html",
                                           user=current_user, user_id=user_id,
                                           message=f"The user '{name}' already exists.")
            except ValueError:
                # User with that name doesn't exist, which is fine
                pass
            except SQLAlchemyError as error:
                return render_template("update_user.html",
                                       user=current_user, user_id=user_id, message=str(error))
            except Exception as error:
                return render_template("update_user.html",
                                       user=current_user, user_id=user_id, message=str(error))

        try:
            # Update user details
            data.update_user(user_id=user_id, user_name=name)
        except ValueError as error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(error))
        except SQLAlchemyError as error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(error))
        except Exception as error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(error))

        # Redirect to users list after successful update
        return redirect(url_for('user.show_users'))

    try:
        user = data.get_user(user_id)
    except ValueError:
        return render_template('update_user.html',
                               user=None, user_id=user_id, message="User not found.")
    except Exception as error:
        return render_template('update_user.html',
                               user=None, user_id=user_id, message=str(error))
    return render_template('update_user.html', user=user, user_id=user_id)


@user_bp.route('/users/<int:user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    """Delete a user from the system, handles exceptions."""
    try:
        user_name = data.delete_user(user_id)
        return redirect(url_for('user.show_users'))
    except ValueError as error:
        return redirect(url_for('user.show_users'))
    except Exception as error:
        return redirect(url_for('user.show_users'))
