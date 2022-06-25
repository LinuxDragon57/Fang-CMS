from flask import (
    Blueprint, render_template, abort
)
from mistune import html as create_html

from Fang.Models import Entry

routes_bp = Blueprint('routes', __name__, url_prefix='/')


@routes_bp.route('/')
def index():
    all_posts = Entry.query.all()
    return render_template('routes/index.html', posts=all_posts)


@routes_bp.route('/genres/<genre>')
def genres(genre):
    relevant_posts = Entry.query.filter_by(genre=genre).all()
    return render_template('routes/index.html', posts=relevant_posts)


@routes_bp.route('/post/<genre>/<post_title>')
def show_post(genre, post_title):
    metadata = Entry.query.filter_by(genre_url=genre, title_url=post_title).first_or_404()
    try:
        content = create_html(open(metadata.content_path, 'r').read())
        return render_template('routes/entry_template.html', post_data=metadata, post_content=content)
    except FileNotFoundError:
        abort(404)
