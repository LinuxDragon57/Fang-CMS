#!./venv/bin/python

from secrets import token_urlsafe
import toml
from flask import Flask
from linuxdragon.Models import db
from linuxdragon.commands import (
    initialize_database, create_author, initialize_data_directories, mkpath, set_up_totp, modify_author
)
from linuxdragon.auth import auth_bp
from linuxdragon.cms import cms_bp
from linuxdragon.routes import routes_bp


# Flask Application factory
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_file('config.toml', load=toml.load)
    app.config.from_mapping(SECRET_KEY=token_urlsafe(64))

    db.init_app(app)
    app.cli.add_command(initialize_database)
    app.cli.add_command(create_author)
    app.cli.add_command(initialize_data_directories)
    app.cli.add_command(set_up_totp)
    app.cli.add_command(modify_author)

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(cms_bp)
    app.add_template_global(mkpath, 'mkpath')

    return app
