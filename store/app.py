from flask import Flask

from store import commands, order, product, user
from store.extensions import (
    bcrypt,
    db,
    debug_toolbar,
    jwt,
    migrate,
    swagger,
)
from store.routes import api


def create_app(config_obj="store.settings"):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_obj)
    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    swagger.init_app(app)


def register_commands(app):
    app.cli.add_command(commands.create_admin_user)


def register_blueprints(app):
    # Register API Blueprint
    api.register_blueprint(user.apis.blueprint)
    api.register_blueprint(product.apis.blueprint)
    api.register_blueprint(order.apis.blueprint)
    app.register_blueprint(api)
