from flask import (
    Blueprint, render_template, url_for
)

routes_bp = Blueprint('routes', __name__, url_prefix='/')


def sort_posts():
    pass


@routes_bp.route('/')
def index():
    return render_template('routes/index.html')


@routes_bp.route('genres/<genre>')
def genres():
    pass


@routes_bp.route('/about')
def about():
    return render_template('routes/about.html')
