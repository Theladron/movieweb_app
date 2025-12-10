from flask import Blueprint, render_template, make_response

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Display the homepage of the application.

    Returns:
        Response: Rendered home page template.
    """
    response = make_response(render_template("home.html"))
    # Prevent premature rendering to avoid FOUC
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
