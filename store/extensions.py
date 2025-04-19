"""
Extensions module.
Each extension is initialized in the app factory located in app.py.
"""

from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from store.settings import REDIS_URL

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=[],
)
cache = Cache()
