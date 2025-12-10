from flask import Blueprint, render_template, make_response

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Shows the homepage of the app"""
    response = make_response(render_template("home.html"))
    # Prevent premature rendering to avoid FOUC
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
