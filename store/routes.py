from flask_smorest import Blueprint


def create_blueprint_api(name: str, url_prefix: str, version: str):
    return Blueprint(name, __name__, url_prefix=f"/api/{version}/{url_prefix}")
