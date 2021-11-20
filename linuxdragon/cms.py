from mistune import html as create_html
from datetime import date
from flask import (
    Blueprint, request, render_template, flash, current_app, session
)

from linuxdragon.auth import login_required
from linuxdragon.Models import db, Author, Entry

cms_bp = Blueprint('cms', __name__, url_prefix='/cms')


@cms_bp.route('/')
@login_required
def index():
    return render_template('cms/index.html')


@cms_bp.route('/new', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        post_data = {
            'post_title': request.form['title'],
            'post_desc': request.form['description'],
            'genres': request.form['genres'],
            'date_created': date.today(),
            'post_content': create_html(request.form['entry'])
        }
        content_path = f"{current_app.config['DATA_DIRECTORY']}/{post_data['genres']}/{post_data['post_title']}.html"
        author_id = session.get('user_id')
        error = None

        try:
            html_file = open(content_path, 'x')
            html_file.write(render_template('cms/entry_template.html', post_data=post_data))
            html_file.close()
        except OSError:
            error = "Error: A post with that title already exists."

        if error is None:
            new_entry = Entry(
                title=post_data['post_title'],
                description=post_data['post_desc'],
                genre=post_data['genres'],
                content_path=content_path,
                date_created=post_data['date_created'],
                author_id=author_id
            )
            db.session.add(new_entry)
            db.session.commit()

        flash(error)
    return render_template('cms/create_post.html')


@cms_bp.context_processor
def current_user_name():
    user_id = session.get('user_id')
    user_name = db.session.execute(
            db.select(Author.first_name, Author.last_name).where(Author.id == user_id)).first()
    full_name = ' '.join(user_name)
    return dict(current_user_name=full_name)
