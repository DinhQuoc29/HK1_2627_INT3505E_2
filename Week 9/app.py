"""User API demonstrating URI path versioning with Flask Blueprints."""

from flask import Flask

from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config.from_mapping(
        TESTING=False,
        V1_SUNSET="Fri, 01 Jan 2027 00:00:00 GMT",
    )
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(v1_bp, url_prefix="/api/v1")
    app.register_blueprint(v2_bp, url_prefix="/api/v2")
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
