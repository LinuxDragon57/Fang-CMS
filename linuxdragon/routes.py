from flask import (
    Blueprint, render_template
)

from linuxdragon.Models import Entry

routes_bp = Blueprint('routes', __name__, url_prefix='/')


@routes_bp.route('/')
def index():
    all_posts = Entry.query.all()
    return render_template('routes/index.html', posts=all_posts)


@routes_bp.route('/genres/<genre>')
def genres(genre):
    relevant_posts = Entry.query.filter_by(genre=genre).first()
    return render_template('routes/index.html', posts=relevant_posts)


@routes_bp.route('/about')
def about():
    return render_template('routes/about.html')
