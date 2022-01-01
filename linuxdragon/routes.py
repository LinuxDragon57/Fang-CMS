from flask import (
    Blueprint, render_template
)
from mistune import html as create_html

from linuxdragon.Models import Entry

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
    # Future versions of the program may try to eliminate the need to query the database simply to display a post.
    metadata = Entry.query.filter_by(genre_url=genre, title_url=post_title).first_or_404()
    content = create_html(open(metadata.content_path, 'r').read())
    return render_template('routes/entry_template.html', post_data=metadata, post_content=content)


@routes_bp.route('/about')
def about():
    return render_template('routes/about.html')
