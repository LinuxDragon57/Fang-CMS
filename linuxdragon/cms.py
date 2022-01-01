from flask import (
    Blueprint, request, render_template, flash, current_app, session, redirect, url_for, Markup
)

from linuxdragon.commands import mkpath
from linuxdragon.auth import login_required
from linuxdragon.Models import db, Author, Entry

cms_bp = Blueprint('cms', __name__, url_prefix='/cms/')


@cms_bp.route('/')
@login_required
def index():
    all_posts = Entry.query.all()
    return render_template('cms/cms.html', posts=all_posts)


@cms_bp.route('/new', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel':
            return redirect(url_for('cms.index'))
        elif request.form.get('create') == 'Create Post':
            post_title = request.form['title']
            post_desc = request.form['description']
            post_genre = request.form['genres']
            content_path = f"{current_app.config['DATA_DIRECTORY']}/{mkpath(post_genre)}/{mkpath(post_title)}.md"
            author_id = session.get('user_id')
            error = None

            if len(post_title) < 3 or len(post_desc) < 3:
                error = "Title and Description are required to be at least 3 characters long."

            if error is None:
                try:
                    markdown_file = open(content_path, 'x')
                    if Entry.query.filter_by(title=post_title).first() is not None:
                        raise ValueError
                    markdown_file.write(request.form['entry'])
                    markdown_file.close()
                except(OSError, ValueError):
                    flash("Error: A post with that title already exists.")\

                new_entry = Entry(
                    title=post_title,
                    description=post_desc,
                    genre=post_genre,
                    content_path=content_path,
                    author_id=author_id
                )
                db.session.add(new_entry)
                db.session.commit()
                flash(Markup(f"Successfully created post, <em>{post_title}</em>."))
                return redirect(url_for('cms.index'))

            flash(error)

    return render_template('cms/create_post.html')


@cms_bp.route('/update/')
@login_required
def edit(post_id=None):
    if post_id is None:
        current_user_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
        return render_template('cms/cms.html', posts=current_user_posts)


@cms_bp.route('/delete/')
@login_required
def delete(post_id=None):
    if post_id is None:
        current_user_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
        return render_template('cms/cms.html', posts=current_user_posts)
    else:
        pass


@cms_bp.route('/settings', methods=("GET", "POST"))
@login_required
def account_settings():
    pass


@cms_bp.context_processor
def current_user_name():
    user_id = session.get('user_id')
    if user_id is not None:
        user_name = Author.query.get(user_id)
        return dict(current_user_name=user_name.full_name)


@cms_bp.context_processor
def display_admin_functions():
    user_id = session.get('user_id')
    if user_id is not None:
        admin_status: bool = all(db.session.execute(db.select(Author.admin).where(Author.id == user_id)).first())
        return dict(is_admin=admin_status)
