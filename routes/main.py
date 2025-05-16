from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Shows the homepage of the app"""
    return render_template("home.html")
