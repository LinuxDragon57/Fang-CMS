#!./venv/bin/python

from datetime import date
import toml
from flask import Flask
from linuxdragon.Models import db
from linuxdragon.commands import (
    initialize_database, create_admin, create_user, initialize_data_directories, mkpath, set_up_totp
)
from linuxdragon.auth import auth_bp
from linuxdragon.cms import cms_bp
from linuxdragon.routes import routes_bp


# Flask Application factory
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_file('config.toml', load=toml.load)

    db.init_app(app)
    app.cli.add_command(initialize_database)
    app.cli.add_command(create_admin)
    app.cli.add_command(create_user)
    app.cli.add_command(initialize_data_directories)
    app.cli.add_command(set_up_totp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(cms_bp)
    app.add_template_global(mkpath, 'mkpath')

    # Allow these template variables to be used application-wide
    @app.context_processor
    def copyleft_msg():
        current_year = date.today().year
        return dict(
            copyleft_msg=f"Copyleft &copy; 2020 &ndash; {current_year} E. L. Jackson"
        )

    return app
