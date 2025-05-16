from flask import Blueprint, render_template, jsonify
from managers import data_manager as data
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("home.html")

