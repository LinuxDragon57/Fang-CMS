from flask import (
    Blueprint, request, render_template, flash, current_app, session, redirect, url_for, g
)

from linuxdragon.auth import login_required
from linuxdragon.Models import db, Author, Entry

cms_bp = Blueprint('cms', __name__, url_prefix='/cms/')


@cms_bp.route('/')
@login_required
def index():
    return render_template('cms/index.html')


@cms_bp.route('/new', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        post_title = request.form['title']
        post_desc = request.form['description']
        post_genre = request.form['genres'].replace(' ', '_').lower()
        content_path = f"{current_app.config['DATA_DIRECTORY']}/{post_genre}/{post_title}.md"
        author_id = session.get('user_id')
        error = None

        if not any([post_title, post_desc, post_genre]):
            error = "Your post is missing required metadata."

        if error is None:
            try:
                markdown_file = open(content_path, 'x')
                markdown_file.write(request.form['entry'])
                markdown_file.close()
            except OSError:
                error = "Error: A post with that title already exists."

        if error is None:
            new_entry = Entry(
                title=post_title,
                description=post_desc,
                genre=post_genre,
                content_path=content_path,
                author_id=author_id
            )
            db.session.add(new_entry)
            db.session.commit()
            flash(f"Successfully created post {post_title}.")
            return redirect(url_for('cms.index'))

        flash(error)
    return render_template('cms/create_post.html')


@cms_bp.route('/update/')
@cms_bp.route('/update/<post>', methods=("GET", "POST"))
@login_required
def edit(post=None):
    pass


@cms_bp.route('/delete/')
@cms_bp.route('/delete/<post>', methods=("GET", "POST"))
@login_required
def delete(post=None):
    pass


@cms_bp.route('/settings', methods=("GET", "POST"))
@login_required
def account_settings():
    pass


@cms_bp.context_processor
def current_user_name():
    user_id = session.get('user_id')
    user_name = db.session.execute(
            db.select(Author.first_name, Author.last_name).where(Author.id == user_id)).first()
    full_name = ' '.join(user_name)
    return dict(current_user_name=full_name)


@cms_bp.context_processor
def display_admin_functions():
    user_id = session.get('user_id')
    if user_id is not None:
        admin_status: bool = all(db.session.execute(db.select(Author.admin).where(Author.id == user_id)).first())
        return dict(is_admin=admin_status)
