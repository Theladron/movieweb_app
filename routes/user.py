import sqlalchemy
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError


def _validate_username(name: str) -> str | None:
    """Validate username and return an error message or None if valid."""
    if not name:
        return "Name is required."
    if len(name) < 2:
        return "Name must be at least 2 characters long."
    if len(name) > 20:
        return "Name must be at most 20 characters long."
    return None

from datamanager import data_manager as data

user_bp = Blueprint('user', __name__)


@user_bp.route('/users')
def show_users():
    """Display all users in the system.

    Returns:
        Response: Rendered users template with list of users.
    """
    try:
        users = data.get_all_users()
        message = "No users found." if not users else None
        return render_template('users.html', users=users, message=message)
    except Exception as unexpected_error:
        return render_template("users.html", users=[], message=str(unexpected_error))


@user_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user to the system.

    GET: Display the add user form.
    POST: Process the form submission and create a new user.

    Returns:
        Response: Redirect to users list on success, or form with error message.
    """
    if request.method == "POST":
        name = request.form.get('name', '').strip()

        validation_error = _validate_username(name)
        if validation_error:
            return render_template("add_user.html", message=validation_error)
        # Check if the name already exists
        try:
            existing_user = data.get_user_by_name(name)
            if existing_user:
                return render_template(
                    "add_user.html",
                    message=f"The user '{name}' already exists."
                )

            data.add_user(name)

        except ValueError as value_error:
            return render_template("add_user.html", message=str(value_error))
        except SQLAlchemyError as db_error:
            return render_template("add_user.html", message=f"Database error: {str(db_error)}")
        except Exception as unexpected_error:
            return render_template("add_user.html", message=f"Error: {str(unexpected_error)}")

        return redirect(url_for('user.show_users'))

    return render_template("add_user.html")


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """Display all movies associated with a specific user.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        Response: Rendered user_movies template with user's movie collection.
    """
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

    except ValueError as value_error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(value_error))
    except SQLAlchemyError as db_error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(db_error))
    except Exception as unexpected_error:
        return render_template("user_movies.html",
                               user=None, movies=None, message=str(unexpected_error))


@user_bp.route('/users/<int:user_id>/update_user', methods=['GET', 'POST'])
def update_user(user_id):
    """Update a user's name in the system.

    GET: Display the update user form.
    POST: Process the form submission and update the user's name.

    Args:
        user_id: The unique identifier of the user to update.

    Returns:
        Response: Redirect to users list on success, or form with error message.
    """
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        # Get current user first (needed for template)
        try:
            current_user = data.get_user(user_id)
        except ValueError as value_error:
            return render_template("update_user.html",
                                   user=None, user_id=user_id, message=str(value_error))

        validation_error = _validate_username(name)
        if validation_error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id,
                                   message=validation_error)

        # Check if the name already exists (but only if it's a different user)
        if name != current_user.name:
            try:
                existing_user = data.get_user_by_name(name)
                if existing_user and existing_user.id != user_id:
                    return render_template(
                        "update_user.html",
                        user=current_user,
                        user_id=user_id,
                        message=f"The user '{name}' already exists."
                    )
            except ValueError:
                # User with that name doesn't exist, which is fine
                pass
            except SQLAlchemyError as db_error:
                return render_template("update_user.html",
                                       user=current_user, user_id=user_id, message=str(db_error))
            except Exception as unexpected_error:
                return render_template("update_user.html",
                                       user=current_user, user_id=user_id, message=str(unexpected_error))

        try:
            # Update user details
            data.update_user(user_id=user_id, user_name=name)
        except ValueError as value_error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(value_error))
        except SQLAlchemyError as db_error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(db_error))
        except Exception as unexpected_error:
            return render_template("update_user.html",
                                   user=current_user, user_id=user_id, message=str(unexpected_error))

        # Redirect to users list after successful update
        return redirect(url_for('user.show_users'))

    try:
        user = data.get_user(user_id)
    except ValueError:
        return render_template('update_user.html',
                               user=None, user_id=user_id, message="User not found.")
    except Exception as unexpected_error:
        return render_template('update_user.html',
                               user=None, user_id=user_id, message=str(unexpected_error))
    return render_template('update_user.html', user=user, user_id=user_id)


@user_bp.route('/users/<int:user_id>/delete_user', methods=['GET'])
def delete_user(user_id):
    """Delete a user from the system.

    Args:
        user_id: The unique identifier of the user to delete.

    Returns:
        Response: Redirect to users list page.
    """
    try:
        user_name = data.delete_user(user_id)
        return redirect(url_for('user.show_users'))
    except ValueError:
        return redirect(url_for('user.show_users'))
    except Exception:
        return redirect(url_for('user.show_users'))
