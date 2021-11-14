from flask import (
    Blueprint, render_template, url_for
)

routes_bp = Blueprint('routes', __name__, url_prefix='/')


@routes_bp.route('/')
def index():
    return render_template(url_for('routes/index.html'))


@routes_bp.route('/<genre>')
def genres():
    pass
