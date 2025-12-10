"""
Selenium fixtures for frontend tests.
"""
import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app
from extensions import db


@pytest.fixture(scope='module')
def test_app():
    """Create Flask application instance for testing."""
    import os
    import tempfile
    
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Set DATABASE_URL before creating app - use temp file path directly
    old_db_url = os.environ.get('DATABASE_URL', None)
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'  # Set test database URI
    
    try:
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost:5000'
        
        # Ensure models are imported and create all tables
        from datamanager.data_models import User, Movie, UserMovies
        with app.app_context():
            db.drop_all()
            db.create_all()
        
        yield app
        
        with app.app_context():
            db.session.remove()
            db.drop_all()
    finally:
        # Restore original DATABASE_URL
        if old_db_url is not None:
            os.environ['DATABASE_URL'] = old_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(scope='function')
def live_server(test_app):
    """Start a live Flask test server in a separate thread."""
    import socket
    
    # Find an available port
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    port = find_free_port()
    
    def run_server():
        test_app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    max_attempts = 10
    for _ in range(max_attempts):
        try:
            import urllib.request
            urllib.request.urlopen(f'http://127.0.0.1:{port}').read()
            break
        except:
            time.sleep(0.5)
    else:
        pytest.skip(f"Could not start test server on port {port}")
    
    yield port
    
    # Server thread is daemon, will be killed when test ends


@pytest.fixture(scope='function')
def driver():
    """Create a Selenium WebDriver instance."""
    import os
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    
    # For Docker: use system chromium/chromedriver instead of webdriver-manager
    if os.path.exists('/usr/bin/chromedriver'):
        # Use system chromedriver in Docker
        chrome_options.binary_location = '/usr/bin/chromium'
        service = Service('/usr/bin/chromedriver')
    else:
        # Fallback to webdriver-manager for local development
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    yield driver
    
    driver.quit()


@pytest.fixture
def base_url(live_server):
    """Base URL for the test server."""
    return f'http://127.0.0.1:{live_server}'

