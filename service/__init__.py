"""
Package: service
Package for the application models and service routes.
This module creates and configures the Flask app and sets up the logging
and SQL database.
"""
import sys
import unittest
from flask import Flask
from flask_talisman import Talisman
from service import config
from service.common import log_handlers

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Initialize Talisman for security headers
talisman = Talisman(app)

# Import the routes after the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # Make our database tables
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # Gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")


class TestAccountService(unittest.TestCase):
    """Test suite for the Account Service"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        talisman.force_https = False  # Desativa HTTPS forçado nos testes
