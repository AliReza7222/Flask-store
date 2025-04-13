"""
Extensions module.
Each extension is initialized in the app factory located in app.py.
"""

from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()
jwt = JWTManager()
