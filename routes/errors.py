from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 Not Found errors.

    Args:
        error: The error object from Flask.

    Returns:
        tuple: Rendered 404 template and status code 404.
    """
    return render_template('404.html'), 404


@errors_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server errors.

    Args:
        error: The error object from Flask.

    Returns:
        tuple: Rendered 500 template and status code 500.
    """
    return render_template('500.html'), 500

