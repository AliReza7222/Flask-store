from flask import Flask

from store.extensions import (
    bcrypt,
    csrf_protect,
    db,
    debug_toolbar,
    login_manager,
    migrate,
)


def create_app(config_obj="store.settings"):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_obj)
    register_extensions(app)
    return app


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
