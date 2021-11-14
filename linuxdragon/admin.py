import mistune
from flask import (
    Blueprint, request, render_template, url_for, current_app, session
)

from linuxdragon.auth import login_required

cms_bp = Blueprint('console', __name__, url_prefix='/admin')


@cms_bp.route('/')
@login_required
def cms():
    return render_template(url_for('admin/index.html'))


@cms_bp.route('/new')
@login_required
def create():
    if request.method == 'POST':
        post_title = request.form['title']
        genre = request.form['genre']
        content_path = current_app.config[f'DATA_DIRECTORY'] + f'/{genre}/{post_title}.html'
        author_id = session.get('user_id')
        error = None

        try:
            html_file = open(content_path, 'x')
        except OSError:
            error = "Error: Post with title already exists."
