from flask import Flask
import toml

from linuxdragon.Models import db
from linuxdragon.commands import (
    create_database, create_admin
)
from linuxdragon.auth import auth_bp
from linuxdragon.routes import routes_bp
from linuxdragon.admin import cms_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_file('config.toml', load=toml.load)

    db.init_app(app)
    app.cli.add_command(create_database)
    app.cli.add_command(create_admin)

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(cms_bp)

    return app
