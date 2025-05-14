"""
Package: service
Package for the application models and service routes.
This module creates and configures the Flask app and sets up the logging
and SQL database.
"""
import sys
import unittest
from flask import Flask
from flask_cors import CORS  # CORS support
from flask_talisman import Talisman
from service import config
from service.common import log_handlers
from service.common import status  # For test status codes

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Activate testing mode
app.testing = app.config.get("TESTING", False)

# Initialize Talisman only if not in test mode
talisman = None
if not app.testing:
    talisman = Talisman(app)

# Enable CORS
CORS(app)  # Adds Access-Control-Allow-Origin: *

# Import routes and models after app creation
from service import routes, models  # noqa: F401, E402
from service.common import error_handlers, cli_commands  # noqa: F401, E402

# Set up logging
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # Initialize DB
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    sys.exit(4)  # Exit with code 4 if DB fails (Gunicorn requirement)

app.logger.info("Service initialized!")

# Environment override for CORS and HTTPS in testing
HTTPS_ENVIRON = {"wsgi.url_scheme": "https"}


# Test class included in same file for simplicity
class TestAccountService(unittest.TestCase):
    """Test suite for the Account Service"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        global talisman
        if talisman:
            talisman.force_https = False  # Ensure HTTPS is disabled during tests

    def setUp(self):
        """Set up before each test"""
        app.testing = True  # Ensure Flask is in test mode
        self.client = app.test_client()

    def test_cors_security(self):
        """It should return a CORS header"""
        response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")