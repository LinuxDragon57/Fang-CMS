from secrets import token_urlsafe
import toml
from flask import Flask, request, abort
from Fang.Models import db
from Fang.commands import (
    initialize_database, expunge_database, create_author, initialize_data_directories, mkpath, set_up_totp, modify_author
)
from Fang.auth import auth_bp
from Fang.cms import cms_bp
from Fang.routes import routes_bp


# Flask Application factory
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_file('config.toml', load=toml.load)
    app.config.from_mapping(SECRET_KEY=token_urlsafe(64), SQLALCHEMY_TRACK_MODIFICATIONS=False)

    db.init_app(app)
    app.cli.add_command(initialize_database)
    app.cli.add_command(expunge_database)
    app.cli.add_command(create_author)
    app.cli.add_command(initialize_data_directories)
    app.cli.add_command(set_up_totp)
    app.cli.add_command(modify_author)

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(cms_bp)
    app.add_template_global(mkpath, 'mkpath')

    @app.before_request
    def prohibit_untrusted_domain():
        acceptable_connection: bool = False
        current_url = request.headers.get('host')
        if current_url == 'localhost' or current_url == '127.0.0.1':
            acceptable_connection = True
        else:
            for trusted in app.config['APP_URL']:
                if current_url == trusted:
                    acceptable_connection = True
                    break

        if not acceptable_connection:
            abort(401)

    return app
